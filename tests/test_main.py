from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_metadata():
    response = client.get("/metadata")

    assert response.status_code == 200

    data = response.json()

    assert data["service"] == "bytespoke-assistant"


def test_metrics():
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "http_request_total" in response.text