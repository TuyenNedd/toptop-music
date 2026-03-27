"""Tests for /health/ready endpoint (Story 1.3, updated Story 1.4)."""

from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, patch

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


def _mock_redis_ok() -> AsyncMock:
    """Create a mock Redis client that responds to ping."""
    mock = AsyncMock()
    mock.ping = AsyncMock(return_value=True)
    return mock


def test_health_ready_all_connected() -> None:
    """health/ready returns 200 when DB and Redis are reachable."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute = AsyncMock(return_value=None)

    app.dependency_overrides[get_db] = _make_db_dependency(mock_session)

    with patch("app.main.get_redis", return_value=_mock_redis_ok()):
        try:
            client = TestClient(app)
            response = client.get("/health/ready")
            assert response.status_code == 200
            data = response.json()
            assert data["data"]["status"] == "ok"
            assert data["data"]["database"] == "connected"
            assert data["data"]["redis"] == "connected"
            assert data["error"] is None
        finally:
            app.dependency_overrides.clear()


def test_health_ready_db_unavailable() -> None:
    """health/ready returns 503 when DB is unreachable."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute = AsyncMock(side_effect=Exception("Connection refused"))

    app.dependency_overrides[get_db] = _make_db_dependency(mock_session)

    with patch("app.main.get_redis", return_value=_mock_redis_ok()):
        try:
            client = TestClient(app)
            response = client.get("/health/ready")
            assert response.status_code == 503
            data = response.json()
            assert data["data"] is None
            assert data["error"]["code"] == "SERVICE_UNAVAILABLE"
            assert "database" in data["error"]["message"]
        finally:
            app.dependency_overrides.clear()


def test_health_ready_redis_unavailable() -> None:
    """health/ready returns 503 when Redis is unreachable."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute = AsyncMock(return_value=None)

    app.dependency_overrides[get_db] = _make_db_dependency(mock_session)

    with patch("app.main.get_redis", side_effect=RuntimeError("Redis not initialized")):
        try:
            client = TestClient(app)
            response = client.get("/health/ready")
            assert response.status_code == 503
            data = response.json()
            assert data["data"] is None
            assert "redis" in data["error"]["message"]
        finally:
            app.dependency_overrides.clear()
