from shared.schemas.feedback import AnalysisResult, RawFeedbackRecord

COMPANY_ALIASES = {
    "AT&T": ["at&t", "att"],
    "Verizon": ["verizon"],
    "T-Mobile": ["t-mobile", "tmobile"],
    "Xfinity Mobile": ["xfinity", "xfinity mobile"],
}

TOPIC_KEYWORDS = {
    "Billing": ["bill", "billing", "charge", "fee", "roaming"],
    "Network outage": ["outage", "down", "status page"],
    "Coverage": ["coverage", "signal", "calls"],
    "Internet speed": ["speed", "slow", "gigabit", "gateway"],
    "Customer support": ["support", "agent", "chat", "wait"],
    "Activation": ["activate", "activation", "port-in", "sim"],
    "Device issue": ["device", "installment", "trade-in"],
    "Technician appointment": ["appointment", "technician"],
    "Cancellation": ["cancel", "cancellation"],
    "Promotion or discount": ["promo", "promotion", "discount", "price"],
}

POSITIVE_WORDS = ["easy", "reliable", "helpful", "resolved", "finally", "good", "great"]
NEGATIVE_WORDS = [
    "down",
    "confusing",
    "never",
    "different answer",
    "wait",
    "cancel",
    "charge",
    "moved",
]


def analyze_feedback(record: RawFeedbackRecord) -> AnalysisResult:
    text = record.text.lower()
    company = record.company_hint or detect_company(text)
    product = record.product_hint or detect_product(text)
    topics = detect_topics(text)
    sentiment_score = score_sentiment(text)
    sentiment_label = label_sentiment(sentiment_score)
    emotion = detect_emotion(text, sentiment_score)
    root_causes = extract_root_causes(topics, text)

    return AnalysisResult(
        company=company,
        product=product,
        sentiment_label=sentiment_label,
        sentiment_score=sentiment_score,
        emotion=emotion,
        topics=topics,
        summary=summarize(record.text, topics),
        root_causes=root_causes,
        urgency_score=min(1.0, max(0.1, abs(sentiment_score) + (0.2 if "outage" in text else 0.0))),
        credibility_score=0.88 if record.source in {"Complaint Dataset", "App Store"} else 0.78,
        confidence=0.86 if company != "Unknown" and topics else 0.62,
    )


def detect_company(text: str) -> str:
    for company, aliases in COMPANY_ALIASES.items():
        if any(alias in text for alias in aliases):
            return company
    return "Unknown"


def detect_product(text: str) -> str | None:
    if "fiber" in text:
        return "Fiber"
    if "prepaid" in text:
        return "Prepaid"
    if "wireless" in text or "signal" in text or "calls" in text:
        return "Wireless"
    if "broadband" in text or "internet" in text:
        return "Broadband"
    return None


def detect_topics(text: str) -> list[str]:
    topics = [
        topic
        for topic, keywords in TOPIC_KEYWORDS.items()
        if any(keyword in text for keyword in keywords)
    ]
    return topics or ["Other"]


def score_sentiment(text: str) -> float:
    positive = sum(1 for word in POSITIVE_WORDS if word in text)
    negative = sum(1 for word in NEGATIVE_WORDS if word in text)
    raw = (positive - negative) / max(positive + negative, 1)
    return round(max(-1.0, min(1.0, raw * 0.85)), 2)


def label_sentiment(score: float) -> str:
    if score >= 0.65:
        return "Very positive"
    if score >= 0.2:
        return "Positive"
    if score <= -0.65:
        return "Very negative"
    if score <= -0.2:
        return "Negative"
    return "Neutral"


def detect_emotion(text: str, score: float) -> str:
    if "outage" in text or "down" in text:
        return "Urgency"
    if "confusing" in text:
        return "Confusion"
    if score > 0.2:
        return "Satisfaction"
    if "never" in text or "cancel" in text:
        return "Anger"
    return "Frustration" if score < 0 else "Neutral"


def extract_root_causes(topics: list[str], text: str) -> list[str]:
    causes: list[str] = []
    if "Billing" in topics:
        causes.append("Unexpected or unclear bill increase")
    if "Network outage" in topics:
        causes.append("Service outage or inaccurate outage communication")
    if "Technician appointment" in topics:
        causes.append("Delayed or rescheduled technician appointment")
    if "Promotion or discount" in topics and "confusing" in text:
        causes.append("Promotion terms not clear to customer")
    return causes


def summarize(text: str, topics: list[str]) -> str:
    topic_text = ", ".join(topics[:2])
    return f"{topic_text}: {text[:130].rstrip()}".strip()
