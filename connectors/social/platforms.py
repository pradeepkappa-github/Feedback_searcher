import hashlib
from datetime import UTC, datetime
from html import unescape
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from connectors.social.base import BaseSocialConnector
from shared.schemas.feedback import RawFeedbackRecord
from shared.schemas.sources import SourceConnectorConfig

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


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
            return self.collect_live_rss(query_terms)
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

    def collect_live_rss(self, query_terms: list[str]) -> list[RawFeedbackRecord]:
        query = " ".join(query_terms or ["AT&T", "Verizon", "T-Mobile", "Xfinity Mobile"])
        params = urlencode({"q": query, "sort": "new", "t": "month"})
        request = Request(
            f"https://www.reddit.com/search.rss?{params}",
            headers={
                "User-Agent": "FeedbackFinderAI/0.1 public feedback research",
                "Accept": "application/atom+xml, application/xml;q=0.9, */*;q=0.8",
            },
        )

        with urlopen(request, timeout=15) as response:
            feed_xml = response.read()

        root = ElementTree.fromstring(feed_xml)
        entries = root.findall("atom:entry", ATOM_NS)
        entry = next((item for item in entries if entry_url(item).find("/comments/") >= 0), None)
        if entry is None and entries:
            entry = entries[0]
        if entry is None:
            return []

        title = text_or_empty(entry, "atom:title")
        content = text_or_empty(entry, "atom:content")
        updated = text_or_empty(entry, "atom:updated")
        source_url = entry_url(entry) or "https://www.reddit.com"
        entry_id = text_or_empty(entry, "atom:id") or source_url
        text = clean_feed_text(f"{title}. {content}")

        return [
            RawFeedbackRecord(
                source=self.config.name,
                source_url=source_url,
                company_hint=detect_company_hint(text, query_terms),
                product_hint=detect_product_hint(text),
                text=text[:2000],
                published_at=parse_feed_datetime(updated),
                author_reference=f"reddit-live-{stable_suffix(entry_id)}",
                location=None,
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


def text_or_empty(entry: ElementTree.Element, selector: str) -> str:
    value = entry.findtext(selector, default="", namespaces=ATOM_NS)
    return value or ""


def entry_url(entry: ElementTree.Element) -> str:
    link = entry.find("atom:link[@rel='alternate']", ATOM_NS)
    if link is None:
        link = entry.find("atom:link", ATOM_NS)
    return link.attrib.get("href", "") if link is not None else ""


def clean_feed_text(value: str) -> str:
    text = unescape(value)
    for left, right in [
        ("<p>", " "),
        ("</p>", " "),
        ("<br>", " "),
        ("<br/>", " "),
        ("<br />", " "),
    ]:
        text = text.replace(left, right)
    return " ".join(text.split())


def stable_suffix(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def parse_feed_datetime(value: str) -> datetime:
    if not value:
        return datetime.now(UTC)
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def detect_company_hint(text: str, query_terms: list[str]) -> str | None:
    lower = text.lower()
    companies = ["AT&T", "Verizon", "T-Mobile", "Xfinity Mobile"]
    for company in companies:
        if company.lower() in lower or company in query_terms:
            return company
    return None


def detect_product_hint(text: str) -> str | None:
    lower = text.lower()
    if "fiber" in lower:
        return "Fiber"
    if "wireless" in lower or "phone" in lower:
        return "Wireless"
    if "internet" in lower:
        return "Broadband"
    return None
