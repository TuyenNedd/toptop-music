"""Standalone scraper worker — runs on host machine, not Docker.

Usage:
    cd backend
    uv run python scraper_worker.py
    uv run python scraper_worker.py --schedule
"""

import argparse
import asyncio
import json
import sys
from datetime import UTC, datetime

from TikTokApi import TikTokApi

from app.config import settings
from app.database import AsyncSessionLocal
from app.scraper.schemas import extract_sound_from_video
from app.sounds.repository import SoundRepository


async def fetch_and_store(count: int = 50) -> int:
    """Fetch trending and store in DB. Returns sounds count."""
    ms_token = settings.TIKTOK_MS_TOKEN or None
    print(f"Fetching {count} videos (token: {'set' if ms_token else 'auto'})...")

    videos = []
    async with TikTokApi() as api:
        await api.create_sessions(
            ms_tokens=[ms_token],
            num_sessions=1,
            sleep_after=5,
            headless=True,
        )
        async for video in api.trending.videos(count=count):
            videos.append(video.as_dict)

    print(f"Got {len(videos)} videos")
    if not videos:
        return 0

    stored = 0
    async with AsyncSessionLocal() as db:
        repo = SoundRepository(db)
        now = datetime.now(UTC)
        for rank, video in enumerate(videos, start=1):
            sd = extract_sound_from_video(video)
            if not sd or not sd["tiktok_sound_id"]:
                continue
            stats = video.get("stats", {})
            await repo.upsert(
                tiktok_sound_id=sd["tiktok_sound_id"],
                title=sd["title"],
                artist=sd["artist"],
                play_url=sd["play_url"],
                cover_url=sd["cover_url"],
                duration=sd["duration"],
                usage_count=stats.get("playCount", 0),
                trend_rank=rank,
                is_original=sd["is_original"],
                last_trending_at=now,
            )
            stored += 1
            print(f"  #{rank}: {sd['title']} - {sd['artist']}")
        await db.commit()

    try:
        import redis.asyncio as aioredis

        r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        await r.set(
            "fetcher:status",
            json.dumps(
                {
                    "last_run": datetime.now(UTC).isoformat(),
                    "success": True,
                    "sounds_fetched": stored,
                }
            ),
            ex=86400,
        )
        await r.close()
    except Exception:
        pass

    print(f"Stored {stored} sounds")
    return stored


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--schedule", action="store_true")
    parser.add_argument("--count", type=int, default=10)
    args = parser.parse_args()

    async def main() -> None:
        if args.schedule:
            interval = settings.TRENDING_FETCH_INTERVAL_MINUTES * 60
            print(
                f"Schedule mode: every {settings.TRENDING_FETCH_INTERVAL_MINUTES} min"
            )
            while True:
                try:
                    await fetch_and_store(args.count)
                except Exception as e:
                    print(f"Error: {e}")
                await asyncio.sleep(interval)
        else:
            try:
                await fetch_and_store(args.count)
            except Exception as e:
                print(f"Error: {e}")
                sys.exit(1)

    asyncio.run(main())
