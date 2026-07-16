from shared.schemas.feedback import FeedbackRecord


def search_feedback(records: list[FeedbackRecord], query: str) -> list[FeedbackRecord]:
    terms = [term.lower() for term in query.split() if term.strip()]
    if not terms:
        return records
    return [
        record
        for record in records
        if all(term in searchable_text(record).lower() for term in terms)
    ]


def searchable_text(record: FeedbackRecord) -> str:
    return " ".join(
        [
            record.cleaned_text,
            record.analysis.company,
            record.analysis.product or "",
            record.location or "",
            record.source,
            *record.analysis.topics,
            record.analysis.summary,
        ]
    )

