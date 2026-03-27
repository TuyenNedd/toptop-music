"""Tests for admin user management (Story 2.6)."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.admin.service import AdminService
from app.auth.models import User, UserStatus
from app.core.exceptions import AppException


def _make_service(db: AsyncMock) -> AdminService:
    return AdminService(db)


def _make_pending_user() -> MagicMock:
    user = MagicMock(spec=User)
    user.id = 2
    user.username = "pendinguser"
    user.email = "pending@example.com"
    user.role = "member"
    user.status = UserStatus.PENDING
    return user


@pytest.mark.asyncio
async def test_update_user_status_approve() -> None:
    """Admin can approve a pending user."""
    db = AsyncMock()
    service = _make_service(db)
    service.audit_repo.create = AsyncMock()

    user = _make_pending_user()
    approved_user = MagicMock(spec=User)
    approved_user.id = 2
    approved_user.username = "pendinguser"
    approved_user.email = "pending@example.com"
    approved_user.role = "member"
    approved_user.status = "active"
    approved_user.created_at = user.created_at

    from app.auth.repository import UserRepository

    with (pytest.MonkeyPatch.context() as mp,):
        mp.setattr(UserRepository, "get_by_id", AsyncMock(return_value=user))
        mp.setattr(
            UserRepository, "update_status", AsyncMock(return_value=approved_user)
        )

        result = await service.update_user_status(2, "active", 1, "127.0.0.1")

    assert result.status == "active"
    service.audit_repo.create.assert_awaited_once()
    db.commit.assert_awaited()


@pytest.mark.asyncio
async def test_update_user_status_not_found() -> None:
    """Updating non-existent user raises 404."""
    db = AsyncMock()
    service = _make_service(db)

    from app.auth.repository import UserRepository

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(UserRepository, "get_by_id", AsyncMock(return_value=None))

        with pytest.raises(AppException) as exc_info:
            await service.update_user_status(999, "active", 1, "127.0.0.1")
        assert exc_info.value.status_code == 404
