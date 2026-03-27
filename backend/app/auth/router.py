"""Auth module router — registration, login, token endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.auth.service import AuthService
from app.config import settings
from app.database import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", status_code=201)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Register a new user account."""
    service = AuthService(db)
    user = await service.register(data)
    return {"data": UserResponse.model_validate(user).model_dump(), "error": None}


@router.post("/login")
async def login(
    data: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Authenticate user and return JWT access token."""
    ip = request.client.host if request.client else "unknown"
    service = AuthService(db)
    access_token, refresh_token, expires_at = await service.login(
        data.username_or_email, data.password, ip
    )

    # Set refresh token as httpOnly secure cookie
    # secure=False in dev (HTTP), True in production (HTTPS)
    is_production = not settings.JWT_SECRET_KEY.startswith("dev-")
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=is_production,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,  # 7 days
        path="/api/auth",
    )

    token_data = TokenResponse(access_token=access_token)
    return {"data": token_data.model_dump(), "error": None}


def _is_production() -> bool:
    return not settings.JWT_SECRET_KEY.startswith("dev-")


@router.post("/refresh")
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Refresh access token using refresh token cookie."""
    token_str = request.cookies.get("refresh_token")
    if not token_str:
        from app.core.exceptions import AppException

        raise AppException(
            code="AUTH_REFRESH_MISSING",
            message="No refresh token provided",
            status_code=401,
        )

    service = AuthService(db)
    access_token, new_refresh, expires_at = await service.refresh_token(token_str)

    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=_is_production(),
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
        path="/api/auth",
    )

    token_data = TokenResponse(access_token=access_token)
    return {"data": token_data.model_dump(), "error": None}


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Logout — revoke refresh token and clear cookie."""
    token_str = request.cookies.get("refresh_token")
    ip = request.client.host if request.client else "unknown"

    if token_str:
        service = AuthService(db)
        await service.logout(token_str, ip)

    response.delete_cookie(
        key="refresh_token",
        path="/api/auth",
        httponly=True,
        secure=_is_production(),
        samesite="lax",
    )

    return {"data": {"message": "Logged out successfully"}, "error": None}
