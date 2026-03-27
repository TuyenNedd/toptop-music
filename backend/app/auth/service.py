"""Service layer for auth module — business logic."""

import json
from datetime import UTC, datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import AuditLog, RefreshToken, User, UserRole, UserStatus
from app.auth.repository import (
    AuditLogRepository,
    InviteCodeRepository,
    RefreshTokenRepository,
    UserRepository,
)
from app.auth.schemas import RegisterRequest
from app.core.exceptions import AppException
from app.core.logging import get_logger
from app.core.redis import get_redis
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)

logger = get_logger(module="auth.service")


class AuthService:
    """Authentication and registration business logic."""

    def __init__(self, db: AsyncSession) -> None:
        self.user_repo = UserRepository(db)
        self.invite_repo = InviteCodeRepository(db)
        self.refresh_repo = RefreshTokenRepository(db)
        self.audit_repo = AuditLogRepository(db)
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

    async def _check_login_lockout(self, ip: str, username: str) -> None:
        """Check if login is locked out due to too many failed attempts."""
        try:
            redis = get_redis()
            key = f"login_attempts:{ip}:{username}"
            attempts = await redis.get(key)
            if attempts and int(attempts) >= 5:
                raise AppException(
                    code="AUTH_LOGIN_LOCKED",
                    message="Too many failed attempts. Try again in 15 minutes.",
                    status_code=429,
                )
        except RuntimeError:
            pass  # Redis not available — skip lockout check

    async def _record_failed_attempt(self, ip: str, username: str) -> None:
        """Increment failed login attempt counter in Redis."""
        try:
            redis = get_redis()
            key = f"login_attempts:{ip}:{username}"
            pipe = redis.pipeline()
            await pipe.incr(key)
            await pipe.expire(key, 900)  # 15 min TTL
            await pipe.execute()
        except RuntimeError:
            pass  # Redis not available — skip tracking

    async def _clear_login_attempts(self, ip: str, username: str) -> None:
        """Clear failed login attempts on successful login."""
        try:
            redis = get_redis()
            await redis.delete(f"login_attempts:{ip}:{username}")
        except RuntimeError:
            pass

    async def _log_audit(
        self, event_type: str, user_id: int | None, ip: str, details: dict[str, str]
    ) -> None:
        """Write an audit log entry."""
        audit = AuditLog(
            event_type=event_type,
            user_id=user_id,
            ip_address=ip,
            details=json.dumps(details),
        )
        await self.audit_repo.create(audit)

    async def login(
        self, username_or_email: str, password: str, ip_address: str
    ) -> tuple[str, str, datetime]:
        """Authenticate user and return (access_token, refresh_token, expires_at).

        Raises AppException for invalid credentials, locked accounts, pending status.
        """
        await self._check_login_lockout(ip_address, username_or_email)

        # Find user by username or email
        user = await self.user_repo.get_by_username(username_or_email)
        if not user:
            user = await self.user_repo.get_by_email(username_or_email)

        if not user or not verify_password(password, user.hashed_password):
            await self._record_failed_attempt(ip_address, username_or_email)
            await self._log_audit(
                "login_failed", None, ip_address, {"identifier": username_or_email}
            )
            await self.db.commit()
            raise AppException(
                code="AUTH_LOGIN_INVALID",
                message="Invalid credentials",
                status_code=401,
            )

        # Check account status
        if user.status == UserStatus.PENDING:
            await self._log_audit(
                "login_denied_pending", user.id, ip_address, {"username": user.username}
            )
            await self.db.commit()
            raise AppException(
                code="AUTH_LOGIN_PENDING",
                message="Account pending approval",
                status_code=403,
            )

        if user.status != UserStatus.ACTIVE:
            await self._log_audit(
                "login_denied_inactive",
                user.id,
                ip_address,
                {"username": user.username},
            )
            await self.db.commit()
            raise AppException(
                code="AUTH_LOGIN_INACTIVE",
                message="Account is not active",
                status_code=403,
            )

        # Generate tokens
        access_token = create_access_token(user.id, user.role)
        refresh_token_str = create_refresh_token()
        expires_at = datetime.now(UTC) + timedelta(days=7)

        # Store refresh token
        rt = RefreshToken(
            token=refresh_token_str,
            user_id=user.id,
            expires_at=expires_at,
        )
        await self.refresh_repo.create(rt)

        # Clear failed attempts and log success
        await self._clear_login_attempts(ip_address, username_or_email)
        await self._log_audit(
            "login_success", user.id, ip_address, {"username": user.username}
        )
        await self.db.commit()

        logger.info("user_logged_in", user_id=user.id, username=user.username)

        return access_token, refresh_token_str, expires_at
