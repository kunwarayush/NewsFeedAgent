from __future__ import annotations

"""Flask interface presenting analyzed news stories."""

from flask import Flask, render_template, request

from .fetcher import fetch_top_stories

app = Flask(__name__)


@app.route("/")
def index():
    limit = request.args.get("limit", default=10, type=int)
    page = request.args.get("page", default=1, type=int)
    sort = request.args.get("sort", default="latest", type=str)
    all_stories = fetch_top_stories(limit * page, sort=sort)
    start = (page - 1) * limit
    stories = all_stories[start : start + limit]
    next_page = page + 1 if len(all_stories) > page * limit else None
    prev_page = page - 1 if page > 1 else None
    return render_template(
        "index.html",
        stories=stories,
        limit=limit,
        page=page,
        sort=sort,
        next_page=next_page,
        prev_page=prev_page,
    )


if __name__ == "__main__":
    app.run(debug=True)
