from collections import Counter, defaultdict

from shared.schemas.feedback import FeedbackRecord


def build_overview(records: list[FeedbackRecord]) -> dict:
    total = len(records)
    positive = sum(1 for record in records if record.analysis.sentiment_score > 0.2)
    negative = sum(1 for record in records if record.analysis.sentiment_score < -0.2)
    confidence = sum(record.analysis.confidence for record in records) / max(total, 1)

    return {
        "total_feedback": total,
        "positive_share": round(positive / max(total, 1), 2),
        "negative_share": round(negative / max(total, 1), 2),
        "average_confidence": round(confidence, 2),
        "critical_issues": [
            record
            for record in sorted(records, key=lambda item: priority_score(item), reverse=True)
            if priority_score(record) >= 0.75
        ][:5],
    }


def sentiment_by_company(records: list[FeedbackRecord]) -> list[dict]:
    grouped: dict[str, list[FeedbackRecord]] = defaultdict(list)
    for record in records:
        grouped[record.analysis.company].append(record)

    return [
        {
            "company": company,
            "positive_share": round(
                sum(1 for record in company_records if record.analysis.sentiment_score > 0.2)
                / max(len(company_records), 1),
                2,
            ),
            "average_sentiment": round(
                sum(record.analysis.sentiment_score for record in company_records)
                / max(len(company_records), 1),
                2,
            ),
            "volume": len(company_records),
        }
        for company, company_records in sorted(grouped.items())
    ]


def topic_distribution(records: list[FeedbackRecord]) -> list[dict]:
    counter: Counter[str] = Counter()
    for record in records:
        counter.update(record.analysis.topics)
    total = sum(counter.values())
    return [
        {"topic": topic, "count": count, "share": round(count / max(total, 1), 2)}
        for topic, count in counter.most_common()
    ]


def priority_score(record: FeedbackRecord) -> float:
    severity = abs(min(record.analysis.sentiment_score, 0.0))
    return round(
        min(
            1.0,
            severity * 0.45
            + record.analysis.urgency_score * 0.25
            + record.analysis.credibility_score * 0.15
            + record.analysis.confidence * 0.15,
        ),
        2,
    )

