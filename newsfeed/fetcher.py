from __future__ import annotations

"""Public API for fetching analysed stories."""

from typing import List

from .story_builder import StoryBuilder
from .models import Story

_builder = StoryBuilder()


def fetch_top_stories(limit: int = 20, sort: str = "latest", include_twitter: bool = True) -> List[Story]:
    """Fetch analysed stories ready for presentation.

    Args:
        limit: Number of stories to return (1-100).
        sort: Ordering of stories - ``latest``, ``trending``, ``top`` or ``oldest``.
        include_twitter: Whether to blend in Twitter trending stories.
    """

    return _builder.build(limit=limit, sort=sort, include_twitter=include_twitter)
