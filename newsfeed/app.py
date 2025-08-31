from __future__ import annotations

"""Flask interface presenting analyzed news stories."""

from flask import Flask, render_template, request

from .fetcher import fetch_top_stories

app = Flask(__name__)


@app.route("/")
def index():
    limit = request.args.get("limit", default=10, type=int)
    stories = fetch_top_stories(limit)
    return render_template("index.html", stories=stories)


if __name__ == "__main__":
    app.run(debug=True)
