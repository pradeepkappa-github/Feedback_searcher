import html
import re

from shared.security.privacy import mask_personal_information

TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")


def clean_text(text: str) -> str:
    without_html = TAG_RE.sub(" ", html.unescape(text))
    masked = mask_personal_information(without_html)
    return SPACE_RE.sub(" ", masked).strip()


def fingerprint_text(text: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", " ", text.lower())
    return SPACE_RE.sub(" ", normalized).strip()

