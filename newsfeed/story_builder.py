from __future__ import annotations

"""Assemble stories from crawled articles and analytics."""

from typing import List

from .models import Story, Reference
from .crawler import GoogleNewsCrawler, CuriousCrawler, related_links
from .analytics import Analyzer


class StoryBuilder:
    """High level orchestration for building ``Story`` objects."""

    def __init__(self, crawler=None, analyzer=None) -> None:
        self.crawler = crawler or GoogleNewsCrawler()
        self.analyzer = analyzer or Analyzer()

    def build(self, limit: int = 10, sort: str = "latest", include_twitter: bool = True) -> List[Story]:
        limit = max(1, min(limit, 100))
        articles = self.crawler.fetch(limit)
        curious = CuriousCrawler().fetch(min(5, limit))
        articles.extend(curious)
        stories: List[Story] = []
        seen_titles = set()
        for art in articles:
            key = art.title.strip().lower()
            if key in seen_titles:
                continue
            seen_titles.add(key)
            category, relevance, bias, trending = self.analyzer.analyze(art)
            summary = self.analyzer.summarize(art)
            perspectives = self.analyzer.generate_perspectives(art)
            stats = self.analyzer.extract_stats(art)
            references = related_links(art.title)
            stories.append(
                Story(
                    title=art.title,
                    summary=summary,
                    link=art.link,
                    source=art.source,
                    category=category,
                    published=art.published,
                    relevance=relevance,
                    bias=bias,
                    trending=trending,
                    references=references,
                    perspectives=perspectives,
                    stats=stats,
                )
            )

        if include_twitter and len(stories) < limit:
            try:
                from .twitter_feed import TwitterTrendsFetcher

                t_fetcher = TwitterTrendsFetcher()
                stories.extend(t_fetcher.fetch(limit - len(stories)))
            except Exception:
                pass

        # Deduplicate again after blending Twitter stories
        unique = {}
        for s in stories:
            key = s.title.strip().lower()
            if key not in unique:
                unique[key] = s
        stories = list(unique.values())

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
