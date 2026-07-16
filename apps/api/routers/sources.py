from fastapi import APIRouter

from connectors.social.registry import connector_configs
from shared.schemas.feedback import SourceStatus

router = APIRouter(tags=["sources"])


@router.get("/sources/status", response_model=list[SourceStatus])
def source_status() -> list[SourceStatus]:
    return [
        SourceStatus(
            name="Reddit",
            status="Healthy",
            records_collected=1,
            average_latency_ms=1200,
            policy_note="OAuth API and rate limit required for production.",
        ),
        SourceStatus(
            name="Complaint Dataset",
            status="Healthy",
            records_collected=1,
            average_latency_ms=500,
            policy_note="Public bulk import with attribution.",
        ),
        SourceStatus(
            name="Community Forum",
            status="Review",
            records_collected=1,
            average_latency_ms=2300,
            policy_note="Robots and terms review required per site.",
        ),
        SourceStatus(
            name="App Store",
            status="Healthy",
            records_collected=1,
            average_latency_ms=900,
            policy_note="Use approved platform APIs.",
        ),
        SourceStatus(
            name="Approved Social API",
            status="Healthy",
            records_collected=1,
            average_latency_ms=1000,
            policy_note="Provider API only; no scraping.",
        ),
        *[
            SourceStatus(
                name=config.name,
                status="Review" if config.mode == "official_api" else "Healthy",
                records_collected=0,
                average_latency_ms=0,
                policy_note=config.policy_note,
            )
            for config in connector_configs()
        ],
    ]
