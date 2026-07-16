from connectors.social.base import BaseSocialConnector
from shared.schemas.feedback import RawFeedbackRecord
from shared.schemas.sources import SourceConnectorConfig


class LinkedInConnector(BaseSocialConnector):
    def collect(self, query_terms: list[str], mock: bool = True) -> list[RawFeedbackRecord]:
        if not mock:
            return self.unsupported_api_notice()
        return [
            self.mock_record(
                text=(
                    "Business fiber buyers are comparing AT&T and Verizon after another "
                    "installation delay for a downtown office."
                ),
                company="AT&T",
                product="Business services",
                location="Dallas, TX",
                path="linkedin-telecom-business-delay",
                author_suffix="li01",
            )
        ]


class FacebookConnector(BaseSocialConnector):
    def collect(self, query_terms: list[str], mock: bool = True) -> list[RawFeedbackRecord]:
        if not mock:
            return self.unsupported_api_notice()
        return [
            self.mock_record(
                text=(
                    "Neighbors are posting that Xfinity Mobile promo pricing changed after "
                    "two billing cycles and support has not clarified it."
                ),
                company="Xfinity Mobile",
                product="Wireless",
                location="Atlanta, GA",
                path="facebook-xfinity-promo-billing",
                author_suffix="fb01",
            )
        ]


class InstagramConnector(BaseSocialConnector):
    def collect(self, query_terms: list[str], mock: bool = True) -> list[RawFeedbackRecord]:
        if not mock:
            return self.unsupported_api_notice()
        return [
            self.mock_record(
                text=(
                    "Several comments under a store post mention T-Mobile activation problems "
                    "but praise the local team for follow-up."
                ),
                company="T-Mobile",
                product="Postpaid",
                location="San Diego, CA",
                path="instagram-tmobile-activation-comments",
                author_suffix="ig01",
            )
        ]


class XConnector(BaseSocialConnector):
    def collect(self, query_terms: list[str], mock: bool = True) -> list[RawFeedbackRecord]:
        if not mock:
            return self.unsupported_api_notice()
        return [
            self.mock_record(
                text=(
                    "AT&T fiber outage reports are spiking around Houston while the status "
                    "page still says there is no known issue."
                ),
                company="AT&T",
                product="Fiber",
                location="Houston, TX",
                path="x-att-houston-fiber-outage",
                author_suffix="x01",
            )
        ]


class TruthSocialConnector(BaseSocialConnector):
    def collect(self, query_terms: list[str], mock: bool = True) -> list[RawFeedbackRecord]:
        if not mock:
            return self.unsupported_api_notice()
        return [
            self.mock_record(
                text=(
                    "Users are complaining that Verizon coverage is weaker inside office "
                    "buildings this week, especially during afternoon calls."
                ),
                company="Verizon",
                product="Wireless",
                location="Raleigh, NC",
                path="truth-verizon-office-coverage",
                author_suffix="ts01",
            )
        ]


class RedditConnector(BaseSocialConnector):
    def collect(self, query_terms: list[str], mock: bool = True) -> list[RawFeedbackRecord]:
        if not mock:
            return self.unsupported_api_notice()
        return [
            self.mock_record(
                text=(
                    "Reddit thread says AT&T first bills include activation fees customers "
                    "did not expect after switching plans online."
                ),
                company="AT&T",
                product="Wireless",
                location="Austin, TX",
                path="reddit-att-activation-fees",
                author_suffix="rd01",
            )
        ]


class TelecomCommunityForumConnector(BaseSocialConnector):
    def collect(self, query_terms: list[str], mock: bool = True) -> list[RawFeedbackRecord]:
        if not mock:
            return self.unsupported_api_notice()
        return [
            self.mock_record(
                text=(
                    "Community forum replies show customers asking why technician windows "
                    "for fiber repair were rescheduled without text notifications."
                ),
                company="AT&T",
                product="Fiber",
                location="Dallas, TX",
                path="forum-fiber-technician-window",
                author_suffix="cf01",
            )
        ]


CONNECTOR_TYPES = {
    "linkedin": LinkedInConnector,
    "facebook": FacebookConnector,
    "instagram": InstagramConnector,
    "x": XConnector,
    "truthsocial": TruthSocialConnector,
    "reddit": RedditConnector,
    "telecom_community": TelecomCommunityForumConnector,
}


def build_connector(config: SourceConnectorConfig, credential_value: str | None = None):
    connector_type = CONNECTOR_TYPES[config.platform]
    return connector_type(config, credential_value)

