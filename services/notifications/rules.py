from services.analytics.metrics import priority_score
from shared.schemas.feedback import FeedbackRecord


def detect_alerts(records: list[FeedbackRecord]) -> list[dict]:
    return [
        {
            "feedback_id": record.id,
            "company": record.analysis.company,
            "title": f"{record.analysis.company}: {', '.join(record.analysis.topics[:2])}",
            "priority_score": priority_score(record),
            "summary": record.analysis.summary,
        }
        for record in records
        if priority_score(record) >= 0.75
    ]

