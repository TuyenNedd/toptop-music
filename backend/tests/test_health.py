"""Tests for health endpoint and app configuration."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint_returns_ok() -> None:
    """Health endpoint returns standard envelope with status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data == {"data": {"status": "ok"}, "error": None}


def test_health_endpoint_envelope_format() -> None:
    """Health endpoint response has data and error keys."""
    response = client.get("/health")
    data = response.json()
    assert "data" in data
    assert "error" in data
    assert data["error"] is None
