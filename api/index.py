"""Vercel entrypoint exposing the Flask app as a serverless function."""

from newsfeed.app import app

__all__ = ["app"]

