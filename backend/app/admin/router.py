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


@router.get("/dashboard")
async def admin_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Admin dashboard — system health, user stats, cache stats, scraper status."""
    import json

    from sqlalchemy import func as sa_func
    from sqlalchemy import select

    # User stats
    from app.auth.models import User as UserModel
    from app.sounds.models import Sound

    total_users = (
        await db.execute(select(sa_func.count()).select_from(UserModel))
    ).scalar_one()
    pending_users = (
        await db.execute(
            select(sa_func.count())
            .select_from(UserModel)
            .where(UserModel.status == "pending")
        )
    ).scalar_one()

    # Sound stats
    total_sounds = (
        await db.execute(select(sa_func.count()).select_from(Sound))
    ).scalar_one()
    cached_sounds = (
        await db.execute(
            select(sa_func.count())
            .select_from(Sound)
            .where(Sound.cached == True)  # noqa: E712
        )
    ).scalar_one()

    # Scraper status from Redis
    scraper_status = None
    cache_stats = None
    try:
        from app.core.redis import get_redis

        redis = get_redis()
        raw = await redis.get("fetcher:status")
        if raw:
            scraper_status = json.loads(raw)
        raw_cache = await redis.get("cache:stats")
        if raw_cache:
            cache_stats = json.loads(raw_cache)
    except RuntimeError:
        pass

    return {
        "data": {
            "users": {"total": total_users, "pending": pending_users},
            "sounds": {"total": total_sounds, "cached": cached_sounds},
            "scraper": scraper_status,
            "cache": cache_stats,
        },
        "error": None,
    }


@router.get("/audit-logs")
async def get_audit_logs(
    event_type: str | None = None,
    user_id: int | None = None,
    page: int = 1,
    page_size: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict[str, Any]:
    """View audit logs with optional filters."""
    from sqlalchemy import func as sa_func
    from sqlalchemy import select

    from app.auth.models import AuditLog

    query = select(AuditLog)
    count_query = select(sa_func.count()).select_from(AuditLog)

    if event_type:
        query = query.where(AuditLog.event_type == event_type)
        count_query = count_query.where(AuditLog.event_type == event_type)
    if user_id:
        query = query.where(AuditLog.user_id == user_id)
        count_query = count_query.where(AuditLog.user_id == user_id)

    total = (await db.execute(count_query)).scalar_one()
    offset = (page - 1) * page_size
    logs = list(
        (
            await db.execute(
                query.order_by(AuditLog.created_at.desc())
                .offset(offset)
                .limit(page_size)
            )
        )
        .scalars()
        .all()
    )

    return {
        "data": [
            {
                "id": log.id,
                "event_type": log.event_type,
                "user_id": log.user_id,
                "ip_address": log.ip_address,
                "details": log.details,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "has_next": (page * page_size) < total,
        },
        "error": None,
    }


@router.post("/scraper/refresh")
async def trigger_manual_refresh(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Trigger manual trending data refresh (admin only)."""
    import asyncio

    from app.scraper.fetcher import fetch_trending_job

    # Run in background — don't block the response
    asyncio.create_task(fetch_trending_job())

    return {"data": {"message": "Trending refresh triggered"}, "error": None}
