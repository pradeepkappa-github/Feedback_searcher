import hashlib
import re
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
        search_params = urlencode({"q": query, "sort": "new", "t": "month"})
        feed_urls = [f"https://www.reddit.com/search.rss?{search_params}"]
        feed_urls.extend(reddit_subreddit_feed_urls(query))

        for feed_url in feed_urls:
            try:
                record = self.collect_first_matching_feed_record(feed_url, query_terms)
            except Exception:
                continue
            if record is not None:
                return [record]
        return []

    def collect_first_matching_feed_record(
        self, feed_url: str, query_terms: list[str]
    ) -> RawFeedbackRecord | None:
        request = Request(
            feed_url,
            headers={
                "User-Agent": "FeedbackFinderAI/0.1 public feedback research",
                "Accept": "application/atom+xml, application/xml;q=0.9, */*;q=0.8",
            },
        )

        with urlopen(request, timeout=15) as response:
            feed_xml = response.read()
        root = ElementTree.fromstring(feed_xml)
        entries = root.findall("atom:entry", ATOM_NS)
        for entry in entries:
            source_url = entry_url(entry)
            if "/comments/" not in source_url:
                continue
            title = text_or_empty(entry, "atom:title")
            content = text_or_empty(entry, "atom:content")
            updated = text_or_empty(entry, "atom:updated")
            author_name = text_or_empty(entry, "atom:author/atom:name")
            author_uri = text_or_empty(entry, "atom:author/atom:uri")
            entry_id = text_or_empty(entry, "atom:id") or source_url
            text = clean_feed_text(f"{title}. {content}")
            if not has_telecom_context(text):
                continue
            return RawFeedbackRecord(
                source=self.config.name,
                source_url=source_url,
                company_hint=detect_company_hint(text, query_terms),
                product_hint=detect_product_hint(text),
                text=text[:2000],
                published_at=parse_feed_datetime(updated),
                author_reference=f"reddit-live-{stable_suffix(entry_id)}",
                public_author_name=author_name or None,
                public_author_url=author_uri or None,
                public_author_note=public_author_note(author_name, author_uri),
                location=None,
            )
        return None


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


def reddit_subreddit_feed_urls(query: str) -> list[str]:
    lower = query.lower()
    subreddits = []
    if "at&t" in lower or "att" in lower or "fiber" in lower:
        subreddits.extend(["ATT", "ATTFiber"])
    if "verizon" in lower:
        subreddits.extend(["verizon", "verizonisp"])
    if "t-mobile" in lower or "tmobile" in lower:
        subreddits.append("tmobile")
    if "xfinity" in lower or "comcast" in lower:
        subreddits.extend(["Comcast_Xfinity", "xfinity"])
    if not subreddits:
        subreddits.extend(["ATT", "ATTFiber", "verizon", "tmobile", "Comcast_Xfinity"])
    return [
        f"https://www.reddit.com/r/{subreddit}/new/.rss"
        for subreddit in dict.fromkeys(subreddits)
    ]


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
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
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


def public_author_note(author_name: str, author_uri: str) -> str:
    if author_name and author_uri:
        return "Public Reddit feed exposed author display name and profile URL."
    if author_name:
        return "Public Reddit feed exposed author display name only."
    return "No public author profile metadata was exposed by the feed item."


def parse_feed_datetime(value: str) -> datetime:
    if not value:
        return datetime.now(UTC)
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def detect_company_hint(text: str, query_terms: list[str]) -> str | None:
    lower = text.lower()
    companies = ["AT&T", "Verizon", "T-Mobile", "Xfinity Mobile"]
    for company in companies:
        if company.lower() in lower:
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


def has_telecom_context(text: str) -> bool:
    lower = text.lower()
    company_terms = [
        "at&t",
        "att ",
        "att fiber",
        "verizon",
        "t-mobile",
        "tmobile",
        "xfinity",
    ]
    service_terms = [
        "internet outage",
        "internet service",
        "internet bill",
        "home internet",
        "fiber internet",
        "wireless",
        "broadband",
        "cell service",
        "mobile plan",
        "coverage",
        "outage",
        "router",
        "modem",
        "isp",
    ]
    return any(term in lower for term in company_terms) or sum(
        1 for term in service_terms if term in lower
    ) >= 2
