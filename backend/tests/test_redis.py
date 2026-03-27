"""Tests for Redis client module (Story 1.4)."""

import pytest

from app.core.redis import get_redis


def test_get_redis_raises_before_init() -> None:
    """get_redis raises RuntimeError if called before init_redis."""
    # Ensure client is None (fresh state)
    import app.core.redis as redis_mod

    original = redis_mod._redis_client
    redis_mod._redis_client = None
    try:
        with pytest.raises(RuntimeError, match="Redis client not initialized"):
            get_redis()
    finally:
        redis_mod._redis_client = original
