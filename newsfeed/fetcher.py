from __future__ import annotations

"""Fetching and assembling news stories with basic scoring."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List

from urllib.parse import quote_plus
import feedparser
import re
from html import unescape
import requests

LI_RE = re.compile(r"<li>(.*?)</li>", re.DOTALL)


def _clean_summary(html_snippet: str) -> str:
    """Extract plain text from a Google News summary block."""

    match = LI_RE.search(html_snippet or "")
    snippet = match.group(1) if match else html_snippet
    text = re.sub(r"<[^>]+>", "", snippet)
    return unescape(text).strip()


def _split_title_source(title: str) -> tuple[str, str]:
    """Split combined title into title and source."""

    if " - " in title:
        return title.rsplit(" - ", 1)
    return title, ""


def _resolve_link(link: str) -> str:
    """Follow Google News redirect to get the original article URL."""

    if "news.google.com" not in link:
        return link
    try:
        resp = requests.get(link, timeout=5, allow_redirects=True)
        return resp.url
    except Exception:
        return link


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
    source: str
    category: str
    relevance_score: float
    bias_score: float
    trending_score: float
    perspectives: List[Perspective]
    references: List[Reference]


def _related_links(title: str) -> List[Reference]:
    """Fetch up to four related links for the given story title."""

    search_url = (
        "https://news.google.com/rss/search?q="
        f"{quote_plus(title)}&hl=en-IN&gl=IN&ceid=IN:en"
    )
    data = feedparser.parse(search_url)
    refs: List[Reference] = []
    for e in data.entries[:4]:
        r_title, _ = _split_title_source(e.get("title", ""))
        r_link = _resolve_link(e.get("link", ""))
        refs.append(Reference(r_title, r_link))
    while len(refs) < 4:
        refs.append(Reference(title, ""))
    return refs


def fetch_top_stories(limit: int = 10, include_twitter: bool = True) -> List[Story]:
    """Fetch top stories from Google News RSS feed and Twitter trends.

    Args:
        limit: Number of stories to return (1-100).

    Returns:
        List of Story objects limited by ``limit``.
    """

    feed_url = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
    data = feedparser.parse(feed_url)
    limit = max(1, min(limit, 100))
    google_limit = limit if not include_twitter else max(1, limit // 2)
    entries = data.entries[:google_limit]
    stories: List[Story] = []
    seen_titles = set()

    for entry in entries:
        raw_title = entry.get("title", "")
        title, source = _split_title_source(raw_title)
        if title in seen_titles:
            continue
        seen_titles.add(title)
        link = _resolve_link(entry.get("link", ""))
        summary = _clean_summary(entry.get("summary", ""))
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

        references = _related_links(title)

        stories.append(
            Story(
                title=title,
                summary=summary,
                link=link,
                source=source,
                category=category,
                relevance_score=relevance_score,
                bias_score=bias_score,
                trending_score=trending_score,
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

    return stories
