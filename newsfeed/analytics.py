from __future__ import annotations

"""Lightweight NLP and scoring helpers."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Tuple, List

import re
import requests
from bs4 import BeautifulSoup

from .models import Article, Score, Perspective



class Categorizer:
    """Rough categorisation based on keywords."""

    POLITICS = ["election", "minister", "parliament", "government", "policy"]
    TECH = ["tech", "technology", "ai", "innovation"]
    MEDICAL = ["medical", "health", "vaccine", "disease", "covid", "therapy"]
    HISTORY = ["history", "ancient", "archaeology", "heritage"]

    def categorize(self, title: str, summary: str) -> str:
        text = f"{title} {summary}".lower()
        if any(k in text for k in self.POLITICS):
            return "Politics"
        if any(k in text for k in self.MEDICAL):
            return "Medical"
        if any(k in text for k in self.TECH):
            return "Technology"
        if "india" in text and any(k in text for k in self.HISTORY):
            return "Indian History"
        if any(k in text for k in self.HISTORY):
            return "History"
        return "General"


def categorize(title: str, summary: str) -> str:
    return Categorizer().categorize(title, summary)


class RelevanceScorer:
    def score(self, article: Article) -> Score:
        val = 1.0 if "india" in article.title.lower() else 0.5
        expl = "Higher score for India-related titles" if val > 0.5 else "Generic relevance"
        return Score(val, expl)


class BiasScorer:
    def score(self, article: Article) -> Score:
        # Placeholder implementation
        return Score(0.5, "Bias detection not yet implemented")


class TrendPredictor:
    def score(self, article: Article) -> Score:
        hours_old = (datetime.now(timezone.utc) - article.published).total_seconds() / 3600
        val = max(0.0, 1 - hours_old / 24)
        expl = "Newer articles trend higher"
        return Score(val, expl)


class PerspectiveGenerator:
    """Produce placeholder multi-perspective analysis."""

    def generate(self, article: Article) -> List[Perspective]:
        base = article.summary or article.title
        return [
            Perspective("Left", f"Left-leaning view: {base}"),
            Perspective("Right", f"Right-leaning view: {base}"),
            Perspective("Center", f"Neutral view: {base}"),
        ]


class StatsExtractor:
    """Pull simple numeric stats from article content."""

    NUM_RE = re.compile(r"\b[0-9][0-9,\.]*%?\b")

    def extract(self, article: Article) -> List[str]:
        try:
            resp = requests.get(article.link, timeout=5)
            soup = BeautifulSoup(resp.text, "html.parser")
            text = " ".join(p.get_text() for p in soup.find_all("p"))
        except Exception:
            text = article.summary
        nums = self.NUM_RE.findall(text)
        return nums[:5]


class Analyzer:
    """Combine categorisation and scoring into a single step."""

    def __init__(self) -> None:
        self.categorizer = Categorizer()
        self.relevance = RelevanceScorer()
        self.bias = BiasScorer()
        self.trend = TrendPredictor()
        self.persp = PerspectiveGenerator()
        self.stats = StatsExtractor()

    def analyze(self, article: Article) -> Tuple[str, Score, Score, Score]:
        category = self.categorizer.categorize(article.title, article.summary)
        relevance = self.relevance.score(article)
        bias = self.bias.score(article)
        trending = self.trend.score(article)
        return category, relevance, bias, trending

    def generate_perspectives(self, article: Article) -> List[Perspective]:
        return self.persp.generate(article)

    def extract_stats(self, article: Article) -> List[str]:
        return self.stats.extract(article)

    def summarize(self, article: Article) -> str:
        """Fetch article text and return the first few sentences.

        This avoids heavyweight NLP dependencies that require external
        downloads, making the code friendly for read-only environments like
        Vercel serverless functions.
        """
        try:
            resp = requests.get(article.link, timeout=5)
            soup = BeautifulSoup(resp.text, "html.parser")
            text = " ".join(p.get_text() for p in soup.find_all("p"))
            sentences = re.split(r"(?<=[.!?])\s+", text)
            return " ".join(sentences[:3]) or article.summary
        except Exception:
            return article.summary
