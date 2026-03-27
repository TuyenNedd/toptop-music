"""TikTok Music Discovery Platform - Backend API."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import redis.asyncio as aioredis
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.admin.router import router as admin_router
from app.auth.router import router as auth_router
from app.config import settings
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    unhandled_exception_handler,
)
from app.core.logging import configure_logging
from app.core.middleware import RequestIDMiddleware
from app.core.redis import close_redis, get_redis, init_redis
from app.database import get_db
from app.sounds.router import router as sounds_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan context manager."""
    await init_redis()

    # Start APScheduler for trending fetcher
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.interval import IntervalTrigger

    from app.scraper.fetcher import fetch_trending_job

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        fetch_trending_job,
        trigger=IntervalTrigger(minutes=settings.TRENDING_FETCH_INTERVAL_MINUTES),
        id="trending_fetcher",
        replace_existing=True,
    )
    scheduler.start()

    yield

    scheduler.shutdown(wait=False)
    await close_redis()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    configure_logging()

    app = FastAPI(
        title="TopTop Music API",
        description="TikTok Music Discovery Platform",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Exception handlers
    app.add_exception_handler(AppException, app_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # Middleware (order matters — outermost first)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health_check() -> dict[str, Any]:
        """Liveness check — app is running."""
        return {"data": {"status": "ok"}, "error": None}

    @app.get("/health/ready", response_model=None)
    async def health_ready(
        db: AsyncSession = Depends(get_db),
    ) -> JSONResponse | dict[str, Any]:
        """Readiness check — verifies database and Redis connectivity."""
        status: dict[str, str] = {}
        errors: list[str] = []

        # Check database
        try:
            await db.execute(text("SELECT 1"))
            status["database"] = "connected"
        except Exception:
            errors.append("database")

        # Check Redis
        try:
            redis_client: aioredis.Redis = get_redis()
            await redis_client.ping()  # type: ignore[misc]
            status["redis"] = "connected"
        except Exception:
            errors.append("redis")

        if errors:
            return JSONResponse(
                status_code=503,
                content={
                    "data": None,
                    "error": {
                        "code": "SERVICE_UNAVAILABLE",
                        "message": f"Unavailable: {', '.join(errors)}",
                    },
                },
            )

        return {"data": {"status": "ok", **status}, "error": None}

    # Routers
    app.include_router(auth_router)
    app.include_router(admin_router)
    app.include_router(sounds_router)

    return app


app = create_app()
