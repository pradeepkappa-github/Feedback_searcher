from uuid import NAMESPACE_URL, uuid5

from services.ai_analysis.classifier import analyze_feedback
from shared.schemas.feedback import FeedbackRecord, RawFeedbackRecord


def analyze_feedback_batch(records: list[RawFeedbackRecord]) -> list[FeedbackRecord]:
    analyzed: list[FeedbackRecord] = []
    for record in records:
        analysis = analyze_feedback(record)
        record_id = str(uuid5(NAMESPACE_URL, f"{record.source}:{record.source_url}:{record.text}"))
        analyzed.append(
            FeedbackRecord(
                **record.model_dump(),
                id=record_id,
                cleaned_text=record.text,
                analysis=analysis,
            )
        )
    return analyzed

