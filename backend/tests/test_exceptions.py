"""Tests for core exception handling (Story 1.4)."""


from fastapi.testclient import TestClient

from app.core.exceptions import AppException
from app.main import app


def test_app_exception_returns_error_envelope() -> None:
    """AppException is caught and returns structured error envelope."""

    @app.get("/test-app-exception")
    async def _raise_app_exception() -> None:
        raise AppException(
            code="TEST_ERROR", message="Test error message", status_code=400
        )

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/test-app-exception")
    assert response.status_code == 400
    data = response.json()
    assert data["data"] is None
    assert data["error"]["code"] == "TEST_ERROR"
    assert data["error"]["message"] == "Test error message"


def test_unhandled_exception_returns_500() -> None:
    """Unhandled exceptions return 500 with generic message."""

    @app.get("/test-unhandled-exception")
    async def _raise_unhandled() -> None:
        raise RuntimeError("Something unexpected")

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/test-unhandled-exception")
    assert response.status_code == 500
    data = response.json()
    assert data["data"] is None
    assert data["error"]["code"] == "INTERNAL_ERROR"
    assert data["error"]["message"] == "An unexpected error occurred"


def test_app_exception_class_attributes() -> None:
    """AppException stores code, message, status_code."""
    exc = AppException(code="AUTH_DENIED", message="Access denied", status_code=403)
    assert exc.code == "AUTH_DENIED"
    assert exc.message == "Access denied"
    assert exc.status_code == 403
    assert str(exc) == "Access denied"
