"""Audio streaming helpers — on-demand caching, file streaming."""

import asyncio
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.scraper.downloader import download_audio
from app.sounds.models import Sound
from app.sounds.repository import SoundRepository

logger = get_logger(module="sounds.stream")

# Lock to prevent duplicate downloads for the same sound
_download_locks: dict[str, asyncio.Lock] = {}


async def ensure_cached(sound: Sound, db: AsyncSession) -> str | None:
    """Ensure a sound is cached on disk. Downloads on-demand if needed.

    Returns file_path or None if download fails.
    Uses per-sound locks to prevent concurrent duplicate downloads.
    """
    if sound.cached and sound.file_path:
        # Update last_accessed_at
        sound.last_accessed_at = datetime.now(UTC)
        await db.flush()
        return sound.file_path

    # Get or create lock for this sound
    lock_key = sound.tiktok_sound_id
    if lock_key not in _download_locks:
        _download_locks[lock_key] = asyncio.Lock()

    async with _download_locks[lock_key]:
        # Re-check after acquiring lock (another request may have cached it)
        repo = SoundRepository(db)
        refreshed = await repo.get_by_tiktok_id(sound.tiktok_sound_id)
        if refreshed and refreshed.cached and refreshed.file_path:
            refreshed.last_accessed_at = datetime.now(UTC)
            await db.flush()
            return refreshed.file_path

        # Download
        file_path = await download_audio(sound.tiktok_sound_id, sound.play_url)
        if file_path:
            sound.cached = True
            sound.file_path = file_path
            sound.cached_at = datetime.now(UTC)
            sound.last_accessed_at = datetime.now(UTC)
            await db.commit()
            logger.info("on_demand_cached", sound_id=sound.tiktok_sound_id)
            return file_path

    return None
