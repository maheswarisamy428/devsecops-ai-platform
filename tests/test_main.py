"""Tests for the main.py file."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    """Test the health endpoint."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_metadata():
    """Test the metadata endpoint."""
    response = client.get("/metadata")

    assert response.status_code == 200

    data = response.json()

    assert data["service"] == "bytespoke-assistant"


def test_metrics():
    """Test the metrics endpoint."""
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "http_request_total" in response.text
