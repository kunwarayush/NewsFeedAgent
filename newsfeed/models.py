from __future__ import annotations

"""Core data models used across the newsfeed package."""

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Reference:
    """A supporting reference link for a story."""

    title: str
    link: str


@dataclass
class Score:
    """Numeric score with an optional explanation."""

    value: float
    explanation: str = ""


@dataclass
class Article:
    """Raw article information produced by a crawler."""

    title: str
    summary: str
    link: str
    source: str
    published: datetime


@dataclass
class Story:
    """Fully analysed story presented to editors."""

    title: str
    summary: str
    link: str
    source: str
    category: str
    published: datetime
    relevance: Score
    bias: Score
    trending: Score
    references: List[Reference]

    @property
    def relevance_score(self) -> float:  # backward compatibility
        return self.relevance.value

    @property
    def bias_score(self) -> float:
        return self.bias.value

    @property
    def trending_score(self) -> float:
        return self.trending.value
