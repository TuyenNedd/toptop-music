# Story 1.1: Backend Project Scaffolding

Status: ready-for-dev

## Story

As a developer,
I want to initialize the FastAPI backend project with proper structure and dependencies,
so that I have a working backend foundation to build all features on.

## Acceptance Criteria

1. **Given** no backend project exists, **When** I run `uv init backend --python 3.14`, **Then** a `backend/` directory is created with `pyproject.toml` and `.python-version` set to `3.14`

2. **Given** the backend project is initialized, **When** I add all core and dev dependencies to `pyproject.toml` and run `uv sync`, **Then** a `.venv` virtual environment is created with all packages installed successfully

3. **Given** dependencies are installed, **When** I create the modular monolith directory structure, **Then** the following directories exist with `__init__.py` files: `app/`, `app/auth/`, `app/sounds/`, `app/scraper/`, `app/admin/`, `app/core/`

4. **Given** the directory structure exists, **When** I create `app/main.py` with a FastAPI app, **Then** a `/health` endpoint returns `{"data": {"status": "ok"}, "error": null}` using the standard API envelope format

5. **Given** the app is created, **When** I create `app/config.py`, **Then** a `Settings` class using `pydantic-settings` loads all configuration from environment variables with sensible defaults for development

6. **Given** the project is complete, **When** I check `.env.example`, **Then** it contains placeholder values for all required environment variables (DATABASE_URL, REDIS_URL, JWT_SECRET_KEY, TIKTOK_MS_TOKEN, etc.)

7. **Given** the project is complete, **When** I run `uv run ruff check .` and `uv run mypy .`, **Then** both pass with zero errors

## Tasks / Subtasks

- [ ] Task 1: Initialize backend project (AC: #1)
  - [ ] Run `uv init backend --python 3.14`
  - [ ] Verify `.python-version` contains `3.14`
- [ ] Task 2: Configure dependencies (AC: #2)
  - [ ] Add core dependencies to `pyproject.toml`: `fastapi[standard]`, `sqlalchemy[asyncio]`, `aiomysql`, `alembic`, `redis`, `pydantic-settings`, `python-jose[cryptography]`, `passlib[bcrypt]`, `httpx`, `structlog`, `apscheduler`, `TikTok-Api`, `yt-dlp`
  - [ ] Add dev dependencies: `pytest`, `pytest-asyncio`, `pytest-cov`, `ruff`, `mypy`, `pre-commit`
  - [ ] Run `uv sync` and verify `.venv` is created
- [ ] Task 3: Create modular monolith directory structure (AC: #3)
  - [ ] Create `app/__init__.py`
  - [ ] Create `app/auth/__init__.py`
  - [ ] Create `app/sounds/__init__.py`
  - [ ] Create `app/scraper/__init__.py`
  - [ ] Create `app/admin/__init__.py`
  - [ ] Create `app/core/__init__.py`
- [ ] Task 4: Create FastAPI app with health endpoint (AC: #4)
  - [ ] Create `app/main.py` with FastAPI app factory
  - [ ] Implement `/health` endpoint returning standard envelope `{"data": {"status": "ok"}, "error": null}`
  - [ ] Register CORS middleware (restricted to app domain)
  - [ ] Add lifespan context manager (empty for now, will be used by APScheduler later)
- [ ] Task 5: Create configuration module (AC: #5)
  - [ ] Create `app/config.py` with `Settings(BaseSettings)` class
  - [ ] Define all config fields: `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET_KEY`, `JWT_EXPIRY_MINUTES=30`, `TIKTOK_MS_TOKEN`, `VN_PROXY_URL`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `CACHE_MAX_SIZE_GB=10`, `TRENDING_FETCH_INTERVAL_MINUTES=30`, `TRENDING_FETCH_COUNT=50`
  - [ ] Use `model_config = SettingsConfigDict(env_file=".env")` for .env loading
- [ ] Task 6: Create .env.example (AC: #6)
  - [ ] Create `.env.example` with all environment variable placeholders and comments
- [ ] Task 7: Configure linting and type checking (AC: #7)
  - [ ] Add `[tool.ruff]` section to `pyproject.toml` (target Python 3.14, line-length 120, select rules)
  - [ ] Add `[tool.mypy]` section (strict mode, ignore missing imports for third-party libs)
  - [ ] Run `uv run ruff check .` — zero errors
  - [ ] Run `uv run mypy .` — zero errors

## Dev Notes

### Architecture Compliance

- **Pattern:** Modular Monolith with Clean Architecture (Router → Service → Repository)
- **Modules:** `auth/`, `sounds/`, `scraper/`, `admin/` — each will have `router.py`, `service.py`, `repository.py`, `schemas.py`, `models.py`
- **Core:** `core/` provides shared infrastructure — `security.py`, `middleware.py`, `exceptions.py`, `redis.py`, `logging.py`, `email.py`
- **This story only creates the directory structure and `__init__.py` files.** Module contents are created in their respective epic stories.
- [Source: architecture.md#Project Structure & Boundaries]

### API Response Envelope (CRITICAL — all endpoints must follow this)

```python
# Standard success response
{"data": {...}, "error": null}

# Standard error response
{"data": null, "error": {"code": "ERROR_CODE", "message": "Human readable message"}}

# Standard list response
{"data": [...], "pagination": {"page": 1, "page_size": 20, "total": 100, "has_next": true}, "error": null}
```

- [Source: architecture.md#Format Patterns]

### Naming Conventions (CRITICAL)

- Python files/modules: `snake_case` — `router.py`, `service.py`
- Classes: `PascalCase` — `SoundService`, `UserRepository`
- Functions/variables: `snake_case` — `get_trending_sounds()`
- Constants: `UPPER_SNAKE_CASE` — `MAX_CACHE_SIZE_GB`
- Pydantic schemas: `PascalCase` with suffix — `SoundResponse`, `LoginRequest`
- [Source: architecture.md#Implementation Patterns & Consistency Rules]

### Package Manager

- **uv** (Rust-based) — replaces pip + venv
- Always use `.venv` virtual environment, never install to system Python
- Use `uv run` to execute commands within the venv
- Use `uv sync` to install/update dependencies
- Use `uv add <package>` to add new dependencies
- [Source: architecture.md#Starter Template Evaluation]

### Python Version

- **Python 3.14.3** — user's local version
- Set `.python-version` to `3.14`
- If TikTok-Api or Playwright has compatibility issues with 3.14, fallback to 3.13
- [Source: User requirement, architecture.md#Architecture Validation Results]

### Key Dependencies and Versions

| Package                     | Purpose            | Notes                           |
| --------------------------- | ------------------ | ------------------------------- |
| `fastapi[standard]`         | Web framework      | Includes uvicorn, httptools     |
| `sqlalchemy[asyncio]`       | ORM (async)        | v2.0+, AsyncSession             |
| `aiomysql`                  | MySQL async driver | For SQLAlchemy async engine     |
| `alembic`                   | DB migrations      | Versioned, reversible           |
| `redis`                     | Cache client       | async via `redis.asyncio`       |
| `pydantic-settings`         | Config management  | Loads from .env                 |
| `python-jose[cryptography]` | JWT tokens         | Encode/decode                   |
| `passlib[bcrypt]`           | Password hashing   | 12 rounds minimum               |
| `httpx`                     | Async HTTP client  | For TikTok audio download       |
| `structlog`                 | Structured logging | JSON output                     |
| `apscheduler`               | Job scheduler      | AsyncIOScheduler                |
| `TikTok-Api`                | TikTok scraping    | v7.3.2, requires Playwright     |
| `yt-dlp`                    | Audio fallback     | Backup audio source             |
| `ruff`                      | Linter + formatter | Replaces black + isort + flake8 |
| `mypy`                      | Type checker       | Strict mode                     |
| `pytest`                    | Testing            | With pytest-asyncio             |

### Project Structure Notes

This story creates the skeleton. Final structure after all epics:

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              ← Created in this story
│   ├── config.py            ← Created in this story
│   ├── database.py          ← Story 1.3
│   ├── auth/
│   │   └── __init__.py      ← Created in this story (empty)
│   ├── sounds/
│   │   └── __init__.py      ← Created in this story (empty)
│   ├── scraper/
│   │   └── __init__.py      ← Created in this story (empty)
│   ├── admin/
│   │   └── __init__.py      ← Created in this story (empty)
│   └── core/
│       └── __init__.py      ← Created in this story (empty)
├── pyproject.toml            ← Created in this story
├── .python-version           ← Created in this story
├── .env.example              ← Created in this story
└── .gitignore                ← Created in this story
```

### Anti-Patterns to Avoid

- ❌ Do NOT create database models, routers, services, or repositories — those belong to later stories
- ❌ Do NOT install packages to system Python — always use `.venv` via `uv`
- ❌ Do NOT use `pip` — use `uv` exclusively
- ❌ Do NOT create `requirements.txt` — use `pyproject.toml` with `uv`
- ❌ Do NOT hardcode any configuration values — use pydantic-settings with env vars
- ❌ Do NOT use bare `raise HTTPException` — this story doesn't create endpoints beyond `/health`, but set the pattern correctly

### References

- [Source: architecture.md#Starter Template Evaluation — Backend initialization command and dependencies]
- [Source: architecture.md#Core Architectural Decisions — Data Architecture, Infrastructure tables]
- [Source: architecture.md#Implementation Patterns & Consistency Rules — All naming and format patterns]
- [Source: architecture.md#Project Structure & Boundaries — Complete directory structure]
- [Source: epics.md#Story 1.1 — Original acceptance criteria]

## Dev Agent Record

### Agent Model Used

(to be filled by dev agent)

### Debug Log References

### Completion Notes List

### File List
