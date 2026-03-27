"""Tests for login service logic (Story 2.3)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.auth.models import User, UserStatus
from app.auth.service import AuthService
from app.core.exceptions import AppException


def _make_active_user() -> MagicMock:
    """Create a mock active user."""
    user = MagicMock(spec=User)
    user.id = 1
    user.username = "testuser"
    user.email = "test@example.com"
    user.hashed_password = "hashed"
    user.role = "member"
    user.status = UserStatus.ACTIVE
    return user


def _make_pending_user() -> MagicMock:
    """Create a mock pending user."""
    user = _make_active_user()
    user.status = UserStatus.PENDING
    return user


def _make_service(db: AsyncMock) -> AuthService:
    return AuthService(db)


@pytest.mark.asyncio
@patch("app.auth.service.verify_password", return_value=True)
@patch("app.auth.service.create_access_token", return_value="access.jwt.token")
@patch("app.auth.service.create_refresh_token", return_value="refresh_token_str")
async def test_login_success(
    _mock_rt: MagicMock, _mock_at: MagicMock, _mock_verify: MagicMock
) -> None:
    """Successful login returns access token and refresh token."""
    db = AsyncMock()
    service = _make_service(db)
    service.user_repo.get_by_username = AsyncMock(return_value=_make_active_user())
    service.refresh_repo.create = AsyncMock()
    service.audit_repo.create = AsyncMock()

    access, refresh, expires = await service.login("testuser", "password", "127.0.0.1")

    assert access == "access.jwt.token"
    assert refresh == "refresh_token_str"
    service.refresh_repo.create.assert_awaited_once()
    db.commit.assert_awaited()


@pytest.mark.asyncio
@patch("app.auth.service.verify_password", return_value=False)
async def test_login_invalid_credentials(_mock_verify: MagicMock) -> None:
    """Invalid credentials raises 401."""
    db = AsyncMock()
    service = _make_service(db)
    service.user_repo.get_by_username = AsyncMock(return_value=_make_active_user())
    service.audit_repo.create = AsyncMock()

    with pytest.raises(AppException) as exc_info:
        await service.login("testuser", "wrongpass", "127.0.0.1")
    assert exc_info.value.code == "AUTH_LOGIN_INVALID"
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_login_user_not_found() -> None:
    """Non-existent user raises 401."""
    db = AsyncMock()
    service = _make_service(db)
    service.user_repo.get_by_username = AsyncMock(return_value=None)
    service.user_repo.get_by_email = AsyncMock(return_value=None)
    service.audit_repo.create = AsyncMock()

    with pytest.raises(AppException) as exc_info:
        await service.login("nobody", "password", "127.0.0.1")
    assert exc_info.value.code == "AUTH_LOGIN_INVALID"


@pytest.mark.asyncio
@patch("app.auth.service.verify_password", return_value=True)
async def test_login_pending_user_raises_403(_mock_verify: MagicMock) -> None:
    """Pending user gets 403."""
    db = AsyncMock()
    service = _make_service(db)
    service.user_repo.get_by_username = AsyncMock(return_value=_make_pending_user())
    service.audit_repo.create = AsyncMock()

    with pytest.raises(AppException) as exc_info:
        await service.login("testuser", "password", "127.0.0.1")
    assert exc_info.value.code == "AUTH_LOGIN_PENDING"
    assert exc_info.value.status_code == 403
    assert "pending" in exc_info.value.message.lower()
