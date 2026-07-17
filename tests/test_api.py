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
        json={"question": "show me post examples which date it is", "company": "AT&T", "days": 7},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "example posts" in payload["answer"]
    assert "publication dates" in payload["answer"]
    assert "2026-07-" in payload["answer"]
    assert payload["supporting_record_ids"]


def test_assistant_returns_reddit_post_details():
    response = client.post(
        "/api/assistant/ask",
        json={
            "question": "what is post in reddit and provide the all the details of post",
            "company": "AT&T",
            "days": 7,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "available live Reddit post details" in payload["answer"]
    assert "example.com" not in payload["answer"]
    assert (
        "published" in payload["answer"]
        or "Run live Reddit collection first" in payload["answer"]
    )
    assert (
        "author:" in payload["answer"]
        or "Run live Reddit collection first" in payload["answer"]
    )


def test_assistant_explains_reddit_post_with_live_details():
    response = client.post(
        "/api/assistant/ask",
        json={
            "question": "what is post in reddit and explain the post",
            "company": "AT&T",
            "days": 7,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "available live Reddit post details" in payload["answer"]
    assert "collected public feedback item" not in payload["answer"]
    assert "example.com" not in payload["answer"]
