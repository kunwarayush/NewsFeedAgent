from __future__ import annotations

"""Fetch trending tweets from high-impact accounts."""

from datetime import datetime, timezone
from typing import List
import os

try:
    import tweepy  # type: ignore
except Exception:  # pragma: no cover - tweepy optional
    tweepy = None

from .models import Story, Perspective, Reference, Score
from .analytics import categorize


class TwitterTrendsFetcher:
    """Retrieve tweets from influential accounts as news stories."""

    HIGH_IMPACT_ACCOUNTS = [
        "PMOIndia",
        "narendramodi",
        "ndtv",
        "timesofindia",
    ]

    def __init__(self, bearer_token: str | None = None) -> None:
        self.bearer_token = bearer_token or os.getenv("TWITTER_BEARER_TOKEN")
        self.client = None
        if tweepy and self.bearer_token:
            try:
                self.client = tweepy.Client(bearer_token=self.bearer_token, wait_on_rate_limit=True)
            except Exception:
                self.client = None

    def fetch(self, limit: int = 5) -> List[Story]:
        """Fetch recent tweets as ``Story`` objects.

        Returns an empty list if credentials are missing or the API call fails.
        """

        if not self.client:
            return []

        tweets = []
        for username in self.HIGH_IMPACT_ACCOUNTS:
            try:
                user = self.client.get_user(username=username)
                user_id = user.data.id if user and user.data else None
                if not user_id:
                    continue
                resp = self.client.get_users_tweets(user_id, max_results=5)
                if resp.data:
                    for t in resp.data:
                        tweets.append((username, t))
            except Exception:
                continue
            if len(tweets) >= limit:
                break

        stories: List[Story] = []
        for username, tweet in tweets[:limit]:
            title = tweet.text
            link = f"https://twitter.com/{username}/status/{tweet.id}"
            category = categorize(title, "")
            perspectives = [Perspective("tweet", title)]
            references = [Reference(title, link) for _ in range(4)]
            stories.append(
                Story(
                    title=title,
                    summary=title,
                    link=link,
                    source=username,
                    category=category,
                    published=datetime.now(timezone.utc),
                    relevance=Score(0.5, "Derived from Twitter feed"),
                    bias=Score(0.5, "Bias scoring not available"),
                    trending=Score(1.0, "Trending on Twitter"),
                    perspectives=perspectives,
                    references=references,
                )
            )
        return stories
