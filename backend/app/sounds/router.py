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
