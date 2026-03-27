"""Repository layer for auth module — database queries."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import InviteCode, User


class UserRepository:
    """Database operations for User model."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_username(self, username: str) -> User | None:
        """Find user by username."""
        result = await self.db.execute(select(User).where(User.username == username))
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

    async def mark_used(self, invite: InviteCode, user_id: int) -> None:
        """Mark an invite code as used by a user."""
        invite.used_by_id = user_id
        invite.used_at = datetime.now(UTC)
        await self.db.flush()
