"""Tests for admin invite code management (Story 2.5)."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.admin.service import AdminService
from app.auth.models import InviteCode


def _make_service(db: AsyncMock) -> AdminService:
    return AdminService(db)


@pytest.mark.asyncio
async def test_create_invite_code() -> None:
    """Admin can create an invite code."""
    db = AsyncMock()
    service = _make_service(db)
    service.audit_repo.create = AsyncMock()

    # Mock flush + refresh to simulate DB behavior
    async def mock_flush() -> None:
        pass

    async def mock_refresh(obj: object) -> None:
        pass

    db.flush = mock_flush
    db.refresh = mock_refresh
    db.add = MagicMock()

    invite = await service.create_invite_code(
        admin_id=1, expiration_days=7, ip_address="127.0.0.1"
    )

    assert invite.code is not None
    assert len(invite.code) == 32  # hex(16) = 32 chars
    assert invite.created_by_id == 1
    db.commit.assert_awaited_once()
    service.audit_repo.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_invite_codes_with_status() -> None:
    """List returns codes with computed status."""
    db = AsyncMock()
    service = _make_service(db)

    now = datetime.now(UTC)
    unused = MagicMock(spec=InviteCode)
    unused.id = 1
    unused.code = "unused_code"
    unused.used_at = None
    unused.expires_at = now + timedelta(days=7)
    unused.created_at = now
    unused.used_by = None

    used = MagicMock(spec=InviteCode)
    used.id = 2
    used.code = "used_code"
    used.used_at = now
    used.expires_at = now + timedelta(days=7)
    used.created_at = now
    used.used_by = MagicMock(username="someuser")

    expired = MagicMock(spec=InviteCode)
    expired.id = 3
    expired.code = "expired_code"
    expired.used_at = None
    expired.expires_at = now - timedelta(days=1)
    expired.created_at = now - timedelta(days=8)
    expired.used_by = None

    service.invite_repo.get_all = AsyncMock(return_value=[unused, used, expired])

    result = await service.list_invite_codes()

    assert len(result) == 3
    assert result[0].status == "unused"
    assert result[1].status == "used"
    assert result[1].used_by_username == "someuser"
    assert result[2].status == "expired"
