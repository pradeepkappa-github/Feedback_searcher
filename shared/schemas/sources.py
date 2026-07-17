from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl

ConnectorMode = Literal["mock", "official_api", "public_feed"]


class SourceConnectorConfig(BaseModel):
    name: str
    platform: str
    enabled: bool = True
    mode: ConnectorMode = "mock"
    query_terms: list[str] = Field(default_factory=list)
    company_terms: list[str] = Field(default_factory=list)
    api_base_url: HttpUrl | None = None
    access_token_env: str | None = None
    client_id_env: str | None = None
    client_secret_env: str | None = None
    rate_limit_per_minute: int = Field(default=30, ge=1)
    policy_note: str
    last_collected_at: datetime | None = None


class CollectionRunResult(BaseModel):
    connector: str
    platform: str
    mode: ConnectorMode
    records_collected: int
    records_stored: int
    vector_documents_stored: int
    warnings: list[str] = Field(default_factory=list)


class SocialCollectionRequest(BaseModel):
    connectors: list[str] | None = None
    query_terms: list[str] = Field(
        default_factory=lambda: ["AT&T", "Verizon", "T-Mobile", "Xfinity Mobile"]
    )
    mock: bool = True


class VectorSearchRequest(BaseModel):
    query: str = Field(min_length=2)
    company: str | None = None
    source: str | None = None
    include_demo: bool = False
    limit: int = Field(default=5, ge=1, le=25)


class VectorSearchHit(BaseModel):
    id: str
    score: float
    text: str
    source: str
    source_url: HttpUrl
    company: str
    product: str | None = None
    topics: list[str]
    sentiment_score: float
    published_at: datetime
    public_author_name: str | None = None
    public_author_url: HttpUrl | None = None
    public_author_note: str | None = None
    comment_conclusion: str | None = None
    is_demo: bool = False
