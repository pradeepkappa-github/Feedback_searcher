from abc import ABC, abstractmethod
from datetime import UTC, datetime
from urllib.parse import quote_plus

from pydantic import HttpUrl

from shared.schemas.feedback import RawFeedbackRecord
from shared.schemas.sources import SourceConnectorConfig


class SocialConnectorError(RuntimeError):
    pass


class BaseSocialConnector(ABC):
    def __init__(self, config: SourceConnectorConfig, credential_value: str | None = None) -> None:
        self.config = config
        self.credential_value = credential_value

    @abstractmethod
    def collect(self, query_terms: list[str], mock: bool = True) -> list[RawFeedbackRecord]:
        raise NotImplementedError

    def ensure_api_ready(self) -> None:
        if self.config.mode == "official_api" and not self.credential_value:
            raise SocialConnectorError(
                f"{self.config.name} requires credential env {self.config.access_token_env}"
            )

    def mock_record(
        self,
        *,
        text: str,
        company: str,
        product: str,
        location: str,
        path: str,
        author_suffix: str,
    ) -> RawFeedbackRecord:
        return RawFeedbackRecord(
            source=self.config.name,
            source_url=HttpUrl(f"https://example.com/{quote_plus(self.config.platform)}/{path}"),
            company_hint=company,
            product_hint=product,
            text=text,
            published_at=datetime.now(UTC),
            author_reference=f"{self.config.platform}-anon-{author_suffix}",
            location=location,
        )

    def unsupported_api_notice(self) -> list[RawFeedbackRecord]:
        self.ensure_api_ready()
        raise SocialConnectorError(
            f"{self.config.name} official API collection is configured but not implemented. "
            "Add the provider SDK/client here and keep requests within platform policy."
        )

