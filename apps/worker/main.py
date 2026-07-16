from connectors.sample_dataset.connector import SampleDatasetConnector
from services.ai_analysis.pipeline import analyze_feedback_batch
from services.ingestion.pipeline import ingest_feedback_batch
from services.vector_store.store import LocalVectorStore


def run_once() -> int:
    connector = SampleDatasetConnector()
    raw_records = connector.collect()
    normalized = ingest_feedback_batch(raw_records)
    analyzed = analyze_feedback_batch(normalized)
    LocalVectorStore().upsert_feedback(analyzed)
    return len(analyzed)


if __name__ == "__main__":
    processed = run_once()
    print(f"Processed {processed} feedback records")
