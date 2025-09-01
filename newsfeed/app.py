"""Flask interface presenting analyzed news stories with a dashboard UI."""

from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from .fetcher import fetch_top_stories
from .models import Story

app = Flask(__name__)


def _story_to_dict(story: Story) -> dict:
    return {
        "title": story.title,
        "summary": story.summary,
        "link": story.link,
        "source": story.source,
        "category": story.category,
        "published": story.published.isoformat(),
        "relevance": story.relevance.value,
        "relevance_expl": story.relevance.explanation,
        "bias": story.bias.value,
        "bias_expl": story.bias.explanation,
        "trending": story.trending.value,
        "trending_expl": story.trending.explanation,
        "references": [
            {"title": ref.title, "link": ref.link} for ref in story.references
        ],
        "perspectives": [
            {"label": p.label, "text": p.text} for p in story.perspectives
        ],
        "stats": story.stats,
    }


@app.route("/")
def index() -> str:
    """Serve the dashboard shell; stories load dynamically via JS."""
    return render_template("index.html")


@app.route("/stories")
def stories() -> "Response":
    limit = request.args.get("limit", default=20, type=int)
    limit = max(1, min(limit, 100))
    offset = request.args.get("offset", default=0, type=int)
    sort = request.args.get("sort", default="latest", type=str)
    fetched = fetch_top_stories(limit + offset, sort=sort)
    subset = fetched[offset:]
    return jsonify([_story_to_dict(s) for s in subset])


if __name__ == "__main__":
    app.run(debug=True)
