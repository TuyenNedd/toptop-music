"""Sounds module router — trending, search, streaming endpoints."""

import contextlib
import json
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.database import get_db
from app.sounds.repository import SoundRepository
from app.sounds.schemas import PaginationMeta, SoundResponse

router = APIRouter(prefix="/api/sounds", tags=["sounds"])


@router.get("/trending")
async def get_trending(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Get paginated trending sounds. Cached in Redis (5 min TTL)."""
    # Try Redis cache
    cache_key = f"trending:{page}:{page_size}"
    try:
        from app.core.redis import get_redis

        redis = get_redis()
        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)  # type: ignore[no-any-return]
    except RuntimeError:
        pass

    repo = SoundRepository(db)
    sounds, total = await repo.get_trending(page, page_size)

    response = {
        "data": [SoundResponse.model_validate(s).model_dump() for s in sounds],
        "pagination": PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
            has_next=(page * page_size) < total,
        ).model_dump(),
        "error": None,
    }

    # Cache in Redis (5 min)
    with contextlib.suppress(Exception):
        await redis.set(cache_key, json.dumps(response, default=str), ex=300)

    return response


@router.get("/search")
async def search_sounds(
    q: str = Query(min_length=1, max_length=100),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Search sounds by title or artist. Cached in Redis (10 min TTL)."""
    cache_key = f"search:{q}:{page}:{page_size}"
    try:
        from app.core.redis import get_redis

        redis = get_redis()
        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)  # type: ignore[no-any-return]
    except RuntimeError:
        pass

    repo = SoundRepository(db)
    sounds, total = await repo.search(q, page, page_size)

    response = {
        "data": [SoundResponse.model_validate(s).model_dump() for s in sounds],
        "pagination": PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
            has_next=(page * page_size) < total,
        ).model_dump(),
        "error": None,
    }

    with contextlib.suppress(Exception):
        await redis.set(cache_key, json.dumps(response, default=str), ex=600)

    return response


@router.get("/stream-url/{sound_id}")
async def get_stream_url(
    sound_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Generate a signed streaming URL for a sound."""
    import time

    from app.core.security import create_signed_stream_url

    expires = int(time.time()) + 7200  # 2 hours
    token = create_signed_stream_url(sound_id, current_user.id, expires)

    return {
        "data": {
            "url": f"/api/sounds/stream/{sound_id}?token={token}&expires={expires}&uid={current_user.id}",
        },
        "error": None,
    }


@router.get("/stream/{sound_id}", response_model=None)
async def stream_audio(
    sound_id: int,
    token: str = Query(...),
    expires: int = Query(...),
    uid: int = Query(...),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Stream audio file with signed URL verification."""
    import os
    import time

    from fastapi.responses import FileResponse
    from starlette.responses import JSONResponse

    from app.core.security import verify_signed_stream_url
    from app.sounds.stream import ensure_cached

    # Verify token
    if not verify_signed_stream_url(sound_id, uid, expires, token):
        return JSONResponse(
            status_code=403,
            content={
                "data": None,
                "error": {
                    "code": "STREAM_INVALID_TOKEN",
                    "message": "Invalid stream token",
                },
            },
        )

    if expires < int(time.time()):
        return JSONResponse(
            status_code=403,
            content={
                "data": None,
                "error": {
                    "code": "STREAM_URL_EXPIRED",
                    "message": "Stream URL has expired",
                },
            },
        )

    # Get sound
    repo = SoundRepository(db)
    sound = await repo.get_by_id(sound_id)
    if not sound:
        return JSONResponse(
            status_code=404,
            content={
                "data": None,
                "error": {"code": "SOUND_NOT_FOUND", "message": "Sound not found"},
            },
        )

    # Ensure cached (on-demand download if needed)
    file_path = await ensure_cached(sound, db)
    if not file_path or not os.path.exists(file_path):
        return JSONResponse(
            status_code=503,
            content={
                "data": None,
                "error": {
                    "code": "STREAM_UNAVAILABLE",
                    "message": "Audio not available",
                },
            },
        )

    # Determine content type
    content_type = "audio/mpeg" if file_path.endswith(".mp3") else "audio/mp4"

    return FileResponse(
        path=file_path,
        media_type=content_type,
        headers={"Accept-Ranges": "bytes"},
    )


# --- Favorites ---


@router.post("/{sound_id}/favorite", status_code=201)
async def add_favorite(
    sound_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Add a sound to favorites."""
    from sqlalchemy.exc import IntegrityError

    from app.sounds.models import Favorite

    fav = Favorite(user_id=current_user.id, sound_id=sound_id)
    db.add(fav)
    try:
        await db.flush()
        await db.commit()
    except IntegrityError:
        await db.rollback()
        from app.core.exceptions import AppException

        raise AppException(
            code="FAVORITE_DUPLICATE",
            message="Sound already in favorites",
            status_code=409,
        )
    return {"data": {"sound_id": sound_id, "favorited": True}, "error": None}


@router.delete("/{sound_id}/favorite")
async def remove_favorite(
    sound_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Remove a sound from favorites."""
    from sqlalchemy import delete

    from app.sounds.models import Favorite

    await db.execute(
        delete(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.sound_id == sound_id,
        )
    )
    await db.commit()
    return {"data": {"sound_id": sound_id, "favorited": False}, "error": None}


@router.get("/favorites")
async def get_favorites(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Get user's favorite sounds."""
    from sqlalchemy import func as sa_func
    from sqlalchemy import select

    from app.sounds.models import Favorite, Sound

    # Count
    count_q = (
        select(sa_func.count())
        .select_from(Favorite)
        .where(Favorite.user_id == current_user.id)
    )
    total = (await db.execute(count_q)).scalar_one()

    # Paginated join
    offset = (page - 1) * page_size
    q = (
        select(Sound)
        .join(Favorite, Favorite.sound_id == Sound.id)
        .where(Favorite.user_id == current_user.id)
        .order_by(Favorite.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    sounds = list((await db.execute(q)).scalars().all())

    return {
        "data": [SoundResponse.model_validate(s).model_dump() for s in sounds],
        "pagination": PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
            has_next=(page * page_size) < total,
        ).model_dump(),
        "error": None,
    }
