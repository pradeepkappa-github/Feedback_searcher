from connectors.sample_dataset.connector import SampleDatasetConnector
from services.ai_analysis.pipeline import analyze_feedback_batch
from services.ingestion.pipeline import ingest_feedback_batch


class InMemoryRepository:
    def __init__(self) -> None:
        self.reload_seed_data()

    def reload_seed_data(self) -> None:
        connector = SampleDatasetConnector()
        raw_records = connector.collect()
        normalized = ingest_feedback_batch(raw_records)
        self.feedback = analyze_feedback_batch(normalized)

    def list_feedback(self):
        return self.feedback

    def add_feedback(self, records):
        normalized = ingest_feedback_batch(records)
        analyzed = analyze_feedback_batch(normalized)
        self.feedback.extend(analyzed)
        return analyzed


repository = InMemoryRepository()

