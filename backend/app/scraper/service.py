"""TikTok-Api wrapper — session management and data extraction."""

from typing import Any

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(module="scraper.service")


async def fetch_trending_videos(count: int = 50) -> list[dict[str, Any]]:
    """Fetch trending videos from TikTok Vietnam via TikTok-Api.

    Returns list of raw video data dicts.
    Requires Playwright and valid ms_token + VN proxy.
    """
    try:
        from TikTokApi import TikTokApi

        async with TikTokApi() as api:
            await api.create_sessions(
                ms_tokens=[settings.TIKTOK_MS_TOKEN],
                num_sessions=1,
                sleep_after=3,
                proxies=[settings.VN_PROXY_URL] if settings.VN_PROXY_URL else None,
            )
            videos: list[dict[str, Any]] = []
            async for video in api.trending.videos(count=count):
                videos.append(video.as_dict)
            return videos
    except Exception as e:
        logger.error("tiktok_fetch_failed", error=str(e))
        raise
