"""Repository layer for auth module — database queries."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import AuditLog, InviteCode, RefreshToken, User


class UserRepository:
    """Database operations for User model."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_username(self, username: str) -> User | None:
        """Find user by username."""
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        """Find user by ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Find user by email."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        """Insert a new user and return it with generated id."""
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def get_by_status(self, status: str) -> list[User]:
        """Get all users with a given status."""
        result = await self.db.execute(
            select(User).where(User.status == status).order_by(User.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_status(self, user: User, new_status: str) -> User:
        """Update user status."""
        user.status = new_status
        await self.db.flush()
        await self.db.refresh(user)
        return user


class InviteCodeRepository:
    """Database operations for InviteCode model."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_code(self, code: str) -> InviteCode | None:
        """Find invite code by code string."""
        result = await self.db.execute(
            select(InviteCode).where(InviteCode.code == code)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[InviteCode]:
        """Get all invite codes ordered by created_at desc."""
        result = await self.db.execute(
            select(InviteCode).order_by(InviteCode.created_at.desc())
        )
        return list(result.scalars().all())

    async def mark_used(self, invite: InviteCode, user_id: int) -> None:
        """Mark an invite code as used by a user."""
        invite.used_by_id = user_id
        invite.used_at = datetime.now(UTC)
        await self.db.flush()


class RefreshTokenRepository:
    """Database operations for RefreshToken model."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, refresh_token: RefreshToken) -> RefreshToken:
        """Store a new refresh token."""
        self.db.add(refresh_token)
        await self.db.flush()
        return refresh_token

    async def get_by_token(self, token: str) -> RefreshToken | None:
        """Find refresh token by token string."""
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.token == token, RefreshToken.revoked == False  # noqa: E712
            )
        )
        return result.scalar_one_or_none()

    async def revoke(self, refresh_token: RefreshToken) -> None:
        """Revoke a refresh token."""
        refresh_token.revoked = True
        await self.db.flush()


class AuditLogRepository:
    """Database operations for AuditLog model."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, audit_log: AuditLog) -> None:
        """Store an audit log entry."""
        self.db.add(audit_log)
        await self.db.flush()
