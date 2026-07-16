from datetime import UTC, datetime

from services.ingestion.cleaning import clean_text
from services.ingestion.pipeline import ingest_feedback_batch
from shared.schemas.feedback import RawFeedbackRecord


def test_clean_text_masks_personal_information():
    cleaned = clean_text("Call me at 555-123-4567 or email me@example.com <b>now</b>")

    assert "[masked-phone]" in cleaned
    assert "[masked-email]" in cleaned
    assert "<b>" not in cleaned


def test_ingestion_removes_duplicate_feedback():
    record = RawFeedbackRecord(
        source="Reddit",
        source_url="https://example.com/one",
        text="AT&T fiber is down",
        published_at=datetime(2026, 7, 15, tzinfo=UTC),
        author_reference="anon",
    )

    records = ingest_feedback_batch([record, record.model_copy(update={"source_url": "https://example.com/two"})])

    assert len(records) == 1

