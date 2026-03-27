# Story 1.4: Redis Setup & Core Infrastructure

Status: done

## Story

As a developer,
I want to set up Redis connection and shared core infrastructure (logging, exceptions, middleware),
so that all modules have consistent error handling, logging, and caching.

## Acceptance Criteria

1. **Given** the backend project exists, **When** I create `app/core/redis.py`, **Then** it creates an async Redis client using `redis.asyncio` with connection helpers (`get_redis`, `close_redis`) and integrates with the app lifespan

2. **Given** `app/core/redis.py` exists, **When** I create `app/core/logging.py`, **Then** it configures structlog with JSON output, correlation ID binding (`request_id`), log levels, and a `get_logger()` helper

3. **Given** logging is configured, **When** I create `app/core/exceptions.py`, **Then** it defines an `AppException` base class with `code`, `message`, `status_code` attributes, and a global exception handler that returns the standard error envelope `{"data": null, "error": {"code": "...", "message": "..."}}`

4. **Given** exceptions are configured, **When** I create `app/core/middleware.py`, **Then** it injects an `X-Request-ID` correlation ID into every request (generates UUID if not present in headers) and binds it to structlog context

5. **Given** all core modules exist, **When** I register them in `app/main.py`, **Then** the global exception handler is registered, middleware is added, Redis connects on startup and disconnects on shutdown, and structlog is configured

6. **Given** Redis is configured, **When** I update `/health/ready`, **Then** it checks both database AND Redis connectivity, returning `{"data": {"status": "ok", "database": "connected", "redis": "connected"}, "error": null}` on success

7. **Given** the project is complete, **When** I run `uv run ruff check .` and `uv run mypy .`, **Then** both pass with zero errors

## Tasks / Subtasks

- [x] Task 1: Create `app/core/redis.py` (AC: #1)
  - [x] Create async Redis client factory using `redis.asyncio.from_url(settings.REDIS_URL)`
  - [x] Create `get_redis()` function returning the Redis client instance
  - [x] Create `close_redis()` for graceful shutdown
  - [x] Store client as module-level variable, initialized in lifespan
- [x] Task 2: Create `app/core/logging.py` (AC: #2)
  - [x] Configure structlog with JSON renderer, timestamp, log level
  - [x] Add `request_id` context variable binding for correlation IDs
  - [x] Create `get_logger()` helper that returns a bound structlog logger
  - [x] Call `configure_logging()` during app startup
- [x] Task 3: Create `app/core/exceptions.py` (AC: #3)
  - [x] Define `AppException(Exception)` with `code: str`, `message: str`, `status_code: int = 500`
  - [x] Create `app_exception_handler(request, exc)` returning `JSONResponse` with error envelope
  - [x] Create `unhandled_exception_handler(request, exc)` returning 500 with generic message, logging full details
  - [x] Register both handlers in `create_app()`
- [x] Task 4: Create `app/core/middleware.py` (AC: #4)
  - [x] Create `RequestIDMiddleware` (Starlette `BaseHTTPMiddleware`)
  - [x] Extract `X-Request-ID` from request headers, generate `uuid4()` if missing
  - [x] Bind `request_id` to structlog context via `structlog.contextvars.bind_contextvars`
  - [x] Set `X-Request-ID` response header
  - [x] Register middleware in `create_app()`
- [x] Task 5: Integrate all core modules in `app/main.py` (AC: #5)
  - [x] Import and register `AppException` handler and unhandled exception handler
  - [x] Add `RequestIDMiddleware`
  - [x] Initialize Redis in lifespan startup, close in shutdown
  - [x] Call `configure_logging()` in `create_app()`
- [x] Task 6: Update `/health/ready` with Redis check (AC: #6)
  - [x] Add Redis `PING` check alongside existing DB `SELECT 1`
  - [x] Return combined status: `{"data": {"status": "ok", "database": "connected", "redis": "connected"}, "error": null}`
  - [x] Return 503 if either DB or Redis is unavailable
- [x] Task 7: Verify linting and type checking (AC: #7)
  - [x] Run `uv run ruff check .` — zero errors
  - [x] Run `uv run mypy .` — zero errors

### Review Follow-ups (AI)

- [x] [Review][Patch] `unhandled_exception_handler` swallows `HTTPException` — FastAPI 404/405/422 replaced by generic 500. Must exclude `HTTPException` [backend/app/core/exceptions.py, backend/app/main.py]
- [x] [Review][Patch] `configure_logging()` called in lifespan but `exceptions.py` uses `get_logger()` at module level — move configure call earlier or lazy-init logger [backend/app/core/exceptions.py, backend/app/core/logging.py]
- [x] [Review][Patch] `close_redis()` doesn't handle connection errors during shutdown — wrap in try/except [backend/app/core/redis.py]
- [x] [Review][Defer] Test routes permanently added to app in `test_exceptions.py` — acceptable for unit tests, revisit if test isolation issues arise [backend/tests/test_exceptions.py] — deferred
- [x] [Review][Defer] `BaseHTTPMiddleware` has known streaming issues — no streaming endpoints yet, revisit in Story 5.1 when `/api/stream/*` is added [backend/app/core/middleware.py] — deferred

## Dev Notes

### Architecture Compliance

- **Core module:** `core/` provides shared infrastructure — NO business logic
- **Error handling:** Custom exceptions → global handler → error envelope. Never bare `raise HTTPException`
- **Logging:** structlog JSON with correlation IDs. Required fields: `timestamp`, `level`, `request_id`, `module`, `message`
- **Middleware:** `X-Request-ID` propagated through all layers. Generated by middleware if not present in request headers
- **Redis:** async via `redis.asyncio`. Used for caching, sessions, rate limiting in later stories
- [Source: architecture.md#Process Patterns, architecture.md#Project Structure & Boundaries]

### `app/core/redis.py` Pattern

```python
import redis.asyncio as aioredis
from app.config import settings

_redis_client: aioredis.Redis | None = None

async def init_redis() -> None:
    global _redis_client
    _redis_client = aioredis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
    )

async def close_redis() -> None:
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None

def get_redis() -> aioredis.Redis:
    assert _redis_client is not None, "Redis not initialized"
    return _redis_client
```

- [Source: architecture.md#Data Architecture — Redis 7.x, async via redis.asyncio]

### `app/core/exceptions.py` Pattern (CRITICAL)

```python
class AppException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 500) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)

# Global handler registered in FastAPI:
async def app_exception_handler(request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"data": None, "error": {"code": exc.code, "message": exc.message}},
    )
```

Error code format: `DOMAIN_ACTION_REASON` — e.g., `AUTH_LOGIN_INVALID_CREDENTIALS`, `SOUND_NOT_FOUND`

- [Source: architecture.md#Process Patterns — Error Handling, architecture.md#Format Patterns — Error Codes]

### `app/core/logging.py` Pattern

```python
import structlog

def configure_logging() -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )

def get_logger(**kwargs: object) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(**kwargs)
```

Required fields per log entry: `timestamp`, `level`, `request_id`, `module`, `message`
Optional: `user_id`, `sound_id`, `duration_ms`, `error_detail`

- [Source: architecture.md#Process Patterns — Logging]

### `app/core/middleware.py` Pattern

```python
import uuid
import structlog
from starlette.middleware.base import BaseHTTPMiddleware

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        structlog.contextvars.bind_contextvars(request_id=request_id)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        structlog.contextvars.unbind_contextvars("request_id")
        return response
```

- [Source: architecture.md#Process Patterns — Logging, architecture.md#Enforcement Guidelines rule #6]

### Lifespan Integration

```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    await init_redis()
    yield
    await close_redis()
```

- [Source: architecture.md#Infrastructure & Deployment — structlog, Redis]

### Previous Story Learnings (Story 1.1, 1.3)

- `app/config.py` already has `REDIS_URL = "redis://localhost:6379/0"` — import `settings` from there
- `app/main.py` has `create_app()` factory with lifespan, CORS, `/health`, `/health/ready`
- `/health/ready` currently checks DB only — extend to include Redis
- `response_model=None` needed on endpoints returning `JSONResponse | dict`
- `redis` package already installed in `pyproject.toml` from Story 1.1
- `structlog` already installed in `pyproject.toml` from Story 1.1
- [Source: backend/app/config.py, backend/app/main.py, backend/pyproject.toml]

### Anti-Patterns to Avoid

- ❌ Do NOT use bare `raise HTTPException` — use `raise AppException(code, message, status_code)`
- ❌ Do NOT use `print()` or `logging.info()` — use `structlog.get_logger()`
- ❌ Do NOT create business logic in `core/` — only shared infrastructure
- ❌ Do NOT expose stack traces in error responses — log them, return generic message
- ❌ Do NOT hardcode request IDs — always use `X-Request-ID` from headers or generate UUID
- [Source: architecture.md#Anti-Patterns to Avoid, architecture.md#Enforcement Guidelines]

### Files to Create/Modify

- `backend/app/core/redis.py` — new
- `backend/app/core/logging.py` — new
- `backend/app/core/exceptions.py` — new
- `backend/app/core/middleware.py` — new
- `backend/app/main.py` — modify (register handlers, middleware, lifespan)
- `backend/tests/test_redis.py` — new
- `backend/tests/test_exceptions.py` — new
- `backend/tests/test_middleware.py` — new

### References

- [Source: architecture.md#Process Patterns — Error Handling, Logging]
- [Source: architecture.md#Data Architecture — Redis 7.x, caching strategy]
- [Source: architecture.md#Project Structure & Boundaries — core/ module files]
- [Source: architecture.md#Enforcement Guidelines — rule #6 correlation ID, rule #7 custom exceptions]
- [Source: epics.md#Story 1.4 — Acceptance criteria]

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.6

### Debug Log References

- N818 ruff rule flags `AppException` (wants `AppError` suffix) — disabled N818 since architecture spec uses `AppException`
- `structlog.get_logger()` returns `Any` — added `type: ignore[no-any-return]`
- `redis.ping()` returns `Awaitable[bool] | bool` — added `type: ignore[misc]`
- `add_exception_handler` type mismatch with async handlers — added `type: ignore[arg-type]`
- Updated `test_health_ready.py` to mock both DB and Redis (previously only mocked DB)

### Completion Notes List

- Created `app/core/redis.py` — async Redis client with `init_redis()`, `close_redis()`, `get_redis()`
- Created `app/core/logging.py` — structlog JSON config with correlation ID support, `get_logger()` helper
- Created `app/core/exceptions.py` — `AppException` base class, global exception handler returning error envelope, unhandled exception handler with generic 500
- Created `app/core/middleware.py` — `RequestIDMiddleware` injects/propagates `X-Request-ID`, binds to structlog context
- Updated `app/main.py` — registered exception handlers, middleware, Redis lifespan, logging config
- Updated `/health/ready` — checks both DB and Redis, returns combined status
- 29 tests passing (8 new: exceptions, middleware, redis, health_ready updated)
- ruff + mypy both pass zero errors

### File List

- backend/app/core/redis.py (new)
- backend/app/core/logging.py (new)
- backend/app/core/exceptions.py (new)
- backend/app/core/middleware.py (new)
- backend/app/main.py (modified — exception handlers, middleware, lifespan, health/ready)
- backend/pyproject.toml (modified — added N818 to ruff ignore)
- backend/tests/test_exceptions.py (new)
- backend/tests/test_middleware.py (new)
- backend/tests/test_redis.py (new)
- backend/tests/test_health_ready.py (modified — mock both DB and Redis)

## Change Log

- 2026-03-27: Story 1.4 implemented — Redis client, structlog logging, AppException + global handlers, RequestIDMiddleware. 29 tests passing, ruff + mypy clean.
- 2026-03-27: Code review complete — 3 patches applied (HTTPException handling, logging init order, redis close error handling), 2 deferred. 29 tests passing.
