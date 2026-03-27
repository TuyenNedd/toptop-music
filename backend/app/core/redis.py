"""Async Redis client setup and connection helpers."""

import contextlib

import redis.asyncio as aioredis

from app.config import settings

_redis_client: aioredis.Redis | None = None


async def init_redis() -> None:
    """Initialize the async Redis client. Call during app startup."""
    global _redis_client  # noqa: PLW0603
    _redis_client = aioredis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
    )


async def close_redis() -> None:
    """Close the Redis connection. Call during app shutdown."""
    global _redis_client  # noqa: PLW0603
    if _redis_client:
        with contextlib.suppress(Exception):
            await _redis_client.close()
        _redis_client = None


def get_redis() -> aioredis.Redis:
    """Return the active Redis client. Raises if not initialized."""
    if _redis_client is None:
        raise RuntimeError("Redis client not initialized. Call init_redis() first.")
    return _redis_client
