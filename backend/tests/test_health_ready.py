"""Tests for /health/ready endpoint (Story 1.3)."""

from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.main import app


def _make_db_dependency(
    mock_session: AsyncMock,
) -> Any:
    """Override get_db dependency with a mock session."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, Any]:
        yield mock_session

    return override_get_db


def test_health_ready_db_connected() -> None:
    """health/ready returns 200 when DB is reachable."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute = AsyncMock(return_value=None)

    app.dependency_overrides[get_db] = _make_db_dependency(mock_session)

    try:
        client = TestClient(app)
        response = client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["status"] == "ok"
        assert data["data"]["database"] == "connected"
        assert data["error"] is None
    finally:
        app.dependency_overrides.clear()


def test_health_ready_db_unavailable() -> None:
    """health/ready returns 503 when DB is unreachable."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute = AsyncMock(side_effect=Exception("Connection refused"))

    app.dependency_overrides[get_db] = _make_db_dependency(mock_session)

    try:
        client = TestClient(app)
        response = client.get("/health/ready")
        assert response.status_code == 503
        data = response.json()
        assert data["data"] is None
        assert data["error"]["code"] == "DB_UNAVAILABLE"
        assert data["error"]["message"] == "Database connection failed"
    finally:
        app.dependency_overrides.clear()
