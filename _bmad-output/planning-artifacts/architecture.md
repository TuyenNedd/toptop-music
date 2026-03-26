---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
inputDocuments:
  - "_bmad-output/planning-artifacts/prd.md"
  - "_bmad-output/planning-artifacts/ux-design-specification.md"
  - "_bmad-output/planning-artifacts/research/technical-tiktok-api-research-2026-03-25.md"
  - "clean_plan.md"
workflowType: "architecture"
project_name: "toptop-music"
user_name: "Nedd"
date: "2026-03-26"
status: "complete"
completedAt: "2026-03-26"
---

# Architecture Decision Document — toptop-music

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**
49 FRs organized into 9 domains: User Registration & Authentication (FR1-FR5), Sound Discovery & Browsing (FR6-FR10), Audio Playback (FR11-FR17), Favorites (FR18-FR21), Playlists (FR22-FR28), Administration (FR29-FR35), Data Collection & Caching (FR36-FR41), Audio Streaming (FR42-FR44), Notifications (FR45), and Playback Resilience (FR46-FR49).

The core architectural challenge is the audio streaming pipeline: TikTok-Api scraping → metadata extraction → audio download/cache → signed URL streaming → multi-source fallback chain. This is not a standard CRUD application — the data source is an unofficial, unstable external API with anti-bot measures, expiring URLs, and region-specific requirements (Vietnam IP proxy).

Dual registration paths (invite code instant activation + open sign-up with admin approval) add complexity to the auth flow beyond typical JWT implementations. Email notification on approval/rejection adds an async communication channel.

**Non-Functional Requirements:**

- Performance: cached audio < 2s, on-demand < 5s, API p95 < 200ms, search < 1s, FCP < 1.5s via SSR
- Security: HTTPS/TLS 1.2+, bcrypt (12 rounds), JWT 30min expiry, httpOnly refresh tokens, signed streaming URLs (2hr expiry), progressive login lockout, multi-layer rate limiting, OWASP API Top 10, security headers (HSTS, CSP, X-Frame-Options), CORS restricted
- Reliability: 99%+ uptime, circuit breaker on TikTok-Api, cached data fallback, DB connection retry
- Scalability: 15 concurrent users on single 4GB VPS, 10GB audio cache, 10K sound records
- Maintainability: 80%+ backend test coverage, automated CI/CD, zero-downtime deployment, structured JSON logging with correlation IDs, versioned DB migrations, env-var configuration

**Scale & Complexity:**

- Primary domain: Full-stack web application (audio streaming player)
- Complexity level: Medium-High — unofficial API dependency with anti-bot measures, multi-layer caching architecture, production-grade security, audio streaming pipeline with fallback chain
- Estimated architectural components: ~12 major components (Nginx, Next.js frontend, FastAPI backend with 4 modules, MySQL, Redis, filesystem cache, Playwright runtime, APScheduler, BFF proxy layer)

### Technical Constraints & Dependencies

- **TikTok-Api (Python-only)** — Forces Python backend; no viable Node.js alternative. Requires Playwright headless browser (~1.5GB RAM overhead per session).
- **Vietnam IP proxy requirement** — TikTok determines region by IP. Backend must route scraping through VN residential proxy for correct trending data.
- **ms_token manual refresh** — TikTok session tokens expire unpredictably, requiring manual extraction from browser cookies. No automated solution exists.
- **Audio URL TTL** — TikTok CDN URLs (`playUrl`) expire within hours. Must download immediately or re-fetch.
- **No CORS on TikTok CDN** — Audio must be proxied through backend; direct browser playback from TikTok CDN blocked for Web Audio API use cases.
- **Playwright memory footprint** — Limits concurrent scraper sessions to 1-2 on a 4GB VPS. Session pooling and proper lifecycle management essential.
- **Single developer** — Architecture must be simple enough for solo maintenance. Modular monolith over microservices.
- **Private, invite-only** — No SEO, no public API, no multi-tenant concerns. Simplifies many architectural decisions.

### Cross-Cutting Concerns Identified

1. **Authentication & Authorization** — JWT + RBAC touches every endpoint. Signed streaming URLs add audio-specific auth layer.
2. **Caching** — Multi-layer (Redis for metadata/sessions/rate-limits, filesystem for audio). Affects trending, search, streaming, and admin modules.
3. **Error Handling & Resilience** — TikTok-Api failures cascade through scraper → cache → streaming → frontend. Circuit breaker, retry, fallback patterns needed at every layer.
4. **Logging & Audit** — Structured JSON logging with correlation IDs across all modules. Separate audit trail for security-sensitive actions.
5. **Rate Limiting** — Three layers (Nginx global, per-user, per-endpoint) using Redis. Affects all API endpoints.
6. **Theme/Dark Mode** — CSS variable system with Tailwind `dark:` variant. Affects all frontend components.
7. **Persistent Player State** — Zustand store at layout level survives all navigation. Affects frontend routing and component architecture.

## Starter Template Evaluation

### Primary Technology Domain

Full-stack web application: FastAPI (Python) backend + Next.js (TypeScript) frontend, deployed as separate containers behind Nginx reverse proxy.

### Starter Options Considered

**Frontend Starters:**

- `create-next-app` (official Next.js CLI) — Standard, well-maintained, exact match for requirements. ✅ Selected.

**Backend Starters:**

- `fastapi/full-stack-fastapi-template` (Tiangolo official) — Uses PostgreSQL + SQLModel + React + Chakra UI. Too many mismatches with project requirements (MySQL, SQLAlchemy 2.0 async, Next.js frontend, Tailwind-only). Stripping and replacing core components would be more work than scaffolding from scratch. ❌ Rejected.
- `ArmanShirzad/fastapi-production-template` — Docker + CI/CD + observability focused, but opinionated about deployment targets (Render/Koyeb) and doesn't match the modular monolith structure defined in technical research. ❌ Rejected.
- Custom scaffold via `uv init` — 100% aligned with project requirements and the detailed backend structure defined in technical research. Clean start with exact dependencies needed. ✅ Selected.

### Selected Starters

#### Frontend: create-next-app (Next.js 16.x)

**Initialization Command:**

```bash
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --turbopack
```

**Architectural Decisions Provided:**

- Language & Runtime: TypeScript (strict mode), Node.js 20+
- Styling: Tailwind CSS v4 (configured, purging enabled)
- Build Tooling: Turbopack (default in Next.js 16, 2-5x faster builds)
- Routing: App Router with React Server Components
- Code Organization: `src/` directory with `app/` router structure
- Development: Hot reload via Turbopack, TypeScript checking, ESLint
- Import Aliases: `@/*` mapped to `src/*`

#### Backend: Custom Scaffold via uv (FastAPI 0.135.x)

**Initialization Command:**

```bash
uv init backend --python 3.14
```

**Runtime Environment:**

- Python 3.14.3
- Virtual environment via `.venv` (managed by `uv`, never install to system Python)
- `uv run` / `uv sync` for all execution (always uses `.venv`)

**Core Dependencies:**

```
fastapi[standard]
sqlalchemy[asyncio]
aiomysql
alembic
redis
pydantic-settings
python-jose[cryptography]
passlib[bcrypt]
httpx
structlog
apscheduler
TikTok-Api
yt-dlp
```

**Dev Dependencies:**

```
pytest
pytest-asyncio
pytest-cov
ruff
mypy
pre-commit
```

**Architectural Decisions (manual setup required):**

- Language & Runtime: Python 3.14.3, async-first, `.venv` virtual environment
- ORM: SQLAlchemy 2.0 with AsyncSession + aiomysql driver
- Database Migrations: Alembic (versioned, reversible)
- Package Manager: uv (Rust-based, replaces pip + venv, manages `.venv` automatically)
- Linting/Formatting: ruff (replaces black + isort + flake8)
- Type Checking: mypy (strict mode)
- Testing: pytest + pytest-asyncio
- Code Organization: Modular monolith — auth/, sounds/, scraper/, admin/, core/ modules, each with router/service/repository layers

**Note:** Project initialization using these commands should be the first implementation story. Backend module structure follows the Clean Architecture pattern defined in technical research (Router → Service → Repository layers).

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**

- Backend stack: FastAPI + SQLAlchemy 2.0 async + MySQL + Redis
- Frontend stack: Next.js 16.x + TypeScript + Tailwind CSS (custom components only)
- Auth: JWT + httpOnly refresh tokens + RBAC (admin/member)
- API communication: BFF proxy pattern (Next.js rewrites → FastAPI)
- Architecture pattern: Modular monolith with Clean Architecture layers
- Deployment: Docker Compose + Nginx on single VPS

**Important Decisions (Shape Architecture):**

- State management: Zustand for player state
- Animation: Framer Motion (primary), GSAP (optional for complex timelines)
- Caching: Redis (metadata/sessions) + filesystem (audio files)
- Audio streaming: Signed URLs (HMAC-SHA256), backend proxy, no direct TikTok CDN exposure
- Email: SMTP direct (Gmail/Mailgun) for account approval notifications

**Deferred Decisions (Post-MVP):**

- Elasticsearch for Vietnamese full-text search (MySQL FULLTEXT for MVP)
- S3-compatible storage for audio (local filesystem for MVP)
- Playwright E2E testing for frontend (Vitest unit tests only for MVP)
- PWA/Service Worker offline capabilities
- Capacitor mobile wrapper

### Data Architecture

| Decision           | Choice                 | Version | Rationale                                                                                                |
| ------------------ | ---------------------- | ------- | -------------------------------------------------------------------------------------------------------- |
| Primary Database   | MySQL                  | 8.0     | Defined in PRD/research. Familiar to developer, sufficient for 10K sound records                         |
| ORM                | SQLAlchemy 2.0 (async) | Latest  | Full async support via AsyncSession, mature MySQL support, Alembic integration                           |
| MySQL Driver       | aiomysql               | Latest  | Async MySQL driver compatible with SQLAlchemy 2.0 async engine                                           |
| Cache Layer        | Redis                  | 7.x     | Hot data cache (trending lists, metadata, sessions, rate limit counters)                                 |
| Audio File Storage | Local filesystem       | N/A     | `sounds/{tiktok_sound_id}.{ext}` — simple, sufficient for single VPS. Migrate to S3 post-MVP if needed   |
| Audio Format       | Preserve original      | N/A     | Keep whatever format TikTok returns (MP3 or M4A). No re-encoding — preserves original quality            |
| Migration Tool     | Alembic                | Latest  | SQLAlchemy-native, versioned, reversible migrations                                                      |
| Search             | MySQL FULLTEXT         | N/A     | `FULLTEXT INDEX` on title + artist columns. Sufficient for MVP scale. Elasticsearch deferred to post-MVP |
| Data Validation    | Pydantic v2            | Latest  | Request/response validation via schemas. `response_model` as allowlist on every endpoint                 |

**Caching Strategy:**

| Data                    | Store      | TTL                  | Pattern                                 |
| ----------------------- | ---------- | -------------------- | --------------------------------------- |
| Trending sounds list    | Redis      | 5 min                | Cache-aside, invalidated on fetcher run |
| Sound metadata          | Redis      | 30 min               | Cache-aside with TTL                    |
| User session data       | Redis      | Matches JWT expiry   | Write-through                           |
| Rate limit counters     | Redis      | Sliding window       | Atomic increment                        |
| Search results          | Redis      | 10 min               | Cache-aside with TTL                    |
| Audio files (trending)  | Filesystem | No TTL, LRU eviction | Pre-cached by scheduled fetcher         |
| Audio files (on-demand) | Filesystem | No TTL, LRU eviction | Downloaded on first play                |

**Cache Eviction:** LRU by `last_accessed` timestamp, triggered when disk usage exceeds 10GB threshold.

### Authentication & Security

| Decision            | Choice                                                                   | Rationale                                                                                  |
| ------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------ |
| Auth Method         | JWT (access) + Refresh Token (httpOnly cookie)                           | Access tokens: 30 min expiry, in-memory. Refresh tokens: 7-30 days, httpOnly secure cookie |
| Password Hashing    | bcrypt via passlib                                                       | Minimum 12 rounds, adaptive hashing                                                        |
| Authorization       | RBAC (admin, member)                                                     | FastAPI `Depends()` with role-checking dependencies                                        |
| Registration        | Dual path: invite code (instant) + open sign-up (pending approval)       | FR1 + FR2 requirements                                                                     |
| Audio Access        | Signed streaming URLs                                                    | HMAC-SHA256(secret, sound_id + user_id + expires), 2-hour expiry, user-bound               |
| Rate Limiting       | Multi-layer: Nginx global (1000/min) → per-user (200/min) → per-endpoint | Redis-backed via slowapi or custom middleware                                              |
| Login Protection    | Progressive lockout                                                      | 5 failed attempts → 15 min cooldown, tracked per IP and username                           |
| Transport           | HTTPS only                                                               | TLS 1.2+, Nginx SSL termination, Let's Encrypt, HSTS header                                |
| CORS                | Restricted                                                               | Application domain only, explicit whitelist, never `*`                                     |
| Security Headers    | Full set                                                                 | HSTS, CSP, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy    |
| Audit Logging       | Structured JSON to MySQL                                                 | Separate `audit_logs` table, 90-day retention, queryable by event/user/date                |
| Email Notifications | SMTP direct                                                              | Gmail SMTP or Mailgun SMTP for account approval/rejection emails (FR45)                    |

### API & Communication Patterns

| Decision           | Choice                     | Rationale                                                                                                              |
| ------------------ | -------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| API Style          | REST                       | Simple, well-understood, sufficient for this use case. No GraphQL complexity needed                                    |
| API Communication  | BFF Proxy                  | Next.js rewrites `/api/*` → `http://backend:8000/api/*`. No CORS issues, hidden backend, API keys injected server-side |
| API Documentation  | OpenAPI (auto-generated)   | FastAPI auto-generates Swagger/ReDoc. Disabled or admin-only in production                                             |
| Response Format    | Consistent JSON envelope   | `{ "data": ..., "pagination": {...}, "error": null }`                                                                  |
| Error Handling     | Structured error responses | Custom exception handlers, consistent error codes, no stack traces in production                                       |
| Audio Streaming    | Backend proxy              | All audio served through `/api/stream/{id}?token={signed}&expires={ts}`. Never expose TikTok CDN URLs to client        |
| Streaming Protocol | HTTP Range requests        | Support `Range` headers for audio seeking. `Content-Type: audio/mpeg` or `audio/mp4` based on file format              |

### Frontend Architecture

| Decision         | Choice                           | Version | Rationale                                                                                                                                              |
| ---------------- | -------------------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Framework        | Next.js (App Router)             | 16.x    | SSR for trending list, React Server Components, Turbopack                                                                                              |
| Language         | TypeScript                       | 5.x     | Strict mode enabled                                                                                                                                    |
| Styling          | Tailwind CSS                     | v4      | Utility-first, custom components only, no component library. `dark:` variant for theme toggle                                                          |
| State Management | Zustand                          | Latest  | Player state (current track, queue, volume, progress). Persisted at layout level                                                                       |
| Animation        | Framer Motion (primary)          | Latest  | Player expand/collapse, page transitions, heart animation, cover art transitions. GSAP available as optional for complex timeline animations if needed |
| Icons            | Lucide React                     | Latest  | Tree-shakeable, consistent style, outline default + filled for active states                                                                           |
| Testing          | Vitest                           | Latest  | Unit and component tests. E2E (Playwright) deferred to post-MVP                                                                                        |
| Audio Playback   | HTML5 `<audio>` element          | N/A     | Native browser support, persistent at layout level, Media Session API for OS controls                                                                  |
| Theme            | CSS Variables + Tailwind `dark:` | N/A     | Class-based dark mode toggle on `<html>`. Dark mode primary, light mode parallel                                                                       |
| Font             | Inter (variable)                 | Latest  | Primary font. Fallback: system font stack                                                                                                              |

**Component Architecture:**

- All components built from scratch with Tailwind utility classes
- No CSS-in-JS, no styled-components, no component library wrappers
- Responsive: mobile-first (`base` = mobile, `md:` = tablet, `lg:` = desktop)
- `prefers-reduced-motion` respected via Tailwind `motion-reduce:` variant

### Infrastructure & Deployment

| Decision                 | Choice                                           | Rationale                                                                    |
| ------------------------ | ------------------------------------------------ | ---------------------------------------------------------------------------- |
| Containerization         | Docker + Docker Compose                          | All services orchestrated: nginx, frontend, backend, mysql, redis            |
| Reverse Proxy            | Nginx                                            | SSL termination, rate limiting, static files, security headers               |
| VPS                      | Single 4GB RAM VPS (Vietnam or Singapore region) | Correct region for TikTok scraping + low user latency                        |
| SSL                      | Let's Encrypt (certbot auto-renewal)             | Free, automated HTTPS                                                        |
| CI/CD                    | GitHub Actions                                   | Push/PR → lint (ruff + mypy) → test (pytest) → build Docker → deploy         |
| Deployment               | Zero-downtime via Docker Compose rolling updates | `docker compose pull && docker compose up -d`                                |
| Monitoring               | Prometheus + Grafana                             | `prometheus-fastapi-instrumentator` for metrics. Grafana dashboards + alerts |
| Logging                  | structlog → JSON                                 | Correlation IDs, structured output. File-based for MVP, Loki optional later  |
| Secret Management        | Environment variables                            | `.env` file for dev (gitignored), Docker secrets for production              |
| Backend Server           | Uvicorn                                          | 2-4 workers, `--loop uvloop`, `--limit-concurrency 100`                      |
| Package Manager (Python) | uv                                               | Rust-based, manages `.venv` automatically, replaces pip + venv               |
| Package Manager (Node)   | npm                                              | Standard, comes with Node.js                                                 |

### Decision Impact Analysis

**Implementation Sequence:**

1. Project scaffolding (backend `uv init` + frontend `create-next-app`) + Docker Compose setup
2. Database schema + Alembic migrations
3. Auth module (JWT, RBAC, invite codes, dual registration)
4. TikTok-Api integration (session management, trending fetcher)
5. Sound module (CRUD, search, metadata) + audio caching
6. Streaming endpoint (signed URLs, Range requests, proxy)
7. Frontend: auth pages, trending page, persistent player
8. Frontend: search, favorites, playlists
9. Admin dashboard
10. Security hardening, rate limiting, monitoring
11. CI/CD pipeline, production deployment

**Cross-Component Dependencies:**

- Auth module → required by all other modules (JWT middleware, RBAC dependencies)
- Redis → required by caching, rate limiting, and session management
- TikTok-Api scraper → feeds sound module with data, triggers audio downloader
- Audio cache (filesystem) → consumed by streaming endpoint
- Zustand player store → consumed by PlayerBar, NowPlaying, QueueDrawer, all sound list components
- BFF proxy (Next.js rewrites) → all frontend API calls depend on this configuration
- Nginx → SSL, rate limiting, and routing depend on proper configuration before production

## Implementation Patterns & Consistency Rules

### Naming Patterns

**Database Naming Conventions:**

- Tables: `snake_case`, plural — `sounds`, `users`, `invite_codes`, `audit_logs`, `refresh_tokens`
- Columns: `snake_case` — `tiktok_sound_id`, `created_at`, `is_active`
- Foreign keys: `{referenced_table_singular}_id` — `user_id`, `sound_id`
- Indexes: `idx_{table}_{columns}` — `idx_sounds_trend_rank`, `idx_users_email`
- Enums: `UPPER_SNAKE_CASE` values — `'admin'`, `'member'`

**API Naming Conventions:**

- Endpoints: plural nouns, kebab-case paths — `/api/sounds`, `/api/invite-codes`, `/api/audit-logs`
- Route params: `{snake_case}` — `/api/sounds/{sound_id}`
- Query params: `snake_case` — `?page=1&page_size=20&event_type=login`
- JSON fields: `snake_case` — `{ "tiktok_sound_id": "...", "trend_rank": 5 }` (Pydantic default, no camelCase conversion)

**Backend Code Naming (Python — PEP 8):**

- Modules/files: `snake_case` — `router.py`, `service.py`, `repository.py`
- Functions/methods: `snake_case` — `get_trending_sounds()`, `create_invite_code()`
- Variables: `snake_case` — `sound_id`, `current_user`
- Classes: `PascalCase` — `SoundService`, `UserRepository`, `AuthRouter`
- Constants: `UPPER_SNAKE_CASE` — `MAX_CACHE_SIZE_GB`, `JWT_EXPIRY_MINUTES`
- Pydantic schemas: `PascalCase` with suffix — `SoundResponse`, `UserCreate`, `LoginRequest`

**Frontend Code Naming (TypeScript/React):**

- Files and folders: `kebab-case` — `player-bar.tsx`, `sound-card.tsx`, `use-player.ts`, `player-store.ts`
- Component exports: `PascalCase` — `export function PlayerBar()`, `export function SoundCard()`
- Hooks: `camelCase` with `use` prefix, file `kebab-case` — `usePlayer()` in `use-player.ts`
- Utilities: `camelCase` exports, `kebab-case` files — `formatDuration()` in `format-duration.ts`
- Store files: `kebab-case` with `-store` suffix — `player-store.ts`
- Types/Interfaces: `PascalCase`, no `I` prefix — `Sound`, `User`, `PlayerState`, `ApiResponse<T>`
- Constants: `UPPER_SNAKE_CASE` — `API_BASE_URL`, `DEFAULT_VOLUME`
- Folders: `kebab-case` — `components/player/`, `components/sound-list/`, `lib/`

### Structure Patterns

**Backend Test Organization:**
Tests in `tests/` directory mirroring `app/` module structure:

```
tests/
  auth/
    test_router.py
    test_service.py
  sounds/
    test_router.py
    test_service.py
    test_repository.py
  scraper/
    test_fetcher.py
    test_downloader.py
  conftest.py          # Shared fixtures (db session, test client, auth helpers)
```

**Frontend Test Organization:**
Co-located with source files:

```
components/
  player/
    player-bar.tsx
    player-bar.test.tsx
```

**Frontend Component Organization (by feature/domain):**

```
components/
  player/          # player-bar, now-playing, queue-drawer, progress-bar, player-controls
  sounds/          # sound-card, sound-list, sound-detail
  auth/            # login-form, register-form
  admin/           # admin-dashboard, invite-code-generator, pending-user-list, audit-log-viewer
  ui/              # toast, skeleton-loader, heart-button, trend-badge, search-bar
```

### Format Patterns

**API Response Envelope (all endpoints):**

Success (list):

```json
{
  "data": [...],
  "pagination": { "page": 1, "page_size": 20, "total": 100, "has_next": true },
  "error": null
}
```

Success (single item):

```json
{ "data": { ... }, "error": null }
```

Error:

```json
{
  "data": null,
  "error": {
    "code": "SOUND_NOT_FOUND",
    "message": "Sound with ID xyz not found"
  }
}
```

**HTTP Status Code Usage:**

- `200` — Success (GET, PUT, PATCH)
- `201` — Created (POST that creates a resource)
- `204` — No Content (DELETE, or actions with no response body)
- `400` — Validation error (bad request body or params)
- `401` — Unauthenticated (missing or invalid token)
- `403` — Forbidden (valid token but insufficient role)
- `404` — Resource not found
- `409` — Conflict (duplicate username, already favorited, etc.)
- `429` — Rate limited
- `500` — Internal server error (never expose details in production)
- `503` — Service unavailable (TikTok-Api down, with `Retry-After` header)

**Date/Time Format:**

- JSON: ISO 8601 strings with UTC timezone — `"2026-03-26T10:30:00Z"`
- Database: `TIMESTAMP` columns in MySQL (UTC)
- Frontend display: localized via `Intl.DateTimeFormat` or simple relative time ("5 phút trước")

**Error Codes (string constants):**
Format: `DOMAIN_ACTION_REASON` — `AUTH_LOGIN_INVALID_CREDENTIALS`, `SOUND_STREAM_URL_EXPIRED`, `ADMIN_INVITE_CODE_USED`

### Process Patterns

**Error Handling (Backend):**

- Custom exception classes in `core/exceptions.py` — `SoundNotFoundException(AppException)`, `AuthenticationError(AppException)`
- Base `AppException` class with `code`, `message`, `status_code` attributes
- Global exception handler registered in FastAPI catches `AppException` → returns error envelope
- Unhandled exceptions → 500 with generic message, full details logged with correlation ID
- Never expose stack traces or internal paths in production responses

**Error Handling (Frontend):**

- API client wrapper in `lib/api-client.ts` handles all HTTP errors
- 401 response → auto-refresh token via refresh endpoint → retry original request → if refresh fails → redirect to login
- Toast notifications for user-facing errors (non-blocking)
- Error boundaries at page level (`error.tsx` in App Router), not per-component
- Playback errors: silent retry → auto-skip → cached-only fallback (never modal dialogs during playback)

**Loading States:**

- Skeleton screens for list views (trending, search results, playlists)
- Inline spinner for button actions (submit, save)
- Never full-screen loading spinners or blocking overlays
- Optimistic UI for favorites: toggle heart immediately, revert on API error
- Player bar: loading state shows subtle pulse animation on cover art

**Logging (Backend — structlog):**

- Format: JSON, one line per entry
- Required fields on every log: `timestamp`, `level`, `request_id`, `module`, `message`
- Optional fields: `user_id` (if authenticated), `sound_id`, `duration_ms`, `error_detail`
- Levels: `DEBUG` (dev only), `INFO` (normal ops), `WARNING` (recoverable), `ERROR` (failures), `CRITICAL` (system down)
- Correlation ID: `X-Request-ID` header propagated through all layers, generated by Nginx if not present
- Audit events: written to `audit_logs` MySQL table (queryable), not just log files

**Environment Variables:**

- Backend: `pydantic-settings` `Settings` class, auto-loaded from `.env` file
- Frontend: `NEXT_PUBLIC_*` prefix for client-accessible vars, no prefix for server-only secrets
- Naming: `UPPER_SNAKE_CASE` — `DATABASE_URL`, `JWT_SECRET_KEY`, `REDIS_URL`, `TIKTOK_MS_TOKEN`
- `.env.example` committed to git with placeholder values, `.env` gitignored

### Enforcement Guidelines

**All AI Agents MUST:**

1. Follow naming conventions exactly as specified — no exceptions for "personal preference"
2. Use the API response envelope for every endpoint — no bare JSON responses
3. Place files in the correct directory per structure patterns — no ad-hoc locations
4. Use `snake_case` for all Python code and JSON fields — no camelCase mixing
5. Use `kebab-case` for all frontend file and folder names — no PascalCase or camelCase files
6. Include correlation ID (`request_id`) in all backend log entries
7. Handle errors via custom exception classes — no bare `raise HTTPException` with inline messages
8. Write Pydantic `response_model` for every endpoint — no untyped responses

**Anti-Patterns to Avoid:**

- ❌ `UserCard.tsx` → ✅ `user-card.tsx`
- ❌ `{ "userId": 1, "firstName": "..." }` → ✅ `{ "user_id": 1, "first_name": "..." }`
- ❌ `raise HTTPException(status_code=404, detail="not found")` → ✅ `raise SoundNotFoundException(sound_id)`
- ❌ `return {"users": [...]}` → ✅ `return {"data": [...], "pagination": {...}, "error": null}`
- ❌ Tests in random locations → ✅ Backend: `tests/{module}/test_{layer}.py`, Frontend: co-located `*.test.tsx`
- ❌ `console.log` in production → ✅ structlog with proper levels and correlation IDs

## Project Structure & Boundaries

### Complete Project Directory Structure

```
toptop-music/
├── .github/
│   └── workflows/
│       ├── ci-backend.yml
│       └── ci-frontend.yml
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                          # FastAPI app factory, lifespan, middleware registration
│   │   ├── config.py                        # pydantic-settings Settings class
│   │   ├── database.py                      # Async engine, session factory, connection pool
│   │   │
│   │   ├── auth/                            # Auth module
│   │   │   ├── __init__.py
│   │   │   ├── router.py                    # /api/auth/* endpoints
│   │   │   ├── service.py                   # Login, register, token logic, invite code validation
│   │   │   ├── repository.py                # User, RefreshToken, InviteCode DB queries
│   │   │   ├── schemas.py                   # LoginRequest, RegisterRequest, TokenResponse, UserResponse
│   │   │   ├── models.py                    # SQLAlchemy: User, RefreshToken, InviteCode
│   │   │   └── dependencies.py              # get_current_user, require_role("admin"), require_role("member")
│   │   │
│   │   ├── sounds/                          # Sound module
│   │   │   ├── __init__.py
│   │   │   ├── router.py                    # /api/sounds/*, /api/stream/*
│   │   │   ├── service.py                   # Sound CRUD, search, streaming logic, signed URL generation
│   │   │   ├── repository.py                # Sound, Favorite, Playlist DB queries
│   │   │   ├── schemas.py                   # SoundResponse, SoundListResponse, SearchQuery, StreamToken
│   │   │   ├── models.py                    # SQLAlchemy: Sound, Favorite, Playlist, PlaylistSound
│   │   │   └── stream.py                    # Audio streaming helpers (Range requests, proxy, file stream)
│   │   │
│   │   ├── scraper/                         # TikTok scraper module (no router — background only)
│   │   │   ├── __init__.py
│   │   │   ├── service.py                   # TikTok-Api wrapper, session pool management
│   │   │   ├── fetcher.py                   # Trending fetcher (APScheduler job)
│   │   │   ├── downloader.py                # Audio download + cache logic, yt-dlp fallback
│   │   │   └── schemas.py                   # Internal data models for scraped TikTok data
│   │   │
│   │   ├── admin/                           # Admin module
│   │   │   ├── __init__.py
│   │   │   ├── router.py                    # /api/admin/* endpoints
│   │   │   ├── service.py                   # User management, audit log queries, system health
│   │   │   └── schemas.py                   # AdminDashboardResponse, AuditLogEntry, InviteCodeCreate
│   │   │
│   │   └── core/                            # Shared infrastructure (no business logic)
│   │       ├── __init__.py
│   │       ├── security.py                  # JWT encode/decode, password hashing, HMAC signing
│   │       ├── middleware.py                 # Rate limiting, request logging, correlation ID
│   │       ├── exceptions.py                # AppException base + domain exceptions
│   │       ├── redis.py                     # Redis client setup + cache helpers
│   │       ├── logging.py                   # structlog configuration, JSON formatter
│   │       └── email.py                     # SMTP email sender (approval/rejection notifications)
│   │
│   ├── alembic/
│   │   ├── alembic.ini
│   │   ├── env.py
│   │   └── versions/
│   │
│   ├── tests/
│   │   ├── conftest.py                      # Shared fixtures: async db session, test client, auth helpers
│   │   ├── auth/
│   │   │   ├── test_router.py
│   │   │   └── test_service.py
│   │   ├── sounds/
│   │   │   ├── test_router.py
│   │   │   ├── test_service.py
│   │   │   └── test_repository.py
│   │   ├── scraper/
│   │   │   ├── test_fetcher.py
│   │   │   └── test_downloader.py
│   │   └── admin/
│   │       └── test_router.py
│   │
│   ├── sounds/                              # Audio file cache directory (gitignored)
│   ├── pyproject.toml
│   ├── .python-version                      # 3.14
│   ├── Dockerfile
│   ├── .env.example
│   └── .gitignore
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── globals.css                  # Tailwind imports + CSS variable tokens
│   │   │   ├── layout.tsx                   # Root layout: PlayerBar + TabBar/Sidebar persistent
│   │   │   ├── page.tsx                     # Home / trending page (SSR)
│   │   │   ├── error.tsx                    # Global error boundary
│   │   │   ├── loading.tsx                  # Global loading (skeleton)
│   │   │   ├── (auth)/
│   │   │   │   ├── login/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── register/
│   │   │   │       └── page.tsx
│   │   │   ├── search/
│   │   │   │   └── page.tsx
│   │   │   ├── library/
│   │   │   │   ├── page.tsx                 # Library overview (playlists + favorites)
│   │   │   │   ├── favorites/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── playlists/
│   │   │   │       ├── page.tsx
│   │   │   │       └── [id]/
│   │   │   │           └── page.tsx
│   │   │   └── admin/
│   │   │       ├── layout.tsx               # Admin layout (admin-only route guard)
│   │   │       ├── page.tsx                 # Admin dashboard
│   │   │       ├── users/
│   │   │       │   └── page.tsx
│   │   │       ├── invite-codes/
│   │   │       │   └── page.tsx
│   │   │       └── audit-logs/
│   │   │           └── page.tsx
│   │   │
│   │   ├── components/
│   │   │   ├── player/
│   │   │   │   ├── player-bar.tsx
│   │   │   │   ├── now-playing.tsx
│   │   │   │   ├── player-controls.tsx
│   │   │   │   ├── progress-bar.tsx
│   │   │   │   └── queue-drawer.tsx
│   │   │   ├── sounds/
│   │   │   │   ├── sound-card.tsx
│   │   │   │   └── sound-list.tsx
│   │   │   ├── auth/
│   │   │   │   ├── login-form.tsx
│   │   │   │   └── register-form.tsx
│   │   │   ├── admin/
│   │   │   │   ├── admin-dashboard.tsx
│   │   │   │   ├── invite-code-generator.tsx
│   │   │   │   ├── pending-user-list.tsx
│   │   │   │   ├── audit-log-viewer.tsx
│   │   │   │   └── scraper-status.tsx
│   │   │   ├── navigation/
│   │   │   │   ├── tab-bar.tsx
│   │   │   │   └── sidebar.tsx
│   │   │   └── ui/
│   │   │       ├── toast.tsx
│   │   │       ├── skeleton-loader.tsx
│   │   │       ├── heart-button.tsx
│   │   │       ├── trend-badge.tsx
│   │   │       └── search-bar.tsx
│   │   │
│   │   ├── lib/
│   │   │   ├── api-client.ts                # Fetch wrapper with auth, token refresh, error handling
│   │   │   ├── auth.ts                      # Auth utilities (token storage, refresh logic)
│   │   │   └── utils.ts                     # Shared utilities (formatDuration, formatDate, cn)
│   │   │
│   │   ├── stores/
│   │   │   └── player-store.ts              # Zustand: current track, queue, volume, progress
│   │   │
│   │   ├── hooks/
│   │   │   ├── use-player.ts
│   │   │   ├── use-auth.ts
│   │   │   └── use-favorites.ts
│   │   │
│   │   └── types/
│   │       ├── sound.ts
│   │       ├── user.ts
│   │       ├── player.ts
│   │       └── api.ts
│   │
│   ├── public/
│   │   ├── favicon.ico
│   │   └── manifest.json                    # PWA manifest
│   │
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── package.json
│   ├── Dockerfile
│   ├── .env.example
│   ├── .env.local
│   └── .gitignore
│
├── nginx/
│   ├── nginx.conf
│   └── conf.d/
│       └── default.conf
│
├── docker-compose.yml                       # Production: nginx, frontend, backend, mysql, redis
├── docker-compose.dev.yml                   # Dev overrides: hot reload, debug ports
├── .env.example
├── .gitignore
└── README.md
```

### Architectural Boundaries

**API Boundaries:**

- Frontend → Next.js rewrites → FastAPI backend (BFF proxy pattern)
- All `/api/*` requests proxied through Next.js to `http://backend:8000/api/*`
- Auth boundary: `dependencies.py` — every protected endpoint uses `Depends(get_current_user)` or `Depends(require_role("admin"))`
- Stream boundary: `/api/stream/{id}` requires signed URL token (HMAC-SHA256) — separate from JWT auth

**Module Boundaries (Backend):**

- Each module (`auth/`, `sounds/`, `scraper/`, `admin/`) is self-contained: router → service → repository → schemas → models
- Cross-module communication through service layer only — never direct repository access across modules
- `core/` provides shared infrastructure (security, middleware, exceptions, redis, logging) — no business logic
- Scraper module has no router — only invoked by APScheduler and admin module's service layer

**Data Boundaries:**

- Repository layer is the ONLY layer that touches the database
- Redis access through `core/redis.py` helpers only
- Audio files accessed only through `sounds/stream.py`
- TikTok-Api accessed only through `scraper/service.py`

### Requirements to Structure Mapping

| FR Domain                      | Backend Module                          | Frontend Pages                                  | Frontend Components                                                         |
| ------------------------------ | --------------------------------------- | ----------------------------------------------- | --------------------------------------------------------------------------- |
| FR1-FR5: Auth & Registration   | `auth/`                                 | `(auth)/login/`, `(auth)/register/`             | `auth/login-form`, `auth/register-form`                                     |
| FR6-FR10: Sound Discovery      | `sounds/`                               | `page.tsx` (home), `search/`                    | `sounds/sound-card`, `sounds/sound-list`, `ui/search-bar`, `ui/trend-badge` |
| FR11-FR17: Audio Playback      | `sounds/stream.py`                      | Root `layout.tsx`                               | `player/*` (all player components)                                          |
| FR18-FR21: Favorites           | `sounds/`                               | `library/favorites/`                            | `ui/heart-button`, `sounds/sound-list`                                      |
| FR22-FR28: Playlists           | `sounds/`                               | `library/playlists/`, `library/playlists/[id]/` | `sounds/sound-list`                                                         |
| FR29-FR35: Administration      | `admin/`                                | `admin/*` (all admin pages)                     | `admin/*` (all admin components)                                            |
| FR36-FR41: Data Collection     | `scraper/`                              | N/A (background jobs)                           | N/A                                                                         |
| FR42-FR44: Audio Streaming     | `sounds/stream.py`, `core/security.py`  | N/A (player handles)                            | `player/player-bar` (audio element)                                         |
| FR45: Email Notifications      | `core/email.py`, `admin/service.py`     | N/A                                             | N/A                                                                         |
| FR46-FR49: Playback Resilience | `sounds/stream.py`, `sounds/service.py` | N/A (player handles)                            | `player/player-bar`, `ui/toast`                                             |

### Data Flow

```
[User Browser]
    ↓ HTTPS
[Nginx] → rate limiting, SSL termination, security headers
    ↓
[Next.js Frontend] → SSR trending page, serve static assets
    ↓ /api/* rewrites (BFF proxy)
[FastAPI Backend]
    ├── auth/ → JWT validation → [MySQL: users, refresh_tokens, invite_codes]
    ├── sounds/ → metadata queries → [Redis cache] → [MySQL: sounds, favorites, playlists]
    ├── sounds/stream → signed URL validation → [Filesystem: sounds/] or [TikTok CDN proxy]
    ├── scraper/ → [TikTok-Api + Playwright] → [MySQL: sounds] → [Filesystem: sounds/]
    └── admin/ → [MySQL: audit_logs, users] → [Redis: system stats]

[APScheduler] → every 30-60 min → scraper/fetcher → trending data + audio pre-cache
```

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:**
All technology choices are compatible within their ecosystems:

- Backend: FastAPI 0.135.x + SQLAlchemy 2.0 async + aiomysql + Redis 7.x + APScheduler — all async-native, same Python event loop
- Frontend: Next.js 16.x + TypeScript + Tailwind v4 + Zustand + Framer Motion + Lucide React — standard React ecosystem, no conflicts
- BFF proxy: Next.js rewrites → FastAPI eliminates CORS, hides backend URLs, enables server-side API key injection
- Infrastructure: Docker Compose orchestrates all 5 services (nginx, frontend, backend, mysql, redis) on single VPS
- No version conflicts detected between any chosen technologies

**Pattern Consistency:** ✅

- Naming conventions are internally consistent: `snake_case` for Python/DB/JSON, `kebab-case` for frontend files/folders, `PascalCase` for component exports and Python classes
- API response envelope format is uniform across all endpoints
- Error handling follows same pattern in both backend (custom exceptions → global handler) and frontend (API client wrapper → toast/retry)
- Logging format consistent via structlog JSON with correlation IDs

**Structure Alignment:** ✅

- Project structure directly implements the modular monolith decision with Clean Architecture layers
- Each backend module has router/service/repository separation as specified
- Frontend component organization by feature domain matches the FR groupings
- Test organization mirrors source structure (backend: `tests/{module}/`, frontend: co-located)

### Requirements Coverage Validation ✅

**Functional Requirements Coverage (49/49):**

| FR Range  | Domain              | Architectural Support                                                                 | Status     |
| --------- | ------------------- | ------------------------------------------------------------------------------------- | ---------- |
| FR1-FR5   | Auth & Registration | `auth/` module (router, service, repository, models)                                  | ✅ Covered |
| FR6-FR10  | Sound Discovery     | `sounds/` module + Redis cache + MySQL FULLTEXT                                       | ✅ Covered |
| FR11-FR17 | Audio Playback      | `sounds/stream.py` + frontend `player/` + Zustand store                               | ✅ Covered |
| FR18-FR21 | Favorites           | `sounds/` repository (Favorite model) + `ui/heart-button`                             | ✅ Covered |
| FR22-FR28 | Playlists           | `sounds/` repository (Playlist, PlaylistSound models) + frontend `library/playlists/` | ✅ Covered |
| FR29-FR35 | Administration      | `admin/` module + frontend `admin/` pages                                             | ✅ Covered |
| FR36-FR41 | Data Collection     | `scraper/` module (fetcher + downloader) + APScheduler                                | ✅ Covered |
| FR42-FR44 | Audio Streaming     | `sounds/stream.py` + `core/security.py` (HMAC signing)                                | ✅ Covered |
| FR45      | Email Notifications | `core/email.py` (SMTP) + `admin/service.py`                                           | ✅ Covered |
| FR46-FR49 | Playback Resilience | `sounds/stream.py` (fallback chain) + frontend player (retry/skip/cached-only)        | ✅ Covered |

**Non-Functional Requirements Coverage:**

| NFR Category                               | Architectural Support                                                    | Status     |
| ------------------------------------------ | ------------------------------------------------------------------------ | ---------- |
| Performance (cached < 2s, API p95 < 200ms) | Redis caching, SSR, audio pre-cache, filesystem streaming                | ✅ Covered |
| Security (JWT, RBAC, signed URLs, OWASP)   | `core/security.py`, `auth/dependencies.py`, Nginx headers, rate limiting | ✅ Covered |
| Reliability (99%+ uptime, fallback chain)  | Circuit breaker, yt-dlp fallback, cached data fallback, DB retry         | ✅ Covered |
| Scalability (15 users, 10GB cache)         | Single 4GB VPS, vertical scaling path, modular monolith extraction path  | ✅ Covered |
| Maintainability (80%+ coverage, CI/CD)     | pytest suite, GitHub Actions, structlog, Alembic migrations              | ✅ Covered |

### Implementation Readiness Validation ✅

**Decision Completeness:** All critical decisions documented with specific technology versions. Implementation patterns cover naming, structure, format, and process categories with concrete examples and anti-patterns.

**Structure Completeness:** Complete directory tree with every file annotated. All modules, components, pages, and configuration files specified. No placeholder directories.

**Pattern Completeness:** All identified conflict points addressed. Enforcement guidelines with 8 mandatory rules. Anti-pattern examples provided for common mistakes.

### Gap Analysis Results

**No Critical Gaps Found.**

**Minor Items (non-blocking):**

1. **Python 3.14 + TikTok-Api/Playwright compatibility** — Python 3.14 is very new. TikTok-Api targets 3.9+, should work, but Playwright wheels for 3.14 need verification during implementation. Fallback: Python 3.13 if issues arise.

2. **Playlist sound reorder** — UX spec mentions drag-to-reorder in queue drawer, but no explicit FR for playlist sound ordering. Can be added during playlist implementation as a natural extension of FR23-FR24.

3. **WebSocket** — PRD explicitly states "No WebSocket needed" for MVP. Correct decision. If real-time admin notifications needed post-MVP, architecture supports adding WebSocket without structural changes.

### Architecture Completeness Checklist

**✅ Requirements Analysis**

- [x] Project context thoroughly analyzed (49 FRs, NFRs, 6 user journeys)
- [x] Scale and complexity assessed (medium-high, 15 users, single VPS)
- [x] Technical constraints identified (TikTok-Api, VN proxy, Playwright memory)
- [x] Cross-cutting concerns mapped (auth, caching, resilience, logging, rate limiting, theme, player state)

**✅ Starter Template Evaluation**

- [x] Frontend: `create-next-app` with TypeScript + Tailwind + App Router + Turbopack
- [x] Backend: Custom scaffold via `uv init` with Python 3.14.3 + `.venv`
- [x] Rationale documented for rejecting Tiangolo full-stack template

**✅ Architectural Decisions**

- [x] All critical decisions documented with versions (18 decisions across 5 categories)
- [x] Technology stack fully specified (backend, frontend, infrastructure)
- [x] Integration patterns defined (BFF proxy, signed URLs, Redis caching)
- [x] Performance considerations addressed (caching strategy, SSR, pre-cache)

**✅ Implementation Patterns**

- [x] Naming conventions established (database, API, backend code, frontend code)
- [x] Structure patterns defined (test organization, component organization)
- [x] Format patterns specified (API envelope, HTTP status codes, date format, error codes)
- [x] Process patterns documented (error handling, loading states, logging, env vars)
- [x] Enforcement guidelines with 8 mandatory rules and anti-pattern examples

**✅ Project Structure**

- [x] Complete directory structure defined (every file annotated)
- [x] Component boundaries established (module isolation, layer separation)
- [x] Integration points mapped (BFF proxy, Redis, filesystem, TikTok-Api)
- [x] Requirements to structure mapping complete (49 FRs → specific files/directories)
- [x] Data flow diagram provided

### Architecture Readiness Assessment

**Overall Status:** READY FOR IMPLEMENTATION

**Confidence Level:** High — all 49 FRs mapped, all NFRs addressed, no critical gaps, comprehensive patterns defined.

**Key Strengths:**

- Complete FR-to-structure mapping ensures no requirements fall through cracks
- Multi-layer caching strategy addresses performance targets
- Production-grade security from day one (not bolted on later)
- Clean Architecture layers enable testability and maintainability
- Modular monolith allows future extraction without rewrite

**Areas for Future Enhancement:**

- Elasticsearch for Vietnamese full-text search (post-MVP, if MySQL FULLTEXT insufficient)
- S3-compatible storage for audio files (when scaling beyond single VPS)
- Playwright E2E tests for frontend (post-MVP)
- PWA offline capabilities and Capacitor mobile wrapper (vision phase)
