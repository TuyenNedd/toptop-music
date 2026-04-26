"""TikTok-Api wrapper — session management and data extraction."""

from typing import Any

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(module="scraper.service")


async def fetch_trending_videos(count: int = 50) -> list[dict[str, Any]]:
    """Fetch trending videos from TikTok Vietnam via TikTok-Api.

    Uses Playwright headless browser to create sessions.
    ms_token is optional — Playwright can self-generate tokens.
    Falls back gracefully if ms_token is empty.
    """
    try:
        from TikTokApi import TikTokApi

        # Use ms_token if available, otherwise let Playwright handle it
        ms_tokens: list[str | None] = (
            [settings.TIKTOK_MS_TOKEN] if settings.TIKTOK_MS_TOKEN else [None]
        )
        proxies = [settings.VN_PROXY_URL] if settings.VN_PROXY_URL else None

        async with TikTokApi() as api:
            await api.create_sessions(
                ms_tokens=ms_tokens,
                num_sessions=1,
                sleep_after=5,
                headless=True,
                proxies=proxies,
                suppress_resource_load_types=["image", "media", "font", "stylesheet"],
            )

            videos: list[dict[str, Any]] = []
            async for video in api.trending.videos(count=count):
                videos.append(video.as_dict)

            if not videos:
                logger.warning("tiktok_fetch_empty", count=count)

            return videos

    except ImportError:
        logger.error("tiktok_api_not_installed")
        raise
    except Exception as e:
        logger.error("tiktok_fetch_failed", error=str(e), error_type=type(e).__name__)
        raise
