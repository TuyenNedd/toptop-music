---
stepsCompleted: [1, 2, 3, 4, 5, 6]
inputDocuments: []
workflowType: "research"
lastStep: 1
research_type: "technical"
research_topic: "TikTok-Api capabilities, limitations, and full-stack architecture for toptop-music (Vietnam market)"
research_goals: "Evaluate TikTok-Api feasibility for trending sounds/audio extraction targeting Vietnam market, determine optimal backend stack (FastAPI + MySQL), research frontend framework for web-first with future mobile scaling"
user_name: "Nedd"
date: "2026-03-25"
web_research_enabled: true
source_verification: true
---

# Research Report: Technical

**Date:** 2026-03-25
**Author:** Nedd
**Research Type:** Technical

---

## Research Overview

This technical research covers the full-stack architecture for toptop-music — a private web app for streaming TikTok trending sounds targeting the Vietnam market. The research evaluates the unofficial TikTok-Api Python wrapper, determines the optimal backend stack (FastAPI + MySQL + Redis), frontend framework (Next.js with Capacitor for future mobile), and provides production-grade security, deployment, and operational patterns. Key finding: the project is technically feasible but requires careful handling of TikTok's anti-bot measures, Vietnam IP proxying, and audio URL expiration. See the Executive Summary in the Research Synthesis section for strategic recommendations.

---

## Technical Research Scope Confirmation

**Research Topic:** TikTok-Api capabilities, limitations, and full-stack architecture for toptop-music
**Research Goals:** Evaluate TikTok-Api feasibility for trending sounds/audio extraction, determine optimal backend stack (FastAPI + MySQL), research frontend framework for web-first with future mobile scaling

**Technical Research Scope:**

- Architecture Analysis - TikTok-Api internals, Playwright-based scraping, session management
- Implementation Approaches - async patterns, caching strategies, error handling for unstable API
- Technology Stack - Backend (FastAPI, SQLAlchemy, APScheduler) + Frontend (web-first, mobile-scalable)
- Integration Patterns - TikTok-Api to backend pipeline, audio URL extraction, frontend audio player
- Performance Considerations - Playwright overhead, session pooling, audio caching vs streaming, frontend UX

**Research Methodology:**

- Current web data with rigorous source verification
- Multi-source validation for critical technical claims
- Confidence level framework for uncertain information
- Comprehensive technical coverage with architecture-specific insights

**Scope Confirmed:** 2026-03-25

---

## Technology Stack Analysis

### TikTok-Api (davidteather/TikTok-Api) — Core Data Source

**Current Version:** v7.3.2 (latest as of 2026)
**Language:** Python 3.9+
**Dependencies:** Playwright (headless browser automation)
**License:** MIT

**Capabilities confirmed via official docs and source analysis:**

- `api.trending.videos(count=N)` — Fetch trending videos (async iterator)
- `api.sound(id='...')` — Access sound/music by TikTok sound ID
- `sound.info()` — Get full sound metadata (title, author, duration, original flag)
- `sound.videos(count=N)` — Get videos using a specific sound
- `video.as_dict` — Raw JSON data dictionary including `musicInfos` with `playUrl` (direct MP3 link)

**Critical finding — Audio URL extraction:**
TikTok video data includes a `musicInfos` object containing:

- `musicId` — unique sound identifier
- `musicName` — song title
- `authorName` — artist/creator
- `playUrl` — **direct MP3 URL** (e.g., `https://p16.muscdn.com/obj/.../*.mp3`)
- `covers`, `coversMedium`, `coversLarger` — album art URLs
- `original` — whether the sound is original content

_Source: [TikTok-Api docs](https://davidteather.github.io/TikTok-Api), [Example response structure](https://gist.github.com/davidteather/0be2e495e2de54098e8f2a9594581d27)_

**Limitations and Risks (HIGH CONFIDENCE):**

1. **Anti-bot detection (Critical):** TikTok employs advanced anti-scraping including encrypted headers, behavioral detection, and real-time fraud scoring. `EmptyResponseException` is the most common issue — TikTok detects bot activity and blocks requests.
   _Source: [Scrapfly — How to Scrape TikTok 2026](https://scrapfly.io/blog/posts/how-to-scrape-tiktok-python-json)_

2. **ms_token requirement:** Requires a valid `ms_token` extracted from TikTok.com cookies. Tokens expire and need periodic manual refresh or automated rotation.

3. **Playwright overhead:** Each session launches a headless Chromium browser. Resource-hungry on small VMs — significant memory footprint per session.
   _Source: [Playwright Browser Footprint](https://datawookie.dev/blog/2025/06/playwright-browser-footprint/)_

4. **URL expiration:** Audio `playUrl` and video URLs are signed with TTL. They expire after a period (typically hours). Must download promptly or re-fetch.

5. **Rate limiting:** No official rate limits documented, but aggressive scraping triggers blocks. Residential proxies recommended for reliability.

6. **Breakage frequency:** TikTok regularly changes internal API structures. The library has historically needed updates when TikTok modifies endpoints. Maintainer is active but updates can lag.

7. **No user-authenticated routes:** Cannot access private content, user playlists, or perform any write operations.

**Alternative/Complementary tools:**

- **yt-dlp** — Can extract audio from TikTok video URLs directly (`yt-dlp -x --audio-format mp3 <url>`). Useful as fallback for audio download when `playUrl` expires.
- **Paid APIs (TikAPI, EnsembleData, TikHub)** — More reliable but cost money. Good fallback if free scraping becomes unreliable.
  _Source: [Best TikTok Scraping APIs 2026](https://www.socialkit.dev/blog/best-tiktok-scraping-api)_

### Backend Stack: FastAPI + SQLAlchemy + MySQL

**FastAPI (Python)**

- Async-native web framework, ideal for I/O-bound operations
- Native integration with TikTok-Api (same Python runtime, same async event loop)
- Auto-generated OpenAPI/Swagger docs
- Pydantic v2 for data validation
- Single codebase, single Docker image deployment

**SQLAlchemy 2.0 (Async)**

- Full async support via `AsyncSession` with `aiomysql` driver
- Mature ORM with excellent MySQL support
- Alembic for database migrations
- Type-safe query building

**aiomysql**

- Async MySQL driver for Python's asyncio
- Compatible with SQLAlchemy 2.0 async engine
- Connection string: `mysql+aiomysql://user:pass@host/db`

**APScheduler**

- Async-compatible job scheduler for Python
- Handles cron-like jobs (trending fetcher every 30-60 min)
- Integrates cleanly with FastAPI lifecycle

_Source: [FastAPI + Async SQLAlchemy guide](https://leapcell.io/blog/building-high-performance-async-apis-with-fastapi-sqlalchemy-2-0-and-asyncpg), [aiomysql docs](https://aiomysql.readthedocs.io/en/latest/)_

**Why not Node.js/NestJS:**

- TikTok-Api is Python-only → would require separate Python worker process + IPC
- Two runtimes to maintain, two Docker images, more deployment complexity
- No significant performance advantage for this use case (small whitelist app)

### Frontend Stack: Next.js (Web-First, Mobile-Scalable)

**Next.js (React framework)**

- Server-side rendering + static generation for fast initial loads
- File-based routing, API routes (can proxy backend calls)
- Built-in image/font optimization
- App Router with React Server Components (latest architecture)

**Why Next.js over plain React:**

- SSR provides faster perceived load times
- Built-in routing eliminates need for react-router
- API routes can serve as BFF (Backend-for-Frontend) proxy layer
- Better SEO if ever needed (not critical for private app, but free)

_Source: [Next.js vs React 2026 comparison](https://groovyweb.co/blog/next-js-vs-react-which-one-should-you-choose)_

**Audio Player Architecture:**

- HTML5 `<audio>` element for playback — native browser support, no plugins
- Persistent player component at app layout level (survives page navigation)
- State management via React Context or Zustand for player state (current track, queue, play/pause)
- Media Session API for OS-level media controls (lock screen, notification center)

_Source: [Persistent Music Players in React & Next.js](https://www.lukehertzler.com/blog/how-i-build-persistent-music-players-in-react-nextjs)_

**Mobile Scaling Strategy — Next.js + Capacitor:**

- **Capacitor** wraps the Next.js web app into native iOS/Android containers
- Same codebase for web and mobile — no rewrite needed
- Access to native device features (background audio, notifications) via Capacitor plugins
- Significantly faster than building separate React Native app
- Trade-off: not truly native UI, but acceptable for a music player app

_Source: [Next.js + Capacitor mobile apps](https://capgo.app/blog/building-a-native-mobile-app-with-nextjs-and-capacitor/), [NextNative comparison](https://nextnative.dev/alternatives/expo-alternative)_

**Alternative considered — React Native / Expo:**

- Would require separate codebase from web
- Better native performance for complex animations
- Overkill for this use case — music player UI is simple enough for web-based approach

### Development Tools and Deployment

**Containerization:**

- Docker with multi-stage build (Python backend + Playwright browsers)
- `mcr.microsoft.com/playwright:focal` as base image for TikTok-Api compatibility

**Storage:**

- Local filesystem (`sounds/`) for MVP
- S3-compatible storage (MinIO self-hosted or AWS S3) for production scale

**Deployment (self-hosted):**

- Single VPS (2GB+ RAM recommended due to Playwright)
- Docker Compose for orchestration (backend + MySQL + frontend)
- Nginx reverse proxy with SSL (Let's Encrypt)

### Technology Adoption Trends

**TikTok scraping landscape in 2026:**

- Free open-source tools face increasing difficulty due to ML-based bot detection
- Paid API services (TikAPI, EnsembleData, TikHub) gaining adoption as reliable alternatives
- Proxy rotation (residential proxies) becoming essential for sustained scraping
- TikTok's USDS Joint Venture (Oracle-managed) has changed data handling and anti-bot measures

_Source: [Best TikTok Scraping Tools 2026](https://research.aimultiple.com/tiktok-scraping/), [Data365 TikTok Scraper Guide](https://data365.co/blog/tiktok-follower-scraper)_

### Vietnam Market Context

**Target market:** Vietnam only — trending sounds và content phải là từ TikTok Vietnam region.

**Region-specific data fetching:**

- TikTok xác định region dựa trên: IP address, SIM card country code, app store region, device locale, và behavioral signals
- TikTok-Api trending endpoint có tham số `region` (ISO2 code) — cần set `region="VN"` để lấy trending Vietnam
- **Proxy requirement:** Để đảm bảo lấy đúng trending VN, backend nên dùng **Vietnam IP proxy** (residential proxy VN hoặc VPS đặt tại Vietnam)
- Nếu server deploy ngoài VN mà không dùng VN proxy, trending data có thể trả về content của region khác

_Source: [TikTok-Api region issue #474](https://github.com/davidteather/TikTok-Api/issues/474), [TikTok region detection](https://megadigital.ai/en/blog/how-to-change-region-on-tiktok/)_

**ms_token cho VN:**

- `ms_token` cần được lấy từ TikTok.com khi truy cập từ Vietnam IP
- Token từ region khác có thể trả về trending data không đúng VN

**Deployment implication:**

- Recommend deploy backend trên VPS tại Vietnam (hoặc Singapore gần VN) + VN residential proxy
- Giảm latency cho cả user access và TikTok scraping
- Các VPS provider phổ biến tại VN: Viettel IDC, VNPT, hoặc Singapore region của AWS/GCP/DigitalOcean

**Content characteristics:**

- TikTok VN trending sounds thường mix giữa nhạc Việt, V-pop, nhạc remix, và international hits
- Nhiều sound là original từ creators VN (không phải licensed music)
- Duration thường 15-60 giây (TikTok sound clips)

---

## Integration Patterns Analysis

### Data Pipeline: TikTok-Api → Backend → Database

**Flow 1: Trending Fetcher (Scheduled Job)**

```
[APScheduler Cron 30-60min]
    → TikTok-Api.trending.videos(count=50, region="VN")
    → Extract musicInfos from each video.as_dict
    → Upsert sound metadata to MySQL (sounds table)
    → If top trending + not cached → trigger audio download
```

**Flow 2: Audio Download & Cache**

```
[Sound marked for caching]
    → Extract playUrl from musicInfos
    → Download MP3 via httpx/aiohttp (async)
    → Save to local filesystem: sounds/{tiktok_sound_id}.mp3
    → Update DB: cached=true, file_path=path
    → Fallback: if playUrl expired → use yt-dlp as backup
```

**Flow 3: On-Demand Stream (User Request)**

```
[User plays uncached sound]
    → Backend checks DB → not cached
    → Option A: Download first, then stream (better UX for repeat plays)
    → Option B: Proxy stream directly from TikTok URL (faster first play, no local cache)
    → Recommended: Option A for sounds with high play count, Option B for one-off plays
```

**APScheduler integration with FastAPI:**

- Use `AsyncIOScheduler` initialized in FastAPI's `lifespan` context manager
- Jobs run in the same async event loop as the API server
- No separate process or message queue needed for this scale

_Source: [FastAPI + APScheduler lifespan pattern](https://openillumi.com/en/en-fastapi-periodic-task-lifespan-apscheduler/)_

### API Design: Backend REST Endpoints

**Authentication pattern:** Full JWT + OAuth2 system (see "Security, Operations & Production Readiness" section for complete details)

- OAuth2 Password flow with short-lived access tokens + long-lived refresh tokens
- RBAC: `admin` and `member` roles via FastAPI dependency injection
- Invite-only registration (admin generates invite codes)
- Multi-layer rate limiting per user via Redis-backed middleware

_Source: [FastAPI JWT/OAuth2 Guide](https://blog.greeden.me/en/2025/10/14/a-beginners-guide-to-serious-security-design-with-fastapi-authentication-authorization-jwt-oauth2-cookie-sessions-rbac-scopes-csrf-protection-and-real-world-pitfalls/)_

**Core endpoints:**

| Endpoint           | Method | Description                               |
| ------------------ | ------ | ----------------------------------------- |
| `/api/trending`    | GET    | List trending sounds (paginated, from DB) |
| `/api/sounds/{id}` | GET    | Sound metadata                            |
| `/api/stream/{id}` | GET    | Audio stream (proxy or local file)        |
| `/api/search`      | GET    | Search sounds by title/artist             |
| `/api/health`      | GET    | Health check                              |

**Audio streaming endpoint pattern:**

- If cached: `FileResponse` or `StreamingResponse` with Range header support for seeking
- If not cached: `StreamingResponse` proxying from TikTok `playUrl` with chunked transfer
- Content-Type: `audio/mpeg` for MP3
- Support HTTP Range requests for audio seeking in browser

_Source: [FastAPI StreamingResponse for media](https://www.restack.io/p/fastapi-knowledge-streamingresponse-javascript), [FastAPI file downloads](https://davidmuraya.com/blog/fastapi-file-downloads/)_

### Frontend ↔ Backend Integration

**Next.js → FastAPI communication:**

- **Option A: Direct API calls** — Frontend calls FastAPI directly (different port/domain)
  - Requires CORS configuration on FastAPI
  - Simpler setup, clear separation

- **Option B: Next.js rewrites as proxy** (Recommended)
  - `next.config.js` rewrites: `/api/*` → `http://backend:8000/api/*`
  - Browser only talks to Next.js domain → no CORS issues
  - API key injected server-side, never exposed to browser
  - Audio stream URLs also proxied → no cross-origin audio issues

_Source: [Next.js rewrites for CORS bypass](https://openillumi.com/en/en-nextjs-cors-fix-vercel-rewrites-2/), [Next.js BFF pattern](https://nextjs.org/docs/app/guides/backend-for-frontend)_

**Audio playback CORS consideration (Critical):**

- TikTok CDN URLs (`p16.muscdn.com`) do NOT set CORS headers
- HTML5 `<audio>` element can play cross-origin audio for basic playback
- BUT Web Audio API (for visualizations, equalizer) requires CORS → will output silence on cross-origin
- **Solution:** Always proxy audio through backend → same-origin, no CORS issues, and hides TikTok URLs from client

### TikTok-Api Session Management

**Session lifecycle:**

```python
async with TikTokApi() as api:
    await api.create_sessions(
        ms_tokens=[ms_token],
        num_sessions=1,
        sleep_after=3,
        browser="chromium",
        proxies=[vietnam_proxy_url]  # VN IP for correct region
    )
    # Session ready — make API calls
```

**Key integration concerns:**

1. **Session pooling:** Create 1-2 sessions at startup, reuse across requests. Don't create per-request (too slow, ~3s per session).
2. **ms_token rotation:** Store multiple tokens, rotate when one expires. Manual refresh needed (extract from browser cookies).
3. **Proxy integration:** Pass VN residential proxy to `create_sessions()` for correct region data.
4. **Error handling:** Catch `EmptyResponseException` → retry with different proxy/token. Implement exponential backoff.
5. **Playwright lifecycle:** Session holds a browser instance in memory. Must be properly closed to avoid memory leaks.

### Integration Security Patterns

> Full security architecture documented in the "Security, Operations & Production Readiness" section below. Key integration-level points:

**Authentication flow:**

```
[Client] → Authorization: Bearer <jwt_token> → [FastAPI Auth Middleware]
    → Validate JWT signature + expiration
    → Extract user_id, role from token claims
    → Inject user context into request state
    → If invalid/expired → 401 Unauthorized
    → If insufficient role → 403 Forbidden
```

**Audio URL protection:**

- Never expose TikTok CDN URLs to frontend
- All audio served through `/api/stream/{id}?token={signed}&expires={ts}`
- Signed URLs: HMAC-SHA256(secret, sound_id + user_id + expires) — time-limited, user-bound
- Backend resolves actual file path or proxy URL internally
- Referrer checking to prevent hotlinking

**Rate limiting:**

- Multi-layer: Nginx global → per-user → per-endpoint
- Redis-backed for distributed consistency
- Separate limits for auth endpoints (brute-force protection)

### Data Format Standards

**API responses:** JSON with consistent structure

```json
{
  "data": [...],
  "pagination": { "page": 1, "total": 100, "has_next": true },
  "error": null
}
```

**Sound metadata format:**

```json
{
  "id": "uuid",
  "tiktok_sound_id": "7016547803243022337",
  "title": "Sound Name",
  "artist": "Artist Name",
  "cover_url": "https://...",
  "duration_seconds": 30,
  "usage_count": 150000,
  "trend_rank": 5,
  "cached": true,
  "stream_url": "/api/stream/uuid"
}
```

---

## Security, Operations & Production Readiness

### Authentication & Authorization (Full Implementation)

**Upgrade from simple API key to proper auth system:**

**Layer 1: User Authentication (JWT + OAuth2)**

- OAuth2 Password flow with JWT tokens (FastAPI built-in support)
- Access tokens: short-lived (15-30 min), stored in memory/localStorage
- Refresh tokens: long-lived (7-30 days), stored in httpOnly secure cookie
- Password hashing: bcrypt via `passlib`
- Registration: invite-only (admin generates invite codes, not open registration)

_Source: [FastAPI JWT/OAuth2 Security Guide](https://blog.greeden.me/en/2025/10/14/a-beginners-guide-to-serious-security-design-with-fastapi-authentication-authorization-jwt-oauth2-cookie-sessions-rbac-scopes-csrf-protection-and-real-world-pitfalls/)_

**Layer 2: Role-Based Access Control (RBAC)**

- Roles: `admin`, `member`
- `admin`: manage users, invite codes, view audit logs, manage cache, system config
- `member`: browse trending, search, play/stream audio
- Implemented via FastAPI dependency injection with role-checking decorators

_Source: [FastAPI RBAC Implementation](https://www.permit.io/blog/fastapi-rbac-full-implementation-tutorial)_

**Layer 3: API Key for programmatic access (optional)**

- For future integrations (mobile app, scripts)
- Separate from user auth, tied to user account
- Revocable per-key

**DB schema upgrade:**

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  username VARCHAR(100) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  role ENUM('admin', 'member') DEFAULT 'member',
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE invite_codes (
  id UUID PRIMARY KEY,
  code VARCHAR(64) UNIQUE NOT NULL,
  created_by UUID REFERENCES users(id),
  used_by UUID REFERENCES users(id) NULL,
  expires_at TIMESTAMP NOT NULL,
  used_at TIMESTAMP NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE refresh_tokens (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  token_hash VARCHAR(255) NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  revoked BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Input Validation & Injection Prevention

**Pydantic v2 for all request validation:**

- Every endpoint uses typed Pydantic models — no raw dict/JSON access
- `response_model` on every endpoint acts as allowlist, preventing accidental data leakage
- Strict type coercion: string fields validated for length, pattern; integers for range
- Path parameters validated: sound IDs must match UUID or TikTok ID pattern

**SQL Injection prevention:**

- SQLAlchemy ORM exclusively — no raw SQL queries
- Parameterized queries via SQLAlchemy Core when needed
- Never interpolate user input into query strings

**OWASP API Security Top 10 coverage:**

| OWASP Risk                                            | Mitigation                                                           |
| ----------------------------------------------------- | -------------------------------------------------------------------- |
| API1: Broken Object Level Authorization               | Every endpoint checks resource ownership via user context            |
| API2: Broken Authentication                           | JWT + refresh token rotation, bcrypt hashing, brute-force protection |
| API3: Broken Object Property Level Authorization      | Pydantic response_model as allowlist, separate read/write schemas    |
| API4: Unrestricted Resource Consumption               | Rate limiting per user, request size limits, pagination enforced     |
| API5: Broken Function Level Authorization             | RBAC middleware, admin-only routes explicitly decorated              |
| API6: Unrestricted Access to Sensitive Business Flows | Invite-only registration, rate-limited auth endpoints                |
| API7: Server Side Request Forgery                     | No user-controlled URLs passed to backend fetchers                   |
| API8: Security Misconfiguration                       | Security headers, CORS whitelist, debug mode disabled in prod        |
| API9: Improper Inventory Management                   | OpenAPI docs disabled in production or behind admin auth             |
| API10: Unsafe Consumption of APIs                     | TikTok-Api responses validated/sanitized before DB storage           |

_Source: [OWASP API Security Top 10](https://qodex.ai/blog/owasp-top-10-for-api-security-a-complete-guide), [FastAPI Security Best Practices](https://readmedium.com/fastapi-best-security-practices-6527ce5050d9)_

### Rate Limiting & Abuse Prevention

**Multi-layer rate limiting:**

| Layer            | Scope              | Limit               | Tool                                |
| ---------------- | ------------------ | ------------------- | ----------------------------------- |
| Global           | All requests       | 1000 req/min        | Nginx `limit_req`                   |
| Per-user         | Authenticated user | 200 req/min         | `slowapi` or Redis-based middleware |
| Auth endpoints   | Login/register     | 5 req/min per IP    | `slowapi` with IP-based key         |
| Stream endpoints | Audio streaming    | 60 req/min per user | Custom middleware                   |
| Admin endpoints  | Admin operations   | 30 req/min per user | `slowapi`                           |

**Brute-force protection:**

- Failed login tracking per IP and per username
- Account lockout after 5 failed attempts (15 min cooldown)
- Progressive delay on repeated failures
- CAPTCHA consideration for repeated failures (optional, hCaptcha)

_Source: [FastAPI Rate Limiting Guide](https://www.compilenrun.com/docs/framework/fastapi/fastapi-security/fastapi-rate-limiting), [Rate Limiting with Redis](https://kindatechnical.com/api-design-development/implementing-rate-limiting-redis.html)_

### Audio Content Protection

**Signed streaming URLs:**

- `/api/stream/{id}` does not serve audio directly
- Backend generates time-limited signed URL: `/api/stream/{id}?token={hmac_signature}&expires={timestamp}`
- HMAC-SHA256 signature = `sign(secret_key, sound_id + user_id + expires_timestamp)`
- Token valid for 1-2 hours, tied to specific user and sound
- Prevents URL sharing and hotlinking

_Source: [Signed URL patterns for streaming](https://blog.cdnsun.com/secure-hls-on-cdnsun-with-url-signing-and-access-control/), [Token-based URL protection](https://www.vdocipher.com/blog/token-based-urls/)_

**Additional audio protection:**

- No direct download endpoint — stream only
- `Content-Disposition: inline` header (not attachment)
- Range request support for seeking, but no full-file download in single request
- Referrer checking: reject requests not originating from app domain
- TikTok CDN URLs never exposed to client

### HTTPS & Transport Security

**Mandatory HTTPS everywhere:**

- Nginx reverse proxy with Let's Encrypt SSL (auto-renewal via certbot)
- HSTS header: `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- HTTP → HTTPS redirect at Nginx level
- TLS 1.2+ only, modern cipher suites

**Security headers (Nginx + FastAPI middleware):**

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 0  (deprecated, rely on CSP)
Content-Security-Policy: default-src 'self'; media-src 'self'; script-src 'self'
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

### CORS Configuration (Strict)

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Explicit whitelist, never "*"
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### Structured Logging & Audit Trail

**Structured logging (JSON format):**

- Library: `structlog` for Python — structured, context-rich, JSON output
- Every log entry includes: `timestamp`, `request_id`, `user_id`, `endpoint`, `method`, `status_code`, `duration_ms`
- Correlation ID (`X-Request-ID`) propagated through all layers

**Audit trail for security-sensitive actions:**

| Event                     | Logged Fields                                    |
| ------------------------- | ------------------------------------------------ |
| User login (success/fail) | user_id, IP, user_agent, success, failure_reason |
| User registration         | user_id, invite_code_used, IP                    |
| Token refresh             | user_id, old_token_id, new_token_id              |
| Admin actions             | admin_user_id, action, target_resource, changes  |
| Sound stream access       | user_id, sound_id, cached_or_proxy, duration     |
| Rate limit triggered      | user_id, IP, endpoint, limit_exceeded            |
| Failed auth attempts      | IP, username_attempted, attempt_count            |

**Audit log storage:**

- Separate `audit_logs` table in MySQL for queryable history
- Retention: 90 days minimum
- Admin dashboard endpoint to query audit logs

```sql
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY,
  event_type VARCHAR(50) NOT NULL,
  user_id UUID REFERENCES users(id) NULL,
  ip_address VARCHAR(45),
  user_agent TEXT,
  details JSON,
  created_at TIMESTAMP DEFAULT NOW(),
  INDEX idx_event_type (event_type),
  INDEX idx_user_id (user_id),
  INDEX idx_created_at (created_at)
);
```

_Source: [FastAPI Observability Guide](https://blog.greeden.me/en/2025/12/16/fastapi-observability-practical-guide-grow-an-api-you-can-see-with-structured-logs-metrics-traces-and-error-monitoring/), [FastAPI Structured Logging](https://oneuptime.com/blog/post/2026-02-02-fastapi-structured-logging/view)_

### Monitoring & Observability

**Three pillars of observability:**

1. **Logs:** structlog → JSON → Loki (or file-based for self-hosted MVP)
2. **Metrics:** Prometheus client (`prometheus-fastapi-instrumentator`)
   - Request count, latency histograms, error rates
   - Custom metrics: cache hit ratio, TikTok-Api success rate, active sessions
3. **Traces:** OpenTelemetry (optional, add when scaling)

**Health checks:**

- `/health` — basic liveness (app running)
- `/health/ready` — readiness (DB connected, TikTok-Api session active)
- `/health/detailed` — admin-only: DB pool stats, cache stats, Playwright session status

**Alerting (self-hosted):**

- Grafana dashboards + alert rules
- Key alerts: error rate spike, TikTok-Api failures, disk space (audio cache), DB connection pool exhaustion

_Source: [FastAPI Observability Stack](https://github.com/blueswen/fastapi-observability)_

### Secret Management

- **Environment variables** for all secrets (DB credentials, JWT secret, TikTok ms_token, proxy credentials)
- `.env` file for local dev, never committed to git
- Docker secrets or mounted env files for production
- JWT secret key: minimum 256-bit, rotatable
- ms_token storage: encrypted at rest in DB or env var, with rotation mechanism
- No secrets in code, logs, or API responses

### Database Security

- Dedicated DB user with minimal privileges (no DROP, no GRANT)
- Connection via SSL/TLS to MySQL
- Connection pooling with max limits to prevent exhaustion
- Regular backups (daily automated, tested restore procedure)
- Alembic migrations versioned in git — no manual schema changes

### Frontend Security (Next.js)

- **CSP headers** configured in `next.config.js`
- **httpOnly cookies** for refresh tokens — not accessible via JavaScript
- **CSRF protection** for state-changing requests from browser
- **No sensitive data in client-side state** — API keys, tokens only in httpOnly cookies or Authorization header
- **Input sanitization** on search fields — prevent XSS
- **Subresource Integrity (SRI)** for external scripts if any
- **Next.js security headers** via `headers()` in config

---

## Architectural Patterns and Design

### System Architecture: Modular Monolith

**Pattern chosen: Modular Monolith** — not microservices, not flat monolith.

**Rationale:**

- Project scope is well-defined: trending fetcher, audio cache, streaming API, user management
- Single team (solo dev), no need for independent deployment of services
- Shared database, shared runtime — simpler ops than microservices
- Clean module boundaries allow future extraction to microservices if needed
- FastAPI's router system naturally supports modular organization

_Source: [Building Scalable Modular Monoliths with FastAPI](https://amal-babu-git.github.io/blog/coding-and-development/building-scalable-modular-monoliths-fastapi/), [FastAPI Production Patterns 2025](https://orchestrator.dev/blog/2025-1-30-fastapi-production-patterns)_

**High-level architecture:**

```
┌─────────────────────────────────────────────────────────┐
│                      Nginx (Reverse Proxy)              │
│              SSL termination, rate limiting,             │
│              static files, security headers              │
├──────────────────────┬──────────────────────────────────┤
│   Next.js Frontend   │        FastAPI Backend           │
│   (App Router)       │   ┌──────────────────────────┐   │
│                      │   │  Auth Module             │   │
│   - Trending page    │   │  (JWT, RBAC, invite)     │   │
│   - Search page      │   ├──────────────────────────┤   │
│   - Player component │   │  Sound Module            │   │
│   - Admin dashboard  │   │  (CRUD, search, stream)  │   │
│                      │   ├──────────────────────────┤   │
│                      │   │  Scraper Module          │   │
│                      │   │  (TikTok-Api, fetcher)   │   │
│                      │   ├──────────────────────────┤   │
│                      │   │  Admin Module            │   │
│                      │   │  (users, audit, config)  │   │
│                      │   └──────────────────────────┘   │
├──────────────────────┴──────────────────────────────────┤
│                    Infrastructure                        │
│   MySQL │ Redis │ Local Storage │ Playwright Runtime     │
└─────────────────────────────────────────────────────────┘
```

### Clean Architecture: Layered Design

**Three-layer architecture per module:**

```
Router Layer (API endpoints)
    ↓ Pydantic schemas for request/response
Service Layer (Business logic)
    ↓ Domain models, validation rules
Repository Layer (Data access)
    ↓ SQLAlchemy models, queries
```

**Key principles:**

- **Router** → thin, only handles HTTP concerns (parsing, status codes, response formatting)
- **Service** → all business logic, orchestration, validation beyond Pydantic
- **Repository** → all database operations, query building, no business logic
- Dependencies flow inward: Router depends on Service, Service depends on Repository
- FastAPI `Depends()` for dependency injection across all layers

_Source: [FastAPI Clean Architecture Guide](https://blog.greeden.me/en/2025/12/23/practical-fastapi-x-clean-architecture-guide-growing-a-maintainable-api-with-router-splitting-a-service-layer-and-the-repository-pattern/), [FastAPI Repository + Service Layer](https://blog.dotcs.me/posts/fastapi-dependency-injection-x-layers)_

### Backend Project Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI app factory, lifespan, middleware
│   ├── config.py                  # Settings via pydantic-settings (env vars)
│   ├── database.py                # Async engine, session factory
│   │
│   ├── auth/                      # Auth module
│   │   ├── router.py              # /auth/* endpoints
│   │   ├── service.py             # Login, register, token logic
│   │   ├── repository.py          # User/token DB queries
│   │   ├── schemas.py             # Pydantic request/response models
│   │   ├── models.py              # SQLAlchemy User, RefreshToken, InviteCode
│   │   └── dependencies.py        # get_current_user, require_role
│   │
│   ├── sounds/                    # Sound module
│   │   ├── router.py              # /sounds/*, /stream/*
│   │   ├── service.py             # Sound CRUD, streaming logic, signed URLs
│   │   ├── repository.py          # Sound DB queries
│   │   ├── schemas.py
│   │   └── models.py              # SQLAlchemy Sound model
│   │
│   ├── scraper/                   # TikTok scraper module
│   │   ├── service.py             # TikTok-Api wrapper, session management
│   │   ├── fetcher.py             # Trending fetcher (scheduled job)
│   │   ├── downloader.py          # Audio download + cache logic
│   │   └── schemas.py             # Internal data models for scraped data
│   │
│   ├── admin/                     # Admin module
│   │   ├── router.py              # /admin/* endpoints
│   │   ├── service.py             # User management, audit log queries
│   │   └── schemas.py
│   │
│   └── core/                      # Shared infrastructure
│       ├── security.py            # JWT encode/decode, password hashing, HMAC signing
│       ├── middleware.py           # Rate limiting, request logging, CORS
│       ├── exceptions.py          # Custom exception handlers
│       ├── redis.py               # Redis client setup
│       └── logging.py             # Structlog configuration
│
├── alembic/                       # Database migrations
├── tests/                         # Test suite
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── requirements.txt
```

### Frontend Architecture (Next.js App Router)

```
frontend/
├── app/
│   ├── layout.tsx                 # Root layout with persistent PlayerBar
│   ├── page.tsx                   # Home / trending page
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── search/page.tsx
│   ├── admin/
│   │   ├── layout.tsx             # Admin layout with sidebar
│   │   ├── users/page.tsx
│   │   └── audit/page.tsx
│   └── api/                       # Next.js Route Handlers (BFF proxy)
│       └── [...proxy]/route.ts    # Proxy all /api/* to FastAPI backend
│
├── components/
│   ├── player/
│   │   ├── PlayerBar.tsx          # Persistent bottom player
│   │   ├── PlayerControls.tsx     # Play/pause/skip/volume
│   │   ├── ProgressBar.tsx        # Seekable progress
│   │   └── QueueDrawer.tsx        # Play queue sidebar
│   ├── sounds/
│   │   ├── SoundCard.tsx          # Sound item in list
│   │   ├── SoundList.tsx          # Trending/search results
│   │   └── SoundDetail.tsx        # Sound detail view
│   └── ui/                        # Shared UI components (shadcn/ui)
│
├── lib/
│   ├── api.ts                     # API client (fetch wrapper with auth)
│   ├── auth.ts                    # Auth utilities (token management)
│   └── utils.ts                   # Shared utilities
│
├── stores/
│   └── player-store.ts            # Zustand store for player state
│
├── next.config.ts
├── Dockerfile
└── tailwind.config.ts
```

**Player state management (Zustand):**

- Current track, queue, play/pause state, volume, progress
- Persisted in `layout.tsx` — survives page navigation
- Media Session API integration for OS-level controls
- Zustand chosen over Redux: simpler API, less boilerplate, perfect for single-concern state

### Caching Architecture (Multi-Layer)

**Layer 1: Redis — Hot data cache**

| Data                 | TTL                | Strategy                                |
| -------------------- | ------------------ | --------------------------------------- |
| Trending sounds list | 5 min              | Cache-aside, invalidated on fetcher run |
| Sound metadata       | 30 min             | Cache-aside with TTL                    |
| User session data    | Matches JWT expiry | Write-through                           |
| Rate limit counters  | Sliding window     | Atomic increment                        |
| Search results       | 10 min             | Cache-aside with TTL                    |

**Layer 2: Filesystem — Audio file cache**

| Data                            | Strategy                                                                  |
| ------------------------------- | ------------------------------------------------------------------------- |
| Top trending audio (pre-cached) | Downloaded by scheduled fetcher, stored as `sounds/{tiktok_sound_id}.mp3` |
| On-demand audio                 | Downloaded on first play, cached for future plays                         |
| Cache eviction                  | LRU by last_accessed, max disk usage threshold (e.g., 10GB)               |
| Cache warming                   | Fetcher pre-downloads top N trending sounds every cycle                   |

**Cache invalidation strategy:**

- Trending list: invalidated every fetcher cycle (30-60 min)
- Sound metadata: TTL-based (30 min), explicit invalidation on re-fetch
- Audio files: never invalidated unless disk pressure → LRU eviction
- Redis eviction policy: `allkeys-lru` with maxmemory limit

_Source: [Redis Caching Patterns Guide](https://nerdleveltech.com/redis-caching-patterns-the-complete-guide-for-scalable-systems), [Redis Cache Invalidation](https://leapcell.io/blog/mastering-redis-cache-invalidation-strategies)_

### Database Architecture

**MySQL with read optimization:**

```sql
-- Core indexes for performance
CREATE INDEX idx_sounds_trend_rank ON sounds(trend_rank);
CREATE INDEX idx_sounds_tiktok_id ON sounds(tiktok_sound_id);
CREATE INDEX idx_sounds_cached ON sounds(cached);
CREATE INDEX idx_sounds_title_artist ON sounds(title, artist);  -- For search
CREATE INDEX idx_sounds_last_trending ON sounds(last_trending_at DESC);

-- Full-text search for Vietnamese content
ALTER TABLE sounds ADD FULLTEXT INDEX ft_sounds_search (title, artist);
```

**Connection pooling:**

- SQLAlchemy async engine with `pool_size=10`, `max_overflow=20`
- Connection recycling: `pool_recycle=3600` (1 hour)
- Pre-ping enabled to detect stale connections

**Migration strategy:**

- Alembic for all schema changes — no manual DDL
- Migrations versioned in git, auto-applied on deployment
- Rollback scripts for every migration

### Deployment Architecture

**Docker Compose production stack:**

```yaml
services:
  nginx: # Reverse proxy, SSL, static files
  frontend: # Next.js (node:20-alpine)
  backend: # FastAPI + Playwright (playwright:focal base)
  mysql: # MySQL 8.0
  redis: # Redis 7 (cache + rate limiting)
```

**Resource allocation (minimum VPS: 4GB RAM):**

| Service            | RAM   | CPU | Notes                       |
| ------------------ | ----- | --- | --------------------------- |
| Nginx              | 128MB | 0.1 | Lightweight                 |
| Frontend (Next.js) | 512MB | 0.5 | SSR rendering               |
| Backend (FastAPI)  | 1.5GB | 1.0 | Playwright browser sessions |
| MySQL              | 1GB   | 0.5 | InnoDB buffer pool          |
| Redis              | 256MB | 0.1 | In-memory cache             |
| OS + overhead      | 512MB | —   | System processes            |

**Note:** Upgraded from 2GB to 4GB RAM recommendation due to production-grade requirements (Redis, proper MySQL buffer pool, Playwright overhead).

_Source: [FastAPI Docker Deployment Guide](https://fastlaunchapi.dev/blog/fastapi-docker-deployment-guide), [FastAPI Production with Docker + Nginx](https://blog.greeden.me/en/2026/01/20/complete-guide-to-deploying-fastapi-in-production-reliable-operations-with-uvicorn-multi-workers-docker-and-a-reverse-proxy/)_

**Uvicorn configuration:**

- Workers: 2-4 (based on CPU cores, but limited by Playwright memory)
- `--loop uvloop` for better async performance
- `--limit-concurrency 100` to prevent overload
- Managed by process manager in Docker (no need for Gunicorn wrapper)

### Scalability Path

**Phase 1 (Current): Single VPS**

- All services on one machine via Docker Compose
- Local filesystem for audio cache
- Sufficient for whitelist group (10-50 users)

**Phase 2 (If needed): Vertical scaling**

- Upgrade VPS (8GB RAM, 4 CPU)
- Move audio storage to S3-compatible (MinIO self-hosted or cloud)
- Separate MySQL to managed database service

**Phase 3 (If needed): Horizontal scaling**

- Frontend on CDN/edge (Vercel or Cloudflare Pages)
- Backend behind load balancer (2+ instances)
- Redis cluster for shared state
- S3 for audio storage (shared across instances)
- Playwright sessions managed via browser pool service

### Error Handling & Resilience

**TikTok-Api failure handling:**

- Retry with exponential backoff (3 attempts, 2s/4s/8s delays)
- Fallback to cached data if TikTok is unreachable
- Circuit breaker pattern: after N consecutive failures, stop trying for cooldown period
- Alert on sustained failures (Grafana alert)
- Graceful degradation: app still works with cached data, just no new trending updates

**Audio stream failure handling:**

- If cached file corrupted → re-download from TikTok
- If TikTok URL expired → re-fetch sound info for new URL
- If all fails → return 503 with retry-after header
- Frontend shows "temporarily unavailable" with retry button

**Database failure handling:**

- Connection pool with retry logic
- Redis as fallback for read-heavy endpoints (trending list)
- Health check endpoint detects DB issues early

---

## Implementation Approaches and Technology Adoption

### Development Tooling & Workflow

**Python backend toolchain (modern 2026 stack):**

| Tool             | Purpose                      | Why                                                                       |
| ---------------- | ---------------------------- | ------------------------------------------------------------------------- |
| `uv`             | Package manager + virtualenv | Rust-based, 10-100x faster than pip, replaces pip + venv + pip-tools      |
| `ruff`           | Linter + formatter           | Rust-based, replaces black + isort + flake8 in one tool, millisecond runs |
| `mypy`           | Static type checker          | Catches type bugs before runtime, essential for production code           |
| `pre-commit`     | Git hooks                    | Runs ruff + mypy automatically before every commit                        |
| `pytest`         | Testing framework            | Async test support, FastAPI TestClient integration                        |
| `pytest-asyncio` | Async test runner            | Required for testing async SQLAlchemy + FastAPI endpoints                 |
| `alembic`        | DB migrations                | SQLAlchemy-native, versioned schema changes                               |

_Source: [Modern Python Code Quality: uv, ruff, mypy](https://simone-carolini.medium.com/modern-python-code-quality-setup-uv-ruff-and-mypy-8038c6549dcc), [Pre-commit hooks for Python](https://pydevtools.com/handbook/how-to/how-to-set-up-pre-commit-hooks-for-a-python-project/)_

**Frontend toolchain:**

| Tool                  | Purpose                                      |
| --------------------- | -------------------------------------------- |
| `pnpm` or `npm`       | Package manager                              |
| `TypeScript`          | Type safety (strict mode)                    |
| `ESLint` + `Prettier` | Linting + formatting                         |
| `Tailwind CSS`        | Utility-first styling                        |
| `shadcn/ui`           | Component library (accessible, customizable) |

### Testing Strategy

**Backend testing pyramid:**

| Level             | Tool                | Scope                                              | Coverage Target |
| ----------------- | ------------------- | -------------------------------------------------- | --------------- |
| Unit tests        | pytest              | Service layer logic, utilities, security functions | 80%+            |
| Integration tests | pytest + TestClient | API endpoints with real DB (test database)         | Key flows       |
| Scraper tests     | pytest + mocks      | TikTok-Api wrapper with mocked responses           | All error paths |
| E2E tests         | (optional)          | Full flow from API to DB                           | Critical paths  |

**Key testing patterns:**

- `httpx.AsyncClient` with FastAPI's `TestClient` for async endpoint testing
- SQLAlchemy async test sessions with transaction rollback (no test data persisted)
- Mock TikTok-Api responses for deterministic scraper tests
- Separate test database (MySQL test container or SQLite for speed)

_Source: [FastAPI Testing with pytest](https://blog.greeden.me/en/2025/08/19/how-tests-grow-robust-apis-a-complete-guide-to-automated-testing-with-fastapi-x-pytest-x-testclient/), [Pytest + FastAPI + Async SQLAlchemy](https://gist.github.com/e-kondr01/969ae24f2e2f31bd52a81fa5a1fe0f96)_

**Frontend testing:**

- Vitest for unit tests (components, stores, utilities)
- Playwright for E2E tests (critical user flows: login, play sound, search)

### CI/CD Pipeline

**GitHub Actions workflow:**

```
Push/PR → Lint (ruff + mypy) → Test (pytest) → Build Docker → Deploy
```

**Pipeline stages:**

1. **Lint & Type Check** — `ruff check .` + `mypy .` (fast, <10s)
2. **Backend Tests** — `pytest` with MySQL test container (Docker service)
3. **Frontend Tests** — `vitest --run` + `tsc --noEmit`
4. **Docker Build** — Multi-stage build, push to container registry (GHCR or Docker Hub)
5. **Deploy** — SSH to VPS, `docker compose pull && docker compose up -d`

**Branch strategy:**

- `main` — production, auto-deploy on merge
- `develop` — staging/integration
- Feature branches → PR to `develop` → PR to `main`

_Source: [FastAPI CI/CD with GitHub Actions](https://blog.greeden.me/en/2025/11/25/introduction-to-building-a-ci-cd-pipeline-with-fastapi-x-github-actions-test-automation-docker-build-container-registry-and-kubernetes-deployment/)_

### Cost Estimation & Resource Management

**Monthly operating costs (Vietnam market):**

| Item                  | Provider Options                            | Est. Cost/month    |
| --------------------- | ------------------------------------------- | ------------------ |
| VPS (4GB RAM, 2 vCPU) | LightNode VN, UltaHost VN, DigitalOcean SGP | $8-20              |
| Domain + SSL          | Namecheap + Let's Encrypt (free)            | $1-2               |
| VN Residential Proxy  | Webshare, DataImpulse, Bright Data          | $5-30 (pay-per-GB) |
| Backup storage        | Local + offsite (B2/Wasabi)                 | $1-5               |
| **Total estimated**   |                                             | **$15-57/month**   |

_Source: [Vietnam VPS providers](https://hostadvice.com/vps/vietnam/), [Vietnam proxy providers](https://proxyway.com/proxy-locations/vietnam-proxy)_

**Cost optimization tips:**

- Start with cheapest VPS tier, upgrade only when needed
- Proxy costs scale with usage — minimize by caching aggressively
- Use free tiers where available (Let's Encrypt, GitHub Actions, GHCR)
- Audio cache reduces repeated TikTok-Api calls → less proxy bandwidth

### Implementation Roadmap

**Phase 1: Foundation (Week 1-2)**

- Project scaffolding (backend + frontend)
- Database schema + Alembic migrations
- Auth module (JWT, RBAC, invite codes)
- Basic API endpoints (health, auth)
- Docker Compose setup (all services)
- CI/CD pipeline

**Phase 2: Core Features (Week 3-4)**

- TikTok-Api integration (session management, trending fetcher)
- Sound module (CRUD, search, metadata)
- Audio download + caching system
- Streaming endpoint with signed URLs
- Redis caching layer

**Phase 3: Frontend (Week 5-6)**

- Next.js setup with App Router
- Auth pages (login, register)
- Trending page with sound list
- Persistent audio player (PlayerBar)
- Search functionality
- BFF proxy configuration

**Phase 4: Polish & Production (Week 7-8)**

- Admin dashboard (user management, audit logs)
- Rate limiting + security hardening
- Structured logging + monitoring setup
- Error handling + resilience patterns
- Performance optimization
- Production deployment to VPS

**Phase 5: Mobile (Future)**

- Capacitor integration
- Native audio background playback
- Push notifications for new trending sounds
- App store deployment

### Risk Assessment & Mitigation

| Risk                                       | Severity | Probability | Mitigation                                                                    |
| ------------------------------------------ | -------- | ----------- | ----------------------------------------------------------------------------- |
| TikTok blocks scraping permanently         | High     | Medium      | Fallback to paid API (TikAPI/EnsembleData), yt-dlp as backup                  |
| ms_token expires frequently                | Medium   | High        | Token rotation mechanism, multiple tokens, monitoring alerts                  |
| Playwright memory issues on VPS            | Medium   | Medium      | Limit to 1-2 sessions, proper cleanup, monitor memory usage                   |
| Audio URLs expire before download          | Low      | Medium      | Immediate download on fetch, yt-dlp fallback                                  |
| TikTok changes data structure              | Medium   | High        | Pin TikTok-Api version, test suite catches breaking changes, monitor releases |
| VN proxy IP gets blocked                   | Medium   | Medium      | Rotate proxy providers, multiple proxy endpoints                              |
| MySQL performance with full-text search VN | Low      | Low         | Add Elasticsearch later if needed, optimize indexes                           |
| Legal/ToS risk                             | High     | Low         | Private use only, no public access, no redistribution                         |

---

## Research Synthesis

### Executive Summary

Dự án toptop-music — web app nghe nhạc từ TikTok trending sounds cho thị trường Việt Nam — là **khả thi về mặt kỹ thuật** nhưng đi kèm với rủi ro cần quản lý chặt chẽ. TikTok-Api (v7.3.2) cung cấp đủ capabilities để fetch trending videos, extract sound metadata bao gồm direct MP3 URLs (`playUrl`), và query sounds theo ID. Tuy nhiên, TikTok đang triển khai các biện pháp anti-bot ngày càng tinh vi (ML-based detection, encrypted headers, behavioral analysis), khiến scraping trở nên khó khăn hơn trong 2026.

Stack được recommend — **FastAPI (Python) + MySQL + Redis + Next.js** — tối ưu cho use case này vì: (1) TikTok-Api là Python-only, cùng runtime giảm complexity; (2) FastAPI async-native phù hợp với I/O-bound operations; (3) Next.js cho phép web-first development với path rõ ràng sang mobile qua Capacitor. Kiến trúc Modular Monolith với Clean Architecture (Router → Service → Repository) đảm bảo code maintainable mà không over-engineer.

Về bảo mật, research đã thiết kế production-grade: JWT + OAuth2 authentication, RBAC, signed streaming URLs (HMAC-SHA256), multi-layer rate limiting, OWASP API Top 10 coverage, structured audit logging, và full HTTPS with security headers. Đây không phải "app nhỏ bỏ qua security" mà là hệ thống chỉnh chu từ đầu.

**Key Technical Findings:**

- TikTok-Api có thể extract `playUrl` (direct MP3) từ `musicInfos` trong video data — đây là core capability cho project
- Audio URLs có TTL ngắn → phải download ngay hoặc dùng yt-dlp làm fallback
- Vietnam market yêu cầu VN IP proxy cho TikTok-Api sessions để lấy đúng trending VN
- Playwright headless browser cần ~1.5GB RAM → VPS tối thiểu 4GB cho production stack
- Next.js + Capacitor là path hiệu quả nhất cho web-first → mobile scaling

**Strategic Recommendations:**

1. **Bắt đầu với FastAPI + TikTok-Api prototype** — validate scraping feasibility trước khi build full system
2. **Invest vào caching sớm** — giảm dependency vào TikTok-Api, giảm proxy costs
3. **Chuẩn bị fallback plan** — paid API (TikAPI/EnsembleData) nếu free scraping bị block
4. **Deploy trên VPS Vietnam** — đúng region cho cả scraping và user latency
5. **Security-first approach** — JWT + RBAC + signed URLs + audit logs từ ngày đầu

### Technology Stack Summary

| Layer                    | Technology                     | Version |
| ------------------------ | ------------------------------ | ------- |
| Backend Framework        | FastAPI                        | Latest  |
| Backend Language         | Python                         | 3.11+   |
| ORM                      | SQLAlchemy 2.0 (async)         | Latest  |
| MySQL Driver             | aiomysql                       | Latest  |
| Database                 | MySQL                          | 8.0     |
| Cache                    | Redis                          | 7.x     |
| TikTok Data              | TikTok-Api (davidteather)      | 7.3.2   |
| Audio Fallback           | yt-dlp                         | Latest  |
| Scheduler                | APScheduler (AsyncIOScheduler) | Latest  |
| Frontend Framework       | Next.js (App Router)           | 16.x    |
| Frontend Language        | TypeScript                     | 5.x     |
| State Management         | Zustand                        | Latest  |
| UI Components            | shadcn/ui + Tailwind CSS       | Latest  |
| Mobile (Future)          | Capacitor                      | Latest  |
| Reverse Proxy            | Nginx                          | Latest  |
| Containerization         | Docker + Docker Compose        | Latest  |
| CI/CD                    | GitHub Actions                 | —       |
| Package Manager (Python) | uv                             | Latest  |
| Linter/Formatter         | ruff + mypy                    | Latest  |
| Testing                  | pytest + pytest-asyncio        | Latest  |

### Next Steps

Với research này hoàn thành, bước tiếp theo trong BMAD workflow là:

1. **`bmad-bmm-create-prd`** — Formalize research findings thành Product Requirements Document, sử dụng document này làm technical reference
2. **`bmad-bmm-create-architecture`** — Chi tiết hóa architecture decisions dựa trên patterns đã research
3. **`bmad-bmm-create-epics-and-stories`** — Chia implementation roadmap thành epics và stories

---

**Technical Research Completion Date:** 2026-03-25
**Research Period:** Comprehensive technical analysis with current 2026 sources
**Source Verification:** All technical facts cited with current sources
**Technical Confidence Level:** High — based on multiple authoritative technical sources

_This technical research document serves as the authoritative reference for the toptop-music project's technical decisions and provides the foundation for PRD and architecture documentation._
