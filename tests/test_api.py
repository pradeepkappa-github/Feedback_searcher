from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_feedback_endpoint_returns_analyzed_records():
    response = client.get("/api/feedback")

    assert response.status_code == 200
    records = response.json()
    assert records
    assert "analysis" in records[0]


def test_assistant_returns_grounded_answer():
    response = client.post(
        "/api/assistant/ask",
        json={"question": "Why did AT&T sentiment decline?", "company": "AT&T", "days": 7},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["records_analyzed"] >= 1
    assert payload["supporting_record_ids"]


def test_assistant_explains_post_definition():
    response = client.post(
        "/api/assistant/ask",
        json={"question": "what is post", "company": "AT&T", "days": 7},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "collected public feedback item" in payload["answer"]
    assert payload["confidence"] >= 0.9


def test_assistant_can_show_example_posts():
    response = client.post(
        "/api/assistant/ask",
        json={"question": "show me post examples", "company": "AT&T", "days": 7},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "example posts" in payload["answer"]
    assert payload["supporting_record_ids"]
