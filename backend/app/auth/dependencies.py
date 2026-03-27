"""Auth dependencies for FastAPI — JWT extraction and RBAC."""

from typing import Any

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.repository import UserRepository
from app.core.exceptions import AppException
from app.core.security import decode_access_token
from app.database import get_db

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate JWT token, return current user."""
    try:
        payload = decode_access_token(credentials.credentials)
    except JWTError:
        raise AppException(
            code="AUTH_INVALID_TOKEN",
            message="Invalid or expired token",
            status_code=401,
        )

    user_id_str = payload.get("sub")
    if not user_id_str or not isinstance(user_id_str, str):
        raise AppException(
            code="AUTH_INVALID_TOKEN",
            message="Invalid token payload",
            status_code=401,
        )

    repo = UserRepository(db)
    user = await repo.get_by_id(int(user_id_str))
    if not user:
        raise AppException(
            code="AUTH_USER_NOT_FOUND",
            message="User not found",
            status_code=401,
        )

    if user.status != "active":
        raise AppException(
            code="AUTH_ACCOUNT_INACTIVE",
            message="Account is not active",
            status_code=403,
        )

    return user


def require_role(role: str) -> Any:
    """Factory that returns a dependency checking user has the required role."""

    async def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role != role:
            raise AppException(
                code="AUTH_FORBIDDEN",
                message="Insufficient permissions",
                status_code=403,
            )
        return current_user

    return role_checker
