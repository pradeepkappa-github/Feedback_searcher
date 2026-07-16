from connectors.social.registry import build_social_connectors
from services.ai_analysis.pipeline import analyze_feedback_batch
from services.ingestion.pipeline import ingest_feedback_batch
from services.vector_store.store import LocalVectorStore
from shared.schemas.feedback import FeedbackRecord
from shared.schemas.sources import CollectionRunResult, SocialCollectionRequest


def collect_analyze_and_vectorize(
    request: SocialCollectionRequest,
    *,
    vector_store: LocalVectorStore,
    connector_mode: str = "mock",
) -> tuple[list[CollectionRunResult], list[FeedbackRecord]]:
    selected = set(request.connectors or [])
    raw_records = []
    results: list[CollectionRunResult] = []

    for connector in build_social_connectors(connector_mode):
        connector_selected = (
            connector.config.platform in selected or connector.config.name in selected
        )
        if selected and not connector_selected:
            continue
        warnings = []
        try:
            collected = connector.collect(request.query_terms, mock=request.mock)
        except Exception as exc:
            collected = []
            warnings.append(str(exc))
        raw_records.extend(collected)
        results.append(
            CollectionRunResult(
                connector=connector.config.name,
                platform=connector.config.platform,
                mode="mock" if request.mock else "public_feed",
                records_collected=len(collected),
                records_stored=0,
                vector_documents_stored=0,
                warnings=warnings,
            )
        )

    analyzed = analyze_feedback_batch(ingest_feedback_batch(raw_records))
    vector_count = vector_store.upsert_feedback(analyzed)

    if results:
        stored_per_connector = {
            result.connector: sum(1 for record in analyzed if record.source == result.connector)
            for result in results
        }
        updated = []
        for result in results:
            stored = stored_per_connector.get(result.connector, 0)
            updated.append(
                result.model_copy(
                    update={
                        "records_stored": stored,
                        "vector_documents_stored": stored if vector_count else 0,
                    }
                )
            )
        results = updated

    return results, analyzed
