from __future__ import annotations

"""Assemble stories from crawled articles and analytics."""

from datetime import datetime, timezone
from typing import List

from .models import Story, Perspective, Reference
from .crawler import GoogleNewsCrawler, related_links
from .analytics import Analyzer


class StoryBuilder:
    """High level orchestration for building ``Story`` objects."""

    def __init__(self, crawler=None, analyzer=None) -> None:
        self.crawler = crawler or GoogleNewsCrawler()
        self.analyzer = analyzer or Analyzer()

    def build(self, limit: int = 10, sort: str = "latest", include_twitter: bool = True) -> List[Story]:
        limit = max(1, min(limit, 100))
        google_limit = limit if not include_twitter else max(1, limit // 2)
        articles = self.crawler.fetch(google_limit)
        stories: List[Story] = []
        for art in articles:
            category, relevance, bias, trending = self.analyzer.analyze(art)
            perspectives = [
                Perspective("left", f"Left perspective on {art.title}"),
                Perspective("center", f"Centrist view on {art.title}"),
                Perspective("right", f"Right perspective on {art.title}"),
            ]
            references = related_links(art.title)
            stories.append(
                Story(
                    title=art.title,
                    summary=art.summary,
                    link=art.link,
                    source=art.source,
                    category=category,
                    published=art.published,
                    relevance=relevance,
                    bias=bias,
                    trending=trending,
                    perspectives=perspectives,
                    references=references,
                )
            )

        if include_twitter:
            try:
                from .twitter_feed import TwitterTrendsFetcher

                t_fetcher = TwitterTrendsFetcher()
                stories.extend(t_fetcher.fetch(limit - len(stories)))
            except Exception:
                pass

        stories = self._sort(stories, sort)
        return stories[:limit]

    def _sort(self, stories: List[Story], sort: str) -> List[Story]:
        sort = (sort or "latest").lower()
        reverse = True
        if sort == "trending":
            key = lambda s: s.trending_score
        elif sort == "top":
            key = lambda s: s.relevance_score
        elif sort == "oldest":
            key = lambda s: s.published
            reverse = False
        else:  # latest
            key = lambda s: s.published
        return sorted(stories, key=key, reverse=reverse)
