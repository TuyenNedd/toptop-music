"""Tests for configuration module."""

import os
from unittest.mock import patch

from app.config import Settings


def make_settings() -> Settings:
    """Create Settings isolated from any .env file on disk."""
    env_overrides = {
        "DATABASE_URL": "mysql+aiomysql://root:password@localhost:3306/toptop_music",
        "REDIS_URL": "redis://localhost:6379/0",
        "JWT_SECRET_KEY": "change-me-in-production",
    }
    with patch.dict(os.environ, env_overrides, clear=False):
        return Settings(model_config={"env_file": None})  # type: ignore[call-arg]


def test_settings_default_values() -> None:
    """Settings has sensible defaults for development."""
    s = Settings()
    assert s.JWT_EXPIRY_MINUTES == 30
    assert s.CACHE_MAX_SIZE_GB == 10
    assert s.TRENDING_FETCH_INTERVAL_MINUTES == 30
    assert s.TRENDING_FETCH_COUNT == 50
    assert s.SMTP_PORT == 587


def test_settings_database_url_default() -> None:
    """DATABASE_URL has a development default."""
    s = Settings()
    assert "toptop_music" in s.DATABASE_URL


def test_settings_redis_url_default() -> None:
    """REDIS_URL has a development default."""
    s = Settings()
    assert s.REDIS_URL.startswith("redis://")


def test_settings_cors_origins_default() -> None:
    """CORS_ALLOWED_ORIGINS defaults to localhost:3000."""
    s = Settings()
    assert "http://localhost:3000" in s.CORS_ALLOWED_ORIGINS
