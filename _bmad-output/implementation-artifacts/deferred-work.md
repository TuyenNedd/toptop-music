# Deferred Work

## Deferred from: code review of 1-1-backend-project-scaffolding (2026-03-26)

- Route handler defined inside `create_app()` factory in `backend/app/main.py` — acceptable for scaffolding, revisit when adding more routes
- Module-level `TestClient` in `backend/tests/test_health.py` — lifespan is empty now, revisit when startup logic (DB/Redis) is added
- CORS `allow_methods=["*"]` and `allow_headers=["*"]` overly permissive — tighten per-environment in a later story

## Deferred from: code review of 1-3-database-setup-initial-migration (2026-03-27)

- Engine created at module level in `database.py` — standard lazy pattern, no runtime issue
- Alembic `env.py` imports trigger engine creation at import time — engine is lazy, acceptable
- `test_get_db` uses `__anext__` directly — fragile but functional, revisit if `get_db` changes

## Deferred from: code review of 1-4-redis-setup-core-infrastructure (2026-03-27)

- Test routes permanently added to app in `test_exceptions.py` — acceptable for unit tests
- `BaseHTTPMiddleware` has known streaming issues — revisit in Story 5.1 when `/api/stream/*` is added
