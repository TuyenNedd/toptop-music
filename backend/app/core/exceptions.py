"""Custom exception classes and global exception handlers."""

from fastapi import Request
from fastapi.exceptions import HTTPException
from starlette.responses import JSONResponse

from app.core.logging import get_logger

logger = get_logger(module="exceptions")


class AppException(Exception):
    """Base exception for all application errors.

    Error code format: DOMAIN_ACTION_REASON
    Examples: AUTH_LOGIN_INVALID_CREDENTIALS, SOUND_NOT_FOUND
    """

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 500,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle AppException — return structured error envelope."""
    logger.warning(
        "app_exception",
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
        path=str(request.url.path),
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "data": None,
            "error": {"code": exc.code, "message": exc.message},
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions — log details, return generic message.

    Excludes HTTPException to preserve FastAPI's built-in 404/405/422 handling.
    """
    if isinstance(exc, HTTPException):
        # Let FastAPI handle its own HTTP exceptions (404, 405, 422, etc.)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "data": None,
                "error": {
                    "code": f"HTTP_{exc.status_code}",
                    "message": (
                        exc.detail if isinstance(exc.detail, str) else "Request error"
                    ),
                },
            },
        )

    logger.error(
        "unhandled_exception",
        error_type=type(exc).__name__,
        error_detail=str(exc),
        path=str(request.url.path),
    )
    return JSONResponse(
        status_code=500,
        content={
            "data": None,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            },
        },
    )
