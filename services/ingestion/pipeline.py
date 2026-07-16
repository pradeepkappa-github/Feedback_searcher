from services.ingestion.cleaning import clean_text, fingerprint_text
from shared.schemas.feedback import RawFeedbackRecord


def ingest_feedback_batch(records: list[RawFeedbackRecord]) -> list[RawFeedbackRecord]:
    seen: set[str] = set()
    normalized: list[RawFeedbackRecord] = []

    for record in records:
        cleaned = clean_text(record.text)
        fingerprint = fingerprint_text(cleaned)
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        normalized.append(record.model_copy(update={"text": cleaned}))

    return normalized

