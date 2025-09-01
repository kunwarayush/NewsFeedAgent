from __future__ import annotations

"""Crawler modules responsible for gathering raw articles."""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from html import unescape
from typing import List
from urllib.parse import quote_plus
import re
import requests
import feedparser

from .models import Article, Reference

LI_RE = re.compile(r"<li>(.*?)</li>", re.DOTALL)


def _clean_summary(html_snippet: str) -> str:
    match = LI_RE.search(html_snippet or "")
    snippet = match.group(1) if match else html_snippet
    text = re.sub(r"<[^>]+>", "", snippet)
    return unescape(text).strip()


def _split_title_source(title: str) -> tuple[str, str]:
    if " - " in title:
        return title.rsplit(" - ", 1)
    return title, ""


def _resolve_link(link: str) -> str:
    if "news.google.com" not in link:
        return link
    try:
        resp = requests.get(link, timeout=5, allow_redirects=True)
        return resp.url
    except Exception:
        return link


def related_links(title: str) -> List[Reference]:
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


class BaseCrawler(ABC):
    """Abstract crawler interface."""

    @abstractmethod
    def fetch(self, limit: int) -> List[Article]:  # pragma: no cover - interface
        raise NotImplementedError


class GoogleNewsCrawler(BaseCrawler):
    """Crawler pulling articles from Google News RSS feed."""

    FEED_URL = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"

    def fetch(self, limit: int) -> List[Article]:
        data = feedparser.parse(self.FEED_URL)
        entries = data.entries[:limit]
        articles: List[Article] = []
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
            else:
                published_dt = datetime.now(timezone.utc)
            articles.append(
                Article(
                    title=title,
                    summary=summary,
                    link=link,
                    source=source,
                    published=published_dt,
                )
            )
        return articles


class CuriousCrawler(BaseCrawler):
    """Crawler for niche sources like Smithsonian and Nature."""

    FEEDS = [
        "https://www.smithsonianmag.com/rss/smartnews/",
        "https://www.history.com/.rss/full/",
        "https://www.britannica.com/explore/feeds",
        "https://www.science.org/rss/news_current.xml",
        "https://www.nature.com/subjects/news.rss",
        "https://www.encyclopedia.com/rss",
    ]

    def fetch(self, limit: int) -> List[Article]:
        articles: List[Article] = []
        for url in self.FEEDS:
            data = feedparser.parse(url)
            for entry in data.entries[:limit]:
                raw_title = entry.get("title", "")
                title, source = _split_title_source(raw_title)
                link = _resolve_link(entry.get("link", ""))
                summary = _clean_summary(entry.get("summary", ""))
                published = entry.get("published_parsed")
                if published:
                    published_dt = datetime(*published[:6], tzinfo=timezone.utc)
                else:
                    published_dt = datetime.now(timezone.utc)
                articles.append(
                    Article(
                        title=title,
                        summary=summary,
                        link=link,
                        source=source or url,
                        published=published_dt,
                    )
                )
                if len(articles) >= limit:
                    return articles
        return articles
