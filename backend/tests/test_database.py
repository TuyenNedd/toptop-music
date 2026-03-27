"""Tests for database module (Story 1.3)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal, Base, get_db


def test_base_is_declarative_base() -> None:
    """Base class is a DeclarativeBase for all models."""
    assert hasattr(Base, "metadata")
    assert hasattr(Base, "registry")


def test_async_session_local_configured() -> None:
    """AsyncSessionLocal is configured with expire_on_commit=False."""
    kw = AsyncSessionLocal.kw
    assert kw.get("expire_on_commit") is False


@pytest.mark.asyncio
async def test_get_db_yields_session() -> None:
    """get_db yields an AsyncSession."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_context = MagicMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_session)
    mock_context.__aexit__ = AsyncMock(return_value=None)

    with patch("app.database.AsyncSessionLocal", return_value=mock_context):
        gen = get_db()
        session = await gen.__anext__()
        assert session is mock_session
