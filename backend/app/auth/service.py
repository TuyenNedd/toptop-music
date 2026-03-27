"""Service layer for auth module — business logic."""

from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User, UserRole, UserStatus
from app.auth.repository import InviteCodeRepository, UserRepository
from app.auth.schemas import RegisterRequest
from app.core.exceptions import AppException
from app.core.logging import get_logger
from app.core.security import hash_password

logger = get_logger(module="auth.service")


class AuthService:
    """Authentication and registration business logic."""

    def __init__(self, db: AsyncSession) -> None:
        self.user_repo = UserRepository(db)
        self.invite_repo = InviteCodeRepository(db)
        self.db = db

    async def register(self, data: RegisterRequest) -> User:
        """Register a new user. With invite code = active, without = pending."""
        # Check duplicate username
        if await self.user_repo.get_by_username(data.username):
            raise AppException(
                code="AUTH_REGISTER_DUPLICATE",
                message="Username or email is already registered",
                status_code=409,
            )

        # Check duplicate email
        if await self.user_repo.get_by_email(data.email):
            raise AppException(
                code="AUTH_REGISTER_DUPLICATE",
                message="Username or email is already registered",
                status_code=409,
            )

        # Determine status based on invite code
        status = UserStatus.PENDING
        invite = None

        if data.invite_code:
            invite = await self.invite_repo.get_by_code(data.invite_code)
            if not invite:
                raise AppException(
                    code="AUTH_REGISTER_INVALID_INVITE",
                    message="Invalid invite code",
                    status_code=400,
                )
            if invite.used_at is not None:
                raise AppException(
                    code="AUTH_REGISTER_INVALID_INVITE",
                    message="Invite code has already been used",
                    status_code=400,
                )
            if invite.expires_at.replace(tzinfo=UTC) < datetime.now(UTC):
                raise AppException(
                    code="AUTH_REGISTER_INVALID_INVITE",
                    message="Invite code has expired",
                    status_code=400,
                )
            status = UserStatus.ACTIVE

        # Create user
        user = User(
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password),
            role=UserRole.MEMBER,
            status=status,
        )
        try:
            user = await self.user_repo.create(user)
        except IntegrityError:
            await self.db.rollback()
            raise AppException(
                code="AUTH_REGISTER_DUPLICATE",
                message="Username or email is already registered",
                status_code=409,
            )

        # Mark invite code as used
        if invite:
            await self.invite_repo.mark_used(invite, user.id)

        await self.db.commit()

        logger.info(
            "user_registered",
            user_id=user.id,
            username=user.username,
            status=user.status,
            has_invite=data.invite_code is not None,
        )

        return user
