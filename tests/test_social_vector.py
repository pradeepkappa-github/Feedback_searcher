from pathlib import Path

from connectors.social.platforms import RedditConnector
from services.ingestion.social_pipeline import collect_analyze_and_vectorize
from services.vector_store.store import LocalVectorStore
from shared.schemas.sources import SocialCollectionRequest, SourceConnectorConfig


def test_social_mock_collection_stores_vectors(tmp_path: Path):
    store = LocalVectorStore(str(tmp_path / "vectors.json"))
    request = SocialCollectionRequest(connectors=["reddit", "x"], mock=True)

    results, records = collect_analyze_and_vectorize(
        request,
        vector_store=store,
        connector_mode="mock",
    )

    assert len(results) == 2
    assert len(records) == 2
    assert store.count() == 2


def test_vector_search_returns_relevant_feedback(tmp_path: Path):
    store = LocalVectorStore(str(tmp_path / "vectors.json"))
    request = SocialCollectionRequest(connectors=["x"], mock=True)
    collect_analyze_and_vectorize(request, vector_store=store, connector_mode="mock")

    hits = store.search("Houston fiber outage status page", limit=1)

    assert hits
    assert hits[0].company == "AT&T"
    assert "Network outage" in hits[0].topics


def test_reddit_live_rss_collects_one_public_record(monkeypatch):
    rss = b"""<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
      <entry>
        <id>reddit-post-1</id>
        <title>AT&amp;T fiber outage in Houston</title>
        <updated>2026-07-16T20:01:02+00:00</updated>
        <author>
          <name>u/public_user</name>
          <uri>https://www.reddit.com/user/public_user</uri>
        </author>
        <link rel="alternate" href="https://www.reddit.com/r/ATT/comments/example" />
        <content type="html">
          &lt;p&gt;Status page says no outage but fiber is down.&lt;/p&gt;
        </content>
      </entry>
    </feed>
    """

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def read(self):
            return rss

    def fake_urlopen(request, timeout):
        assert "search.rss" in request.full_url
        assert timeout == 15
        return FakeResponse()

    monkeypatch.setattr("connectors.social.platforms.urlopen", fake_urlopen)
    connector = RedditConnector(
        SourceConnectorConfig(
            name="Reddit",
            platform="reddit",
            policy_note="Use Reddit public feeds or API within policy.",
        )
    )

    records = connector.collect(["AT&T", "fiber", "outage"], mock=False)

    assert len(records) == 1
    assert records[0].source == "Reddit"
    assert records[0].company_hint == "AT&T"
    assert records[0].product_hint == "Fiber"
    assert records[0].public_author_name == "u/public_user"
    assert str(records[0].public_author_url) == "https://www.reddit.com/user/public_user"
    assert "profile URL" in records[0].public_author_note
    assert "fiber is down" in records[0].text
