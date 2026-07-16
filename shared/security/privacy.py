import re

EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
PHONE_RE = re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")


def mask_personal_information(text: str) -> str:
    text = EMAIL_RE.sub("[masked-email]", text)
    return PHONE_RE.sub("[masked-phone]", text)

