from __future__ import annotations

"""Fetching and assembling news stories with basic scoring."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List

import feedparser


def _categorize(title: str, summary: str) -> str:
    """Roughly classify a story into broad categories.

    This is a heuristic placeholder until more advanced NLP models are added.
    """

    text = f"{title} {summary}".lower()
    politics_kw = ["election", "minister", "parliament", "government", "policy"]
    tech_kw = ["tech", "science", "ai", "technology", "health", "medical"]

    if any(k in text for k in politics_kw):
        return "Politics"
    if any(k in text for k in tech_kw):
        return "Tech/Visual"
    return "General"


@dataclass
class Reference:
    title: str
    link: str


@dataclass
class Perspective:
    viewpoint: str
    detail: str


@dataclass
class Story:
    """Structured representation of a news story."""

    title: str
    summary: str
    link: str
    category: str
    relevance_score: float
    bias_score: float
    trending_score: float
    perspectives: List[Perspective]
    references: List[Reference]


def fetch_top_stories(limit: int = 10) -> List[Story]:
    """Fetch top stories from Google News RSS feed.

    Args:
        limit: Number of stories to return (1-100).

    Returns:
        List of Story objects limited by ``limit``.
    """

    feed_url = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
    data = feedparser.parse(feed_url)
    limit = max(1, min(limit, 100))
    entries = data.entries[:limit]
    stories: List[Story] = []

    for idx, entry in enumerate(entries):
        title = entry.get("title", "")
        link = entry.get("link", "")
        summary = entry.get("summary", "")
        published = entry.get("published_parsed")

        if published:
            published_dt = datetime(*published[:6], tzinfo=timezone.utc)
            hours_old = (datetime.now(timezone.utc) - published_dt).total_seconds() / 3600
            trending_score = max(0.0, 1 - hours_old / 24)
        else:
            trending_score = 0.5

        relevance_score = 1.0 if "India" in title else 0.5
        bias_score = 0.5  # Placeholder until real bias detection is implemented
        category = _categorize(title, summary)

        perspectives = [
            Perspective("left", f"Left perspective on {title}"),
            Perspective("center", f"Centrist view on {title}"),
            Perspective("right", f"Right perspective on {title}"),
        ]

        ref_entries = data.entries[idx + 1 : idx + 5]
        references = [
            Reference(e.get("title", ""), e.get("link", ""))
            for e in ref_entries
        ]
        while len(references) < 4:
            references.append(Reference(title, link))

        stories.append(
            Story(
                title=title,
                summary=summary,
                link=link,
                category=category,
                relevance_score=relevance_score,
                bias_score=bias_score,
                trending_score=trending_score,
                perspectives=perspectives,
                references=references,
            )
        )

    return stories
