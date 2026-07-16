from fastapi import APIRouter, Depends

from apps.api.core.config import settings
from apps.api.dependencies import get_repository
from connectors.social.registry import connector_configs
from services.ingestion.social_pipeline import collect_analyze_and_vectorize
from shared.schemas.feedback import FeedbackRecord
from shared.schemas.sources import (
    CollectionRunResult,
    SocialCollectionRequest,
    SourceConnectorConfig,
    VectorSearchHit,
    VectorSearchRequest,
)

router = APIRouter(tags=["social-sources"])


@router.get("/sources/social", response_model=list[SourceConnectorConfig])
def list_social_connectors() -> list[SourceConnectorConfig]:
    return connector_configs(settings.social_connector_mode)


@router.post("/sources/social/collect")
def collect_social_feedback(
    request: SocialCollectionRequest,
    repo=Depends(get_repository),
) -> dict[str, list[CollectionRunResult] | list[FeedbackRecord] | int]:
    results, analyzed = collect_analyze_and_vectorize(
        request,
        vector_store=repo.vector_store,
        connector_mode=settings.social_connector_mode,
    )
    repo.feedback.extend(analyzed)
    return {
        "results": results,
        "records": analyzed,
        "vector_documents_total": repo.vector_store.count(),
    }


@router.post("/vector/search", response_model=list[VectorSearchHit])
def vector_search(
    request: VectorSearchRequest,
    repo=Depends(get_repository),
) -> list[VectorSearchHit]:
    return repo.vector_store.search(
        request.query,
        company=request.company,
        source=request.source,
        include_demo=request.include_demo,
        limit=request.limit,
    )


@router.get("/vector/status")
def vector_status(repo=Depends(get_repository)) -> dict:
    return {
        "documents": repo.vector_store.count(),
        "live_documents": repo.vector_store.count_live(),
        "demo_documents": repo.vector_store.count_demo(),
        "path": settings.vector_store_path,
        "embedding": "deterministic-hashed-local",
    }
