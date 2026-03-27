"""Service layer for admin module."""

import json
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.schemas import AdminUserResponse, InviteCodeResponse
from app.auth.models import AuditLog, InviteCode
from app.auth.repository import AuditLogRepository, InviteCodeRepository, UserRepository
from app.core.exceptions import AppException
from app.core.logging import get_logger

logger = get_logger(module="admin.service")


class AdminService:
    """Admin business logic — invite codes, user management."""

    def __init__(self, db: AsyncSession) -> None:
        self.invite_repo = InviteCodeRepository(db)
        self.audit_repo = AuditLogRepository(db)
        self.db = db

    async def create_invite_code(
        self, admin_id: int, expiration_days: int, ip_address: str
    ) -> InviteCode:
        """Generate a new invite code."""
        code = secrets.token_hex(16)
        expires_at = datetime.now(UTC) + timedelta(days=expiration_days)

        invite = InviteCode(
            code=code,
            created_by_id=admin_id,
            expires_at=expires_at,
        )
        self.db.add(invite)
        await self.db.flush()
        await self.db.refresh(invite)

        # Audit log
        audit = AuditLog(
            event_type="invite_code_created",
            user_id=admin_id,
            ip_address=ip_address,
            details=json.dumps({"code": code, "expiration_days": expiration_days}),
        )
        await self.audit_repo.create(audit)
        await self.db.commit()

        logger.info("invite_code_created", admin_id=admin_id, code=code)
        return invite

    async def list_invite_codes(self) -> list[InviteCodeResponse]:
        """List all invite codes with computed status."""
        codes = await self.invite_repo.get_all()
        now = datetime.now(UTC)
        result: list[InviteCodeResponse] = []

        for c in codes:
            if c.used_at is not None:
                status = "used"
            elif c.expires_at.replace(tzinfo=UTC) < now:
                status = "expired"
            else:
                status = "unused"

            result.append(
                InviteCodeResponse(
                    id=c.id,
                    code=c.code,
                    status=status,
                    created_at=c.created_at,
                    expires_at=c.expires_at,
                    used_by_username=c.used_by.username if c.used_by else None,
                )
            )

        return result

    async def list_users_by_status(self, status: str) -> list[AdminUserResponse]:
        """List users filtered by status."""
        user_repo = UserRepository(self.db)
        users = await user_repo.get_by_status(status)
        return [AdminUserResponse.model_validate(u) for u in users]

    async def update_user_status(
        self, user_id: int, new_status: str, admin_id: int, ip_address: str
    ) -> AdminUserResponse:
        """Update a user's status (approve/reject/deactivate/reactivate)."""
        user_repo = UserRepository(self.db)
        user = await user_repo.get_by_id(user_id)
        if not user:
            raise AppException(
                code="ADMIN_USER_NOT_FOUND",
                message="User not found",
                status_code=404,
            )

        old_status = user.status
        user = await user_repo.update_status(user, new_status)

        # Audit log
        audit = AuditLog(
            event_type="user_status_changed",
            user_id=admin_id,
            ip_address=ip_address,
            details=json.dumps(
                {
                    "target_user_id": user_id,
                    "old_status": old_status,
                    "new_status": new_status,
                }
            ),
        )
        await self.audit_repo.create(audit)
        await self.db.commit()

        logger.info(
            "user_status_changed",
            admin_id=admin_id,
            target_user_id=user_id,
            old_status=old_status,
            new_status=new_status,
        )

        return AdminUserResponse.model_validate(user)
