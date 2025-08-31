from __future__ import annotations

"""Lightweight NLP and scoring helpers."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Tuple, List

import nltk
import requests
from bs4 import BeautifulSoup
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lsa import LsaSummarizer

from .models import Article, Score, Perspective

nltk.download("punkt", quiet=True)


class Categorizer:
    """Rough categorisation based on keywords."""

    POLITICS = ["election", "minister", "parliament", "government", "policy"]
    TECH = ["tech", "science", "ai", "technology", "health", "medical"]

    def categorize(self, title: str, summary: str) -> str:
        text = f"{title} {summary}".lower()
        if any(k in text for k in self.POLITICS):
            return "Politics"
        if any(k in text for k in self.TECH):
            return "Tech/Visual"
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


class Analyzer:
    """Combine categorisation and scoring into a single step."""

    def __init__(self) -> None:
        self.categorizer = Categorizer()
        self.relevance = RelevanceScorer()
        self.bias = BiasScorer()
        self.trend = TrendPredictor()
        self.persp = PerspectiveGenerator()
        self.summarizer = LsaSummarizer()

    def analyze(self, article: Article) -> Tuple[str, Score, Score, Score]:
        category = self.categorizer.categorize(article.title, article.summary)
        relevance = self.relevance.score(article)
        bias = self.bias.score(article)
        trending = self.trend.score(article)
        return category, relevance, bias, trending

    def generate_perspectives(self, article: Article) -> List[Perspective]:
        return self.persp.generate(article)

    def summarize(self, article: Article) -> str:
        try:
            resp = requests.get(article.link, timeout=5)
            soup = BeautifulSoup(resp.text, "html.parser")
            text = " ".join(p.get_text() for p in soup.find_all("p"))
            parser = PlaintextParser.from_string(text, Tokenizer("english"))
            summary = self.summarizer(parser.document, sentences_count=3)
            return " ".join(str(s) for s in summary) or article.summary
        except Exception:
            return article.summary
