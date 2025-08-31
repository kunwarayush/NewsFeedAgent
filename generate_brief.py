"""Command-line helper to generate a text brief of top stories.

This can be scheduled via cron or any task scheduler. It prints a simple
markdown summary to stdout which can be redirected to a file or sent via
email/Slack.
"""

from __future__ import annotations

import argparse

from newsfeed.fetcher import fetch_top_stories


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a daily news brief")
    parser.add_argument("--limit", type=int, default=10, help="Number of stories")
    args = parser.parse_args()

    stories = fetch_top_stories(limit=args.limit)
    for story in stories:
        print(f"# {story.title}\n")
        print(story.summary)
        print("\nReferences:")
        for ref in story.references:
            print(f"- {ref.title} - {ref.link}")
        print("\n")


if __name__ == "__main__":
    main()

