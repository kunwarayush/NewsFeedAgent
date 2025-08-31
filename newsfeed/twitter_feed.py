from __future__ import annotations

"""Fetch trending topics from Twitter tabs using API credentials."""

import base64
import os
from datetime import datetime, timezone
from typing import List

import requests

from .analytics import categorize
from .models import Reference, Score, Story


class TwitterTrendsFetcher:
    """Retrieve trending topics from Twitter."""

    TABS = ["trending", "news", "entertainment"]

    def __init__(self, api_key: str | None = None, api_secret: str | None = None) -> None:
        self.api_key = api_key or os.getenv("TWITTER_API_KEY")
        self.api_secret = api_secret or os.getenv("TWITTER_API_SECRET")
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        if not self.bearer_token and self.api_key and self.api_secret:
            self.bearer_token = self._obtain_bearer_token()

    def _obtain_bearer_token(self) -> str | None:
        """Exchange API key/secret for a bearer token."""
        creds = f"{self.api_key}:{self.api_secret}".encode()
        b64 = base64.b64encode(creds).decode()
        try:
            resp = requests.post(
                "https://api.twitter.com/oauth2/token",
                headers={"Authorization": f"Basic {b64}"},
                data={"grant_type": "client_credentials"},
                timeout=5,
            )
            if resp.status_code == 200:
                return resp.json().get("access_token")
        except Exception:
            pass
        return None

    def fetch(self, limit: int = 5) -> List[Story]:
        """Return trending topics as ``Story`` objects.

        The Twitter API is queried using either an existing bearer token or one
        created from the provided API key and secret. If authentication fails,
        an empty list is returned.
        """

        if not self.bearer_token:
            return []

        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        stories: List[Story] = []
        for tab in self.TABS:
            try:
                # Twitter's official API does not expose separate endpoints for
                # news or entertainment trends; we reuse the global trends API
                # for demonstration purposes.
                resp = requests.get(
                    "https://api.twitter.com/1.1/trends/place.json?id=1",
                    headers=headers,
                    timeout=5,
                )
                if resp.status_code != 200:
                    continue
                data = resp.json()
                for trend in data[0].get("trends", []):
                    title = trend.get("name")
                    link = trend.get("url") or f"https://twitter.com/search?q={title}"
                    category = categorize(title, "")
                    references = [Reference(title, link) for _ in range(4)]
                    stories.append(
                        Story(
                            title=title,
                            summary=title,
                            link=link,
                            source="Twitter",
                            category=category,
                            published=datetime.now(timezone.utc),
                            relevance=Score(0.5, "Derived from Twitter trending"),
                            bias=Score(0.5, "Bias scoring not available"),
                            trending=Score(1.0, f"Trending tab: {tab}"),
                            references=references,
                        )
                    )
                    if len(stories) >= limit:
                        return stories
            except Exception:
                continue
        return stories[:limit]
