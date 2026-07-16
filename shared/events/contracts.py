from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field

EventName = Literal[
    "feedback.collected",
    "feedback.normalized",
    "feedback.analyzed",
    "issue.detected",
    "story.generated",
]


class PlatformEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: EventName
    subject_id: str
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    payload: dict

