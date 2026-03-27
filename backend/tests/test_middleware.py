"""Tests for request ID middleware (Story 1.4)."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_response_has_request_id_header() -> None:
    """Response includes X-Request-ID header."""
    response = client.get("/health")
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 0


def test_request_id_propagated_from_header() -> None:
    """X-Request-ID from request is propagated to response."""
    custom_id = "test-request-id-12345"
    response = client.get("/health", headers={"X-Request-ID": custom_id})
    assert response.headers["X-Request-ID"] == custom_id


def test_request_id_generated_when_missing() -> None:
    """UUID is generated when X-Request-ID not in request."""
    response = client.get("/health")
    request_id = response.headers["X-Request-ID"]
    # UUID4 format: 8-4-4-4-12 hex chars
    parts = request_id.split("-")
    assert len(parts) == 5
