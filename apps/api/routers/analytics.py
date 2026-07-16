from fastapi import APIRouter, Depends

from apps.api.dependencies import get_repository
from services.analytics.metrics import build_overview, sentiment_by_company, topic_distribution
from services.notifications.rules import detect_alerts

router = APIRouter(tags=["analytics"])


@router.get("/analytics/overview")
def overview(repo=Depends(get_repository)) -> dict:
    records = repo.list_feedback()
    return build_overview(records)


@router.get("/analytics/companies")
def companies(repo=Depends(get_repository)) -> list[dict]:
    return sentiment_by_company(repo.list_feedback())


@router.get("/analytics/topics")
def topics(repo=Depends(get_repository)) -> list[dict]:
    return topic_distribution(repo.list_feedback())


@router.get("/analytics/alerts")
def alerts(repo=Depends(get_repository)) -> list[dict]:
    return detect_alerts(repo.list_feedback())

