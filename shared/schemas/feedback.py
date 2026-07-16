from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl

SentimentLabel = Literal["Very positive", "Positive", "Neutral", "Negative", "Very negative"]


class RawFeedbackRecord(BaseModel):
    source: str
    source_url: HttpUrl
    company_hint: str | None = None
    product_hint: str | None = None
    text: str = Field(min_length=3)
    published_at: datetime
    author_reference: str
    public_author_name: str | None = None
    public_author_url: HttpUrl | None = None
    public_author_note: str | None = None
    location: str | None = None
    language: str = "English"


class AnalysisResult(BaseModel):
    company: str
    product: str | None = None
    sentiment_label: SentimentLabel
    sentiment_score: float = Field(ge=-1.0, le=1.0)
    emotion: str
    topics: list[str]
    summary: str
    root_causes: list[str] = Field(default_factory=list)
    urgency_score: float = Field(ge=0.0, le=1.0)
    credibility_score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)


class FeedbackRecord(RawFeedbackRecord):
    id: str
    cleaned_text: str
    collected_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    analysis: AnalysisResult


class SourceStatus(BaseModel):
    name: str
    status: Literal["Healthy", "Review", "Paused"]
    records_collected: int
    average_latency_ms: int
    policy_note: str


class AssistantQuestion(BaseModel):
    question: str = Field(min_length=3)
    company: str | None = None
    topic: str | None = None
    days: int = Field(default=7, ge=1, le=90)


class AssistantResponse(BaseModel):
    answer: str
    confidence: float = Field(ge=0.0, le=1.0)
    records_analyzed: int
    supporting_record_ids: list[str]
    supporting_source_urls: list[HttpUrl]
