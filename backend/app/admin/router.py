"""Admin module router — invite codes, user management, system health."""

from typing import Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.schemas import InviteCodeCreateRequest
from app.admin.service import AdminService
from app.auth.dependencies import require_role
from app.auth.models import User
from app.database import get_db

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/invite-codes", status_code=201)
async def create_invite_code(
    data: InviteCodeCreateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Generate a new invite code (admin only)."""
    ip = request.client.host if request.client else "unknown"
    service = AdminService(db)
    invite = await service.create_invite_code(
        admin_id=current_user.id,
        expiration_days=data.expiration_days,
        ip_address=ip,
    )
    return {
        "data": {"code": invite.code, "expires_at": invite.expires_at.isoformat()},
        "error": None,
    }


@router.get("/invite-codes")
async def list_invite_codes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict[str, Any]:
    """List all invite codes with status (admin only)."""
    service = AdminService(db)
    codes = await service.list_invite_codes()
    return {
        "data": [c.model_dump() for c in codes],
        "error": None,
    }


@router.get("/users")
async def list_users(
    status: str = "pending",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict[str, Any]:
    """List users filtered by status (admin only)."""
    service = AdminService(db)
    users = await service.list_users_by_status(status)
    return {"data": [u.model_dump() for u in users], "error": None}


@router.put("/users/{user_id}/approve")
async def approve_user(
    user_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Approve a pending user (admin only)."""
    ip = request.client.host if request.client else "unknown"
    service = AdminService(db)
    user = await service.update_user_status(user_id, "active", current_user.id, ip)
    return {"data": user.model_dump(), "error": None}


@router.put("/users/{user_id}/reject")
async def reject_user(
    user_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Reject a pending user (admin only)."""
    ip = request.client.host if request.client else "unknown"
    service = AdminService(db)
    user = await service.update_user_status(user_id, "rejected", current_user.id, ip)
    return {"data": user.model_dump(), "error": None}


@router.put("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Deactivate an active user (admin only)."""
    ip = request.client.host if request.client else "unknown"
    service = AdminService(db)
    user = await service.update_user_status(user_id, "inactive", current_user.id, ip)
    return {"data": user.model_dump(), "error": None}


@router.put("/users/{user_id}/reactivate")
async def reactivate_user(
    user_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Reactivate an inactive user (admin only)."""
    ip = request.client.host if request.client else "unknown"
    service = AdminService(db)
    user = await service.update_user_status(user_id, "active", current_user.id, ip)
    return {"data": user.model_dump(), "error": None}
