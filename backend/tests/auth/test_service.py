"""Tests for auth service — registration logic (Story 2.1)."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.auth.models import InviteCode, User, UserStatus
from app.auth.schemas import RegisterRequest
from app.auth.service import AuthService
from app.core.exceptions import AppException


def _make_service(db: AsyncMock) -> AuthService:
    """Create AuthService with mocked DB session."""
    return AuthService(db)


def _make_invite(*, used: bool = False, expired: bool = False) -> InviteCode:
    """Create a mock InviteCode."""
    invite = MagicMock(spec=InviteCode)
    invite.id = 1
    invite.code = "VALID123"
    invite.used_at = datetime.now(UTC) if used else None
    invite.expires_at = (
        datetime.now(UTC) - timedelta(days=1)
        if expired
        else datetime.now(UTC) + timedelta(days=7)
    )
    return invite


@pytest.mark.asyncio
async def test_register_with_valid_invite() -> None:
    """Registration with valid invite code creates active user."""
    db = AsyncMock()
    service = _make_service(db)

    service.user_repo.get_by_username = AsyncMock(return_value=None)
    service.user_repo.get_by_email = AsyncMock(return_value=None)
    service.invite_repo.get_by_code = AsyncMock(return_value=_make_invite())
    service.invite_repo.mark_used = AsyncMock()

    created_user = MagicMock(spec=User)
    created_user.id = 1
    created_user.username = "testuser"
    created_user.email = "test@example.com"
    created_user.role = "member"
    created_user.status = UserStatus.ACTIVE
    service.user_repo.create = AsyncMock(return_value=created_user)

    data = RegisterRequest(
        username="testuser",
        email="test@example.com",
        password="securepass123",
        invite_code="VALID123",
    )
    user = await service.register(data)

    assert user.status == UserStatus.ACTIVE
    service.invite_repo.mark_used.assert_awaited_once()
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_register_duplicate_username_raises() -> None:
    """Duplicate username raises 409."""
    db = AsyncMock()
    service = _make_service(db)
    service.user_repo.get_by_username = AsyncMock(return_value=MagicMock(spec=User))

    data = RegisterRequest(
        username="taken", email="new@example.com", password="securepass123"
    )
    with pytest.raises(AppException) as exc_info:
        await service.register(data)
    assert exc_info.value.code == "AUTH_REGISTER_DUPLICATE"
    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_register_duplicate_email_raises() -> None:
    """Duplicate email raises 409."""
    db = AsyncMock()
    service = _make_service(db)
    service.user_repo.get_by_username = AsyncMock(return_value=None)
    service.user_repo.get_by_email = AsyncMock(return_value=MagicMock(spec=User))

    data = RegisterRequest(
        username="newuser", email="taken@example.com", password="securepass123"
    )
    with pytest.raises(AppException) as exc_info:
        await service.register(data)
    assert exc_info.value.code == "AUTH_REGISTER_DUPLICATE"


@pytest.mark.asyncio
async def test_register_expired_invite_raises() -> None:
    """Expired invite code raises 400."""
    db = AsyncMock()
    service = _make_service(db)
    service.user_repo.get_by_username = AsyncMock(return_value=None)
    service.user_repo.get_by_email = AsyncMock(return_value=None)
    service.invite_repo.get_by_code = AsyncMock(return_value=_make_invite(expired=True))

    data = RegisterRequest(
        username="newuser",
        email="new@example.com",
        password="securepass123",
        invite_code="EXPIRED",
    )
    with pytest.raises(AppException) as exc_info:
        await service.register(data)
    assert exc_info.value.code == "AUTH_REGISTER_INVALID_INVITE"


@pytest.mark.asyncio
async def test_register_used_invite_raises() -> None:
    """Already-used invite code raises 400."""
    db = AsyncMock()
    service = _make_service(db)
    service.user_repo.get_by_username = AsyncMock(return_value=None)
    service.user_repo.get_by_email = AsyncMock(return_value=None)
    service.invite_repo.get_by_code = AsyncMock(return_value=_make_invite(used=True))

    data = RegisterRequest(
        username="newuser",
        email="new@example.com",
        password="securepass123",
        invite_code="USED",
    )
    with pytest.raises(AppException) as exc_info:
        await service.register(data)
    assert exc_info.value.code == "AUTH_REGISTER_INVALID_INVITE"


@pytest.mark.asyncio
async def test_register_invalid_invite_code_raises() -> None:
    """Non-existent invite code raises 400."""
    db = AsyncMock()
    service = _make_service(db)
    service.user_repo.get_by_username = AsyncMock(return_value=None)
    service.user_repo.get_by_email = AsyncMock(return_value=None)
    service.invite_repo.get_by_code = AsyncMock(return_value=None)

    data = RegisterRequest(
        username="newuser",
        email="new@example.com",
        password="securepass123",
        invite_code="NONEXISTENT",
    )
    with pytest.raises(AppException) as exc_info:
        await service.register(data)
    assert exc_info.value.code == "AUTH_REGISTER_INVALID_INVITE"
