from pathlib import Path

from services.ingestion.social_pipeline import collect_analyze_and_vectorize
from services.vector_store.store import LocalVectorStore
from shared.schemas.sources import SocialCollectionRequest


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

