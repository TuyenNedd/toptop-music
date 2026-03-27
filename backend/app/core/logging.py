"""Structured logging configuration using structlog."""

import logging
from typing import Any

import structlog


def configure_logging() -> None:
    """Configure structlog with JSON output and correlation ID support."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(**kwargs: Any) -> structlog.stdlib.BoundLogger:
    """Return a bound structlog logger with optional initial context."""
    return structlog.get_logger(**kwargs)  # type: ignore[no-any-return]
