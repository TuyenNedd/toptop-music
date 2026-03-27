"""Cache storage management — LRU eviction when disk limit exceeded."""

import json
import os
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.logging import get_logger
from app.sounds.models import Sound

logger = get_logger(module="sounds.cache")


async def get_cache_stats(db: AsyncSession) -> dict[str, object]:
    """Get cache statistics — total size, file count."""
    result = await db.execute(select(Sound).where(Sound.cached == True))  # noqa: E712
    cached_sounds = list(result.scalars().all())

    total_size = 0
    file_count = 0
    for s in cached_sounds:
        if s.file_path and os.path.exists(s.file_path):
            total_size += os.path.getsize(s.file_path)
            file_count += 1

    return {
        "total_size_bytes": total_size,
        "total_size_gb": round(total_size / (1024**3), 2),
        "file_count": file_count,
        "max_size_gb": settings.CACHE_MAX_SIZE_GB,
    }


async def evict_lru_if_needed(db: AsyncSession) -> int:
    """Evict least recently accessed cached files if over disk limit.

    Returns number of files evicted.
    """
    stats = await get_cache_stats(db)
    max_bytes = settings.CACHE_MAX_SIZE_GB * (1024**3)

    total_size = int(stats["total_size_bytes"])  # type: ignore[call-overload]
    if total_size <= max_bytes:
        return 0

    # Get cached sounds ordered by last_accessed_at ASC (least recent first)
    result = await db.execute(
        select(Sound)
        .where(Sound.cached == True)  # noqa: E712
        .order_by(Sound.last_accessed_at.asc().nullsfirst())
    )
    candidates = list(result.scalars().all())

    evicted = 0
    for sound in candidates:
        if total_size <= max_bytes:
            break

        if not sound.file_path or not os.path.exists(sound.file_path):
            sound.cached = False
            sound.file_path = None
            evicted += 1
            continue

        file_size = os.path.getsize(sound.file_path)
        try:
            os.remove(sound.file_path)
        except OSError:
            continue

        sound.cached = False
        sound.file_path = None
        sound.cached_at = None
        total_size -= file_size
        evicted += 1

    await db.commit()

    # Store stats in Redis
    try:
        from app.core.redis import get_redis

        redis = get_redis()
        await redis.set(
            "cache:stats",
            json.dumps(
                {
                    "total_size_gb": round(total_size / (1024**3), 2),
                    "file_count": int(stats["file_count"]) - evicted,  # type: ignore[call-overload]
                    "eviction_count": evicted,
                    "last_eviction": datetime.now(UTC).isoformat(),
                }
            ),
            ex=3600,
        )
    except RuntimeError:
        pass

    logger.info(
        "cache_eviction_complete",
        evicted=evicted,
        remaining_gb=round(total_size / (1024**3), 2),
    )
    return evicted
