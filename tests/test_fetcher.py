from newsfeed.fetcher import fetch_top_stories
from newsfeed.twitter_feed import TwitterTrendsFetcher


class DummyEntry(dict):
    pass


class DummyFeed:
    def __init__(self, entries):
        self.entries = entries


def test_limit_and_references(monkeypatch):
    entries = [DummyEntry(title=f"T{i}", link=f"http://example.com/{i}", summary="S") for i in range(10)]

    def fake_parse(url):
        return DummyFeed(entries)

    monkeypatch.setattr("newsfeed.crawler.feedparser.parse", fake_parse)

    stories = fetch_top_stories(limit=5, include_twitter=False)
    assert len(stories) == 5
    for story in stories:
        assert len(story.references) == 4
        assert 0 <= story.relevance_score <= 1
        assert 0 <= story.bias_score <= 1
        assert 0 <= story.trending_score <= 1


def test_twitter_fetcher_handles_missing_credentials(monkeypatch):
    monkeypatch.delenv("TWITTER_BEARER_TOKEN", raising=False)
    monkeypatch.delenv("TWITTER_API_KEY", raising=False)
    monkeypatch.delenv("TWITTER_API_SECRET", raising=False)
    tf = TwitterTrendsFetcher()
    assert tf.fetch(5) == []


def test_deduplicates_titles(monkeypatch):
    entries = [
        DummyEntry(title="Same", link="http://example.com/1", summary="S"),
        DummyEntry(title="Same", link="http://example.com/2", summary="S"),
    ]

    def fake_parse(url):
        return DummyFeed(entries)

    monkeypatch.setattr("newsfeed.crawler.feedparser.parse", fake_parse)

    stories = fetch_top_stories(limit=10, include_twitter=False)
    assert len(stories) == 1
