"""Trending fetcher — APScheduler job that fetches and stores trending sounds."""

import json
from datetime import UTC, datetime

from app.config import settings
from app.core.logging import get_logger
from app.database import AsyncSessionLocal
from app.scraper.schemas import extract_sound_from_video
from app.scraper.service import fetch_trending_videos
from app.sounds.repository import SoundRepository

logger = get_logger(module="scraper.fetcher")


async def fetch_trending_job() -> None:
    """APScheduler job: fetch trending sounds and upsert to database.

    Retries up to 3 times with exponential backoff.
    Stores fetcher status in Redis for admin dashboard.
    """
    import asyncio

    max_retries = 3
    sounds_fetched = 0
    last_error = ""

    for attempt in range(max_retries):
        try:
            logger.info("trending_fetch_start", attempt=attempt + 1)

            videos = await fetch_trending_videos(
                count=settings.TRENDING_FETCH_COUNT,
            )

            async with AsyncSessionLocal() as db:
                repo = SoundRepository(db)
                now = datetime.now(UTC)

                for rank, video in enumerate(videos, start=1):
                    sound_data = extract_sound_from_video(video)
                    if not sound_data or not sound_data["tiktok_sound_id"]:
                        continue

                    # Get usage count from video stats
                    stats = video.get("stats", {})
                    usage_count = stats.get("playCount", 0)

                    await repo.upsert(
                        tiktok_sound_id=sound_data["tiktok_sound_id"],
                        title=sound_data["title"],
                        artist=sound_data["artist"],
                        play_url=sound_data["play_url"],
                        cover_url=sound_data["cover_url"],
                        duration=sound_data["duration"],
                        usage_count=usage_count,
                        trend_rank=rank,
                        is_original=sound_data["is_original"],
                        last_trending_at=now,
                    )
                    sounds_fetched += 1

                await db.commit()

            # Store status in Redis
            await _store_fetcher_status(
                success=True,
                sounds_fetched=sounds_fetched,
                error="",
            )

            logger.info("trending_fetch_complete", sounds_fetched=sounds_fetched)
            return

        except Exception as e:
            last_error = str(e)
            logger.warning(
                "trending_fetch_retry",
                attempt=attempt + 1,
                error=last_error,
            )
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** (attempt + 1))  # Exponential backoff

    # All retries failed
    await _store_fetcher_status(
        success=False,
        sounds_fetched=0,
        error=last_error,
    )
    logger.error("trending_fetch_failed_all_retries", error=last_error)


async def _store_fetcher_status(success: bool, sounds_fetched: int, error: str) -> None:
    """Store fetcher status in Redis for admin dashboard."""
    try:
        from app.core.redis import get_redis

        redis = get_redis()
        status = json.dumps(
            {
                "last_run": datetime.now(UTC).isoformat(),
                "success": success,
                "sounds_fetched": sounds_fetched,
                "error": error,
            }
        )
        await redis.set("fetcher:status", status, ex=86400)  # 24h TTL
    except RuntimeError:
        pass  # Redis not available
