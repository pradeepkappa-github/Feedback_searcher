from apps.api.core.config import settings
from connectors.sample_dataset.connector import SampleDatasetConnector
from services.ai_analysis.pipeline import analyze_feedback_batch
from services.ingestion.pipeline import ingest_feedback_batch
from services.vector_store.store import LocalVectorStore


class InMemoryRepository:
    def __init__(self) -> None:
        self.vector_store = LocalVectorStore(settings.vector_store_path)
        self.reload_seed_data()

    def reload_seed_data(self) -> None:
        connector = SampleDatasetConnector()
        raw_records = connector.collect()
        normalized = ingest_feedback_batch(raw_records)
        self.feedback = analyze_feedback_batch(normalized)
        self.vector_store.upsert_feedback(self.feedback)

    def list_feedback(self):
        return self.feedback

    def add_feedback(self, records):
        normalized = ingest_feedback_batch(records)
        analyzed = analyze_feedback_batch(normalized)
        self.feedback.extend(analyzed)
        self.vector_store.upsert_feedback(analyzed)
        return analyzed

    def add_analyzed_feedback(self, records):
        self.feedback.extend(records)
        self.vector_store.upsert_feedback(records)
        return records


repository = InMemoryRepository()
