from fastapi import APIRouter, Depends, Query

from apps.api.dependencies import get_repository
from services.search.retrieval import search_feedback
from shared.schemas.feedback import FeedbackRecord, RawFeedbackRecord

router = APIRouter(tags=["feedback"])


@router.get("/feedback", response_model=list[FeedbackRecord])
def list_feedback(
    company: str | None = None,
    source: str | None = None,
    topic: str | None = None,
    query: str | None = Query(default=None, min_length=1),
    repo=Depends(get_repository),
):
    records = repo.list_feedback()
    if company:
        records = [record for record in records if record.analysis.company == company]
    if source:
        records = [record for record in records if record.source == source]
    if topic:
        records = [record for record in records if topic in record.analysis.topics]
    if query:
        records = search_feedback(records, query)
    return records


@router.post("/feedback/ingest", response_model=list[FeedbackRecord])
def ingest_feedback(records: list[RawFeedbackRecord], repo=Depends(get_repository)):
    return repo.add_feedback(records)

