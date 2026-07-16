from fastapi import APIRouter, Depends

from apps.api.dependencies import get_repository
from services.analytics.metrics import priority_score
from shared.schemas.feedback import AssistantQuestion, AssistantResponse

router = APIRouter(tags=["assistant"])


@router.post("/assistant/ask", response_model=AssistantResponse)
def ask_assistant(question: AssistantQuestion, repo=Depends(get_repository)) -> AssistantResponse:
    records = repo.list_feedback()
    if question.company:
        records = [record for record in records if record.analysis.company == question.company]
    if question.topic:
        records = [record for record in records if question.topic in record.analysis.topics]

    ranked = sorted(records, key=priority_score, reverse=True)
    top = ranked[:3]
    topic_counts: dict[str, int] = {}
    for record in records:
        for topic in record.analysis.topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

    sorted_topics = sorted(topic_counts.items(), key=lambda item: item[1], reverse=True)
    top_topics = ", ".join(topic for topic, _ in sorted_topics[:3])
    company_text = question.company or "the selected companies"
    locations = ", ".join(sorted({record.location for record in top if record.location}))
    answer = (
        f"Negative sentiment for {company_text} is primarily associated with "
        f"{top_topics or 'mixed topics'}. "
        f"The highest-priority evidence comes from {locations or 'the retrieved feedback set'}. "
        "Recommended next actions are to audit billing explanations, outage communication, "
        "and support escalation queues."
    )

    confidence = round(sum(record.analysis.confidence for record in top) / max(len(top), 1), 2)
    return AssistantResponse(
        answer=answer,
        confidence=confidence,
        records_analyzed=len(records),
        supporting_record_ids=[record.id for record in top],
        supporting_source_urls=[record.source_url for record in top],
    )
