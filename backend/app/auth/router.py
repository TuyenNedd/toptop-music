"""Auth module router — registration, login, token endpoints."""

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import RegisterRequest, UserResponse
from app.auth.service import AuthService
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
