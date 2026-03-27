"""Tests for token refresh and logout (Story 2.4)."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.auth.models import RefreshToken, User, UserStatus
from app.auth.service import AuthService
from app.core.exceptions import AppException


def _make_service(db: AsyncMock) -> AuthService:
    return AuthService(db)


def _make_valid_rt() -> MagicMock:
    rt = MagicMock(spec=RefreshToken)
    rt.token = "valid_token"
    rt.user_id = 1
    rt.revoked = False
    rt.expires_at = datetime.now(UTC) + timedelta(days=7)
    return rt


def _make_expired_rt() -> MagicMock:
    rt = _make_valid_rt()
    rt.expires_at = datetime.now(UTC) - timedelta(days=1)
    return rt


def _make_active_user() -> MagicMock:
    user = MagicMock(spec=User)
    user.id = 1
    user.username = "testuser"
    user.role = "member"
    user.status = UserStatus.ACTIVE
    return user


@pytest.mark.asyncio
@patch("app.auth.service.create_access_token", return_value="new_access")
@patch("app.auth.service.create_refresh_token", return_value="new_refresh")
async def test_refresh_success(_mock_rt: MagicMock, _mock_at: MagicMock) -> None:
    """Valid refresh token returns new tokens."""
    db = AsyncMock()
    service = _make_service(db)
    service.refresh_repo.get_by_token = AsyncMock(return_value=_make_valid_rt())
    service.refresh_repo.revoke = AsyncMock()
    service.refresh_repo.create = AsyncMock()
    service.user_repo.get_by_id = AsyncMock(return_value=_make_active_user())

    access, refresh, expires = await service.refresh_token("valid_token")

    assert access == "new_access"
    assert refresh == "new_refresh"
    service.refresh_repo.revoke.assert_awaited_once()
    service.refresh_repo.create.assert_awaited_once()
    db.commit.assert_awaited()


@pytest.mark.asyncio
async def test_refresh_invalid_token_raises() -> None:
    """Invalid/revoked refresh token raises 401."""
    db = AsyncMock()
    service = _make_service(db)
    service.refresh_repo.get_by_token = AsyncMock(return_value=None)

    with pytest.raises(AppException) as exc_info:
        await service.refresh_token("bad_token")
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_refresh_expired_token_raises() -> None:
    """Expired refresh token raises 401."""
    db = AsyncMock()
    service = _make_service(db)
    service.refresh_repo.get_by_token = AsyncMock(return_value=_make_expired_rt())
    service.refresh_repo.revoke = AsyncMock()

    with pytest.raises(AppException) as exc_info:
        await service.refresh_token("expired_token")
    assert exc_info.value.code == "AUTH_REFRESH_EXPIRED"


@pytest.mark.asyncio
async def test_logout_revokes_token() -> None:
    """Logout revokes the refresh token and logs audit."""
    db = AsyncMock()
    service = _make_service(db)
    service.refresh_repo.get_by_token = AsyncMock(return_value=_make_valid_rt())
    service.refresh_repo.revoke = AsyncMock()
    service.audit_repo.create = AsyncMock()

    await service.logout("valid_token", "127.0.0.1")

    service.refresh_repo.revoke.assert_awaited_once()
    service.audit_repo.create.assert_awaited_once()
    db.commit.assert_awaited()


@pytest.mark.asyncio
async def test_logout_no_token_is_noop() -> None:
    """Logout with no matching token is a no-op."""
    db = AsyncMock()
    service = _make_service(db)
    service.refresh_repo.get_by_token = AsyncMock(return_value=None)

    await service.logout("nonexistent", "127.0.0.1")
    # Should not raise, just silently succeed
