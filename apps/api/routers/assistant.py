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
    normalized_question = question.question.strip().lower()

    if is_reddit_post_detail_question(normalized_question):
        reddit_records = [record for record in records if record.source.lower() == "reddit"]
        reddit_top = sorted(reddit_records, key=priority_score, reverse=True)[:3]
        details = " ".join(format_post_details(record) for record in reddit_top)
        answer = (
            "Here are the available Reddit post details from the filtered feedback set. "
            f"{details or 'No Reddit posts are available for the selected filters.'} "
            "Only public source metadata is shown; private identity or contact details "
            "are not inferred."
        )
        return AssistantResponse(
            answer=answer,
            confidence=0.92 if reddit_top else 0.35,
            records_analyzed=len(reddit_records),
            supporting_record_ids=[record.id for record in reddit_top],
            supporting_source_urls=[record.source_url for record in reddit_top],
        )

    if is_post_definition_question(normalized_question):
        answer = (
            "A post is one collected public feedback item, such as a Reddit discussion, "
            "app-store review, complaint record, social-media mention, or telecom forum entry. "
            "The platform stores each post with its source URL, original text, anonymized author "
            "reference, company, product, location when available, sentiment, topics, confidence, "
            "and the AI summary used for search and executive stories."
        )
        return AssistantResponse(
            answer=answer,
            confidence=0.96,
            records_analyzed=len(records),
            supporting_record_ids=[record.id for record in top],
            supporting_source_urls=[record.source_url for record in top],
        )

    if is_example_post_question(normalized_question):
        examples = "; ".join(
            (
                f"{record.source} on {record.published_at.date().isoformat()} "
                f"for {record.analysis.company}: {record.cleaned_text}"
            )
            for record in top
        )
        answer = (
            "Here are example posts currently in the filtered feedback set, "
            "including their publication dates. "
            f"{examples or 'No matching posts are available for the selected filters.'}"
        )
        return AssistantResponse(
            answer=answer,
            confidence=0.9 if top else 0.4,
            records_analyzed=len(records),
            supporting_record_ids=[record.id for record in top],
            supporting_source_urls=[record.source_url for record in top],
        )

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


def is_post_definition_question(question: str) -> bool:
    return any(
        phrase in question
        for phrase in [
            "what is post",
            "what is a post",
            "what are posts",
            "define post",
            "meaning of post",
        ]
    )


def is_reddit_post_detail_question(question: str) -> bool:
    wants_details = any(
        phrase in question
        for phrase in [
            "all the details",
            "provide the details",
            "post details",
            "details of post",
            "who posted",
            "who is author",
            "author information",
        ]
    )
    return "reddit" in question and ("post" in question or wants_details) and wants_details


def is_example_post_question(question: str) -> bool:
    return any(
        phrase in question
        for phrase in [
            "show post",
            "show me post",
            "example post",
            "sample post",
            "latest post",
            "recent post",
        ]
    )


def format_post_details(record) -> str:
    author = record.public_author_name or record.author_reference
    author_url = (
        f", public author URL: {record.public_author_url}" if record.public_author_url else ""
    )
    author_note = f", author note: {record.public_author_note}" if record.public_author_note else ""
    location = record.location or "not publicly available"
    source_description = source_url_description(str(record.source_url))
    return (
        f"Post {record.id}: source Reddit, published {record.published_at.isoformat()}, "
        f"{source_description}, author: {author}{author_url}{author_note}, "
        f"company: {record.analysis.company}, product: {record.analysis.product or 'unknown'}, "
        f"location: {location}, sentiment: {record.analysis.sentiment_label} "
        f"({record.analysis.sentiment_score}), emotion: {record.analysis.emotion}, "
        f"topics: {', '.join(record.analysis.topics)}, confidence: {record.analysis.confidence}, "
        f"text: {record.cleaned_text}"
    )


def source_url_description(source_url: str) -> str:
    if "example.com" in source_url:
        return (
            f"demo placeholder source URL: {source_url} "
            "(not a live Reddit URL; run live Reddit collection for a public Reddit link)"
        )
    return f"source URL: {source_url}"
