"""Audio download and cache logic — httpx primary, yt-dlp fallback."""

import os
from pathlib import Path

import httpx

from app.core.logging import get_logger

logger = get_logger(module="scraper.downloader")

SOUNDS_DIR = Path("sounds")


def ensure_sounds_dir() -> None:
    """Create sounds/ directory if it doesn't exist."""
    SOUNDS_DIR.mkdir(exist_ok=True)


async def download_audio(
    tiktok_sound_id: str,
    play_url: str | None,
) -> str | None:
    """Download audio file and return the file path, or None on failure.

    Tries play_url via httpx first, falls back to yt-dlp.
    """
    ensure_sounds_dir()

    # Try primary URL via httpx
    if play_url:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(play_url)
                resp.raise_for_status()

                # Determine extension from content-type
                content_type = resp.headers.get("content-type", "")
                ext = "mp3" if "mpeg" in content_type else "m4a"
                file_path = str(SOUNDS_DIR / f"{tiktok_sound_id}.{ext}")

                with open(file_path, "wb") as f:
                    f.write(resp.content)

                logger.info(
                    "audio_downloaded", sound_id=tiktok_sound_id, source="httpx"
                )
                return file_path
        except Exception as e:
            logger.warning(
                "audio_download_httpx_failed",
                sound_id=tiktok_sound_id,
                error=str(e),
            )

    # Fallback: yt-dlp
    try:
        import subprocess

        file_path = str(SOUNDS_DIR / f"{tiktok_sound_id}.mp3")
        tiktok_url = f"https://www.tiktok.com/music/{tiktok_sound_id}"
        result = subprocess.run(
            [
                "yt-dlp",
                "--extract-audio",
                "--audio-format",
                "mp3",
                "-o",
                file_path,
                tiktok_url,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0 and os.path.exists(file_path):
            logger.info("audio_downloaded", sound_id=tiktok_sound_id, source="yt-dlp")
            return file_path
        logger.warning(
            "audio_download_ytdlp_failed",
            sound_id=tiktok_sound_id,
            stderr=result.stderr[:200],
        )
    except Exception as e:
        logger.error(
            "audio_download_all_failed",
            sound_id=tiktok_sound_id,
            error=str(e),
        )

    return None


async def pre_cache_top_sounds(
    sounds: list[dict[str, object]],
    limit: int = 20,
) -> int:
    """Download and cache top N uncached trending sounds.

    Returns count of successfully cached sounds.
    """
    from datetime import UTC, datetime

    from app.database import AsyncSessionLocal
    from app.sounds.repository import SoundRepository

    cached_count = 0

    async with AsyncSessionLocal() as db:
        repo = SoundRepository(db)

        for sound_data in sounds[:limit]:
            tiktok_id = str(sound_data.get("tiktok_sound_id", ""))
            if not tiktok_id:
                continue

            sound = await repo.get_by_tiktok_id(tiktok_id)
            if not sound or sound.cached:
                continue

            file_path = await download_audio(tiktok_id, sound.play_url)
            if file_path:
                sound.cached = True
                sound.file_path = file_path
                sound.cached_at = datetime.now(UTC)
                cached_count += 1

        await db.commit()

    logger.info("pre_cache_complete", cached_count=cached_count)
    return cached_count
