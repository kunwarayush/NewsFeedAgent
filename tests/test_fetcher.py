from newsfeed.fetcher import fetch_top_stories


class DummyEntry(dict):
    pass


class DummyFeed:
    def __init__(self, entries):
        self.entries = entries


def test_limit_and_references(monkeypatch):
    entries = [DummyEntry(title=f"T{i}", link=f"http://example.com/{i}", summary="S") for i in range(10)]

    def fake_parse(url):
        return DummyFeed(entries)

    monkeypatch.setattr("newsfeed.fetcher.feedparser.parse", fake_parse)

    stories = fetch_top_stories(limit=5)
    assert len(stories) == 5
    for story in stories:
        assert len(story.references) == 4
        assert 0 <= story.relevance_score <= 1
        assert 0 <= story.bias_score <= 1
        assert 0 <= story.trending_score <= 1
