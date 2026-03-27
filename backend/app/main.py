"""TikTok Music Discovery Platform - Backend API."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.config import settings
from app.database import get_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan context manager."""
    # Startup: will be used by APScheduler and other services later
    yield
    # Shutdown: cleanup resources


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="TopTop Music API",
        description="TikTok Music Discovery Platform",
        version="0.1.0",
        lifespan=lifespan,
    )

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
        """Readiness check — verifies database connectivity."""
        try:
            await db.execute(text("SELECT 1"))
            return {"data": {"status": "ok", "database": "connected"}, "error": None}
        except Exception:
            return JSONResponse(
                status_code=503,
                content={
                    "data": None,
                    "error": {
                        "code": "DB_UNAVAILABLE",
                        "message": "Database connection failed",
                    },
                },
            )

    return app


app = create_app()
