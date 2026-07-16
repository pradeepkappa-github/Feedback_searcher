from connectors.sample_dataset.connector import SampleDatasetConnector
from services.ai_analysis.classifier import analyze_feedback


def test_classifier_detects_billing_and_negative_sentiment():
    record = SampleDatasetConnector().collect()[1]

    analysis = analyze_feedback(record)

    assert analysis.company == "AT&T"
    assert "Billing" in analysis.topics
    assert analysis.sentiment_score < 0
    assert analysis.confidence >= 0.8


def test_classifier_detects_positive_verizon_feedback():
    record = SampleDatasetConnector().collect()[2]

    analysis = analyze_feedback(record)

    assert analysis.company == "Verizon"
    assert analysis.sentiment_label in {"Positive", "Very positive"}
    assert "Coverage" in analysis.topics
