"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env")

    # Database
    DATABASE_URL: str = "mysql+aiomysql://root:password@localhost:3306/toptop_music"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_EXPIRY_MINUTES: int = 30

    # TikTok
    TIKTOK_MS_TOKEN: str = ""
    VN_PROXY_URL: str = ""

    # SMTP
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    # Cache
    CACHE_MAX_SIZE_GB: int = 10

    # Trending
    TRENDING_FETCH_INTERVAL_MINUTES: int = 30
    TRENDING_FETCH_COUNT: int = 50

    # CORS
    CORS_ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    def validate_production_secrets(self) -> None:
        """Raise if critical secrets are still at insecure defaults."""
        if self.JWT_SECRET_KEY == "change-me-in-production":
            import warnings

            warnings.warn(
                "JWT_SECRET_KEY is using the default insecure value. "
                "Set a strong secret in production.",
                stacklevel=2,
            )


settings = Settings()
