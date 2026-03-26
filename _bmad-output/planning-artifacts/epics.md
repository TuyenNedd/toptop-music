---
stepsCompleted: [1, 2, 3, 4]
inputDocuments:
  - "_bmad-output/planning-artifacts/prd.md"
  - "_bmad-output/planning-artifacts/architecture.md"
  - "_bmad-output/planning-artifacts/ux-design-specification.md"
---

# toptop-music - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for toptop-music, decomposing the requirements from the PRD, UX Design, and Architecture into implementable stories.

## Requirements Inventory

### Functional Requirements

- FR1: Visitors can register using an invite code for instant account activation
- FR2: Visitors can register without an invite code, creating a pending account awaiting admin approval
- FR3: Registered users can log in with username/email and password
- FR4: Authenticated users can log out from any device
- FR5: The system maintains authenticated sessions that renew automatically without requiring re-login
- FR6: Members can view a paginated list of trending sounds from TikTok Vietnam
- FR7: Members can see sound metadata (title, artist, cover art, duration, usage count, trend rank)
- FR8: Members can search sounds by title or artist name
- FR9: The system displays an informative message explaining search limitations and suggesting alternatives when search returns no results
- FR10: Members can view sound details including trending rank changes over time and days on trending list
- FR11: Members can play any sound from the trending list, search results, favorites, or playlists
- FR12: Members can pause, resume, skip to next, and go to previous sound
- FR13: Members can adjust playback volume
- FR14: Members can seek to any position within a playing sound
- FR15: Members can add sounds to a play queue
- FR16: Members can view and manage the current play queue
- FR17: The player persists across page navigation without interrupting playback
- FR18: Members can mark any sound as a favorite
- FR19: Members can remove a sound from favorites
- FR20: Members can view their complete favorites list
- FR21: Members can play all favorites as a continuous playlist
- FR22: Members can create named playlists
- FR23: Members can add sounds to a playlist
- FR24: Members can remove sounds from a playlist
- FR25: Members can rename a playlist
- FR26: Members can delete a playlist
- FR27: Members can view all their playlists
- FR28: Members can play an entire playlist continuously
- FR29: Admins can view a dashboard with system health, user stats, cache stats, and scraper status
- FR30: Admins can generate invite codes with configurable expiration
- FR31: Admins can view and approve or reject pending user registrations
- FR32: Admins can activate or deactivate existing user accounts
- FR33: Admins can view audit logs filtered by event type, user, or date range
- FR34: Admins can view and manage TikTok-Api scraper status (session health, last fetch time)
- FR35: Admins can trigger manual trending data refresh
- FR36: The system can automatically fetch trending sounds from TikTok Vietnam at configurable intervals
- FR37: The system can extract and store sound metadata including audio URLs from TikTok data
- FR38: The system can pre-download and cache audio files for top trending sounds
- FR39: The system can download and cache audio on-demand when a user plays an uncached sound
- FR40: The system can manage cache storage with automatic eviction when disk limits are reached
- FR41: The system can retrieve audio from alternative sources when primary audio URLs are unavailable or expired
- FR42: The system supports audio seeking to any position during streaming playback of cached files
- FR43: The system can proxy-stream uncached audio from TikTok sources
- FR44: The system restricts audio access to authenticated users with time-limited, user-specific authorization that rejects expired or unauthorized requests
- FR45: The system sends email notifications to users when their pending account is approved or rejected by an admin
- FR46: The system automatically retries audio playback from alternative sources when primary playback fails
- FR47: The system skips to the next queued sound when a sound is temporarily unavailable after retry attempts
- FR48: The system can filter playback to cached-only sounds when external audio sources are unreachable
- FR49: The system displays non-disruptive status messages during playback recovery without interrupting the listening experience

### Non-Functional Requirements

- NFR1: Cached audio playback starts within 2 seconds of user action
- NFR2: On-demand audio playback starts within 5 seconds
- NFR3: API metadata responses complete within 200ms at p95
- NFR4: Search results return within 1 second
- NFR5: Trending list page renders (FCP) within 1.5 seconds via SSR
- NFR6: System supports 15 concurrent users without performance degradation
- NFR7: All data transmitted over HTTPS (TLS 1.2+)
- NFR8: Passwords hashed with bcrypt (minimum 12 rounds)
- NFR9: JWT access tokens expire within 30 minutes
- NFR10: Refresh tokens stored in httpOnly secure cookies
- NFR11: All API endpoints require authentication except registration and login
- NFR12: Audio streaming URLs are signed with HMAC-SHA256 and expire within 2 hours
- NFR13: Failed login attempts trigger progressive lockout (5 attempts, 15 min cooldown)
- NFR14: Multi-layer rate limiting: global (Nginx), per-user, per-endpoint
- NFR15: All security-sensitive actions logged to audit trail
- NFR16: OWASP API Security Top 10 mitigations implemented
- NFR17: Security headers enforced (HSTS, CSP, X-Content-Type-Options, X-Frame-Options)
- NFR18: CORS restricted to application domain only
- NFR19: System uptime target: 99%+
- NFR20: TikTok-Api failures handled gracefully with cached data fallback
- NFR21: Circuit breaker on TikTok-Api: stops requests after consecutive failures, auto-recovers
- NFR22: Database connection pool with automatic retry on transient failures
- NFR23: Initial capacity: 15 concurrent users on single 4GB VPS
- NFR24: Audio cache supports up to 10GB of stored sounds
- NFR25: Architecture supports vertical scaling as first scaling step
- NFR26: 80%+ backend test coverage (unit + integration)
- NFR27: Automated CI/CD pipeline (lint, test, build, deploy)
- NFR28: Zero-downtime deployment via container orchestration rolling updates
- NFR29: Structured JSON logging with correlation IDs for debugging
- NFR30: Database migrations managed with versioned, reversible migration tooling
- NFR31: All configuration via environment variables (no hardcoded secrets)

### Additional Requirements (from Architecture)

- AR1: Project scaffolding uses `create-next-app` for frontend and `uv init` for backend with Python 3.14.3 and `.venv` virtual environment
- AR2: Backend follows Modular Monolith with Clean Architecture (Router → Service → Repository layers) across 4 modules: auth, sounds, scraper, admin
- AR3: BFF proxy pattern: Next.js rewrites `/api/*` → FastAPI backend — no direct browser-to-backend communication
- AR4: Docker Compose orchestrates 5 services: nginx, frontend, backend, mysql, redis
- AR5: Nginx handles SSL termination, global rate limiting, security headers, and reverse proxy
- AR6: Redis serves as hot data cache (trending lists, metadata, sessions, rate limit counters)
- AR7: Audio files stored on local filesystem (`sounds/{tiktok_sound_id}.{ext}`) with LRU eviction at 10GB threshold
- AR8: APScheduler (AsyncIOScheduler) runs trending fetcher as cron job within FastAPI lifespan
- AR9: All API responses use consistent JSON envelope: `{ "data": ..., "pagination": {...}, "error": null }`
- AR10: Custom exception classes in `core/exceptions.py` with global exception handler — no bare `raise HTTPException`
- AR11: structlog with JSON output, correlation IDs (`X-Request-ID`), and audit events to MySQL `audit_logs` table
- AR12: GitHub Actions CI/CD: lint (ruff + mypy) → test (pytest) → build Docker → deploy
- AR13: Frontend files/folders use `kebab-case`, component exports use `PascalCase`
- AR14: Pydantic `response_model` required on every endpoint — no untyped responses
- AR15: Vietnam IP proxy required for TikTok-Api sessions to get correct VN trending data

### UX Design Requirements

- UX-DR1: Implement TikTok-inspired color token system as CSS variables with dark mode primary and light mode parallel — 14 semantic color tokens (primary #25F4EE, secondary #FE2C55, bg, surface, surface-hover, surface-active, text, text-secondary, text-tertiary, border, success, warning, error)
- UX-DR2: Implement Inter variable font as primary with system font fallback stack, JetBrains Mono for admin monospace — 7-step type scale from text-xs (12px) to text-3xl (30px)
- UX-DR3: Build persistent PlayerBar component (64px mobile, 90px desktop) fixed at bottom — mini controls (cover art, title/artist, play/pause, heart, progress) that survives all page navigation
- UX-DR4: Build NowPlaying full-screen view — swipe up from PlayerBar on mobile, click to expand on desktop — large cover art (280-320px), full controls, queue access
- UX-DR5: Build QueueDrawer slide-from-right panel with ordered sound list and drag-to-reorder capability
- UX-DR6: Build SoundCard component — cover art (48-56px) + title + artist + duration + heart icon + trend rank badge — states: default, playing (cyan border), hover, loading
- UX-DR7: Build SearchBar component — sticky top position, always visible, instant results as-you-type, clear button, loading indicator
- UX-DR8: Build TabBar (mobile bottom navigation, 4 tabs: Home, Search, Library, Admin) and Sidebar (desktop left, 256px) with active state cyan indicators
- UX-DR9: Build HeartButton with Framer Motion scale + color fill animation (outline → filled red #FE2C55) — single tap toggle, instant visual feedback
- UX-DR10: Build TrendBadge component — rank indicator (#1, #2...) with usage count, highlighted style for top-3
- UX-DR11: Build Toast notification system — non-disruptive, slides from top, auto-dismisses (3s info, 5s error), supports info/success/warning/error variants
- UX-DR12: Build SkeletonLoader component — pulsing gray shapes matching SoundCard and list layouts for loading states
- UX-DR13: Implement responsive breakpoints: mobile (320-767px), tablet (768-1023px), desktop (1024px+) with layout changes per UX spec platform strategy table
- UX-DR14: Implement touch optimization — minimum 44x44px tap targets, swipe up on player bar, swipe right on sound card for queue, long press for context menu, pull-to-refresh on trending
- UX-DR15: Implement keyboard navigation — Tab order (search → sound list → player controls → navigation), Space/Enter for play/pause, arrow keys for volume/seek, Escape to close modals
- UX-DR16: Implement screen reader support — ARIA labels on all interactive elements, player state announcements, trend rank announcements, live regions for playback status
- UX-DR17: Implement focus management — visible focus ring (2px cyan, 2px offset), focus trap in modals, focus return on modal close
- UX-DR18: Implement `prefers-reduced-motion` support — disable Framer Motion animations, replace with instant state changes, keep essential color feedback
- UX-DR19: Implement auto-queue behavior — tapping a sound from any list queues all subsequent sounds, music never stops unless user pauses or queue exhausts
- UX-DR20: Implement playback resilience UX — silent retry indicator ("Đang thử lại..."), graceful skip with ⚠️ icon, cached-only fallback toast, non-disruptive inline messages
- UX-DR21: Implement dual registration UX — invite code path (pre-filled from link, instant activation) and open sign-up path (pending approval screen, "chờ admin duyệt" message)
- UX-DR22: Implement empty states for Favorites ("No favorites yet. Tap ❤️..."), Playlists ("No playlists yet..."), Search no results ("No sounds found. Trending updates every 30-60 min."), Queue empty
- UX-DR23: Implement sound crossfade transitions (200ms overlap) between tracks for seamless continuous playback
- UX-DR24: Implement Media Session API integration for OS-level media controls (lock screen, notification center)

### FR Coverage Map

- FR1: Epic 2 - Register with invite code
- FR2: Epic 2 - Register without invite code (pending approval)
- FR3: Epic 2 - Login with username/email and password
- FR4: Epic 2 - Logout from any device
- FR5: Epic 2 - Auto-renewing authenticated sessions
- FR6: Epic 4 - View paginated trending sounds list
- FR7: Epic 4 - View sound metadata
- FR8: Epic 4 - Search sounds by title/artist
- FR9: Epic 4 - No-results message with alternatives
- FR10: Epic 4 - Sound details with trending history
- FR11: Epic 5 - Play any sound from any list
- FR12: Epic 5 - Pause, resume, skip, previous
- FR13: Epic 5 - Adjust volume
- FR14: Epic 5 - Seek to any position
- FR15: Epic 5 - Add sounds to play queue
- FR16: Epic 5 - View and manage play queue
- FR17: Epic 5 - Player persists across navigation
- FR18: Epic 6 - Mark sound as favorite
- FR19: Epic 6 - Remove sound from favorites
- FR20: Epic 6 - View favorites list
- FR21: Epic 6 - Play all favorites continuously
- FR22: Epic 6 - Create named playlists
- FR23: Epic 6 - Add sounds to playlist
- FR24: Epic 6 - Remove sounds from playlist
- FR25: Epic 6 - Rename playlist
- FR26: Epic 6 - Delete playlist
- FR27: Epic 6 - View all playlists
- FR28: Epic 6 - Play entire playlist continuously
- FR29: Epic 8 - Admin dashboard (health, stats, cache, scraper)
- FR30: Epic 2 - Generate invite codes with expiration
- FR31: Epic 2 - Approve/reject pending registrations
- FR32: Epic 2 - Activate/deactivate user accounts
- FR33: Epic 8 - View audit logs with filters
- FR34: Epic 8 - View/manage scraper status
- FR35: Epic 8 - Trigger manual trending refresh
- FR36: Epic 3 - Auto-fetch trending sounds from TikTok VN
- FR37: Epic 3 - Extract and store sound metadata
- FR38: Epic 3 - Pre-download and cache top trending audio
- FR39: Epic 3 - On-demand audio download and cache
- FR40: Epic 3 - Cache storage management with eviction
- FR41: Epic 3 - Retrieve audio from alternative sources
- FR42: Epic 5 - Audio seeking during streaming
- FR43: Epic 5 - Proxy-stream uncached audio
- FR44: Epic 5 - Signed URL audio access restriction
- FR45: Epic 2 - Email notification on approval/rejection
- FR46: Epic 7 - Auto-retry from alternative sources
- FR47: Epic 7 - Skip to next on unavailable sound
- FR48: Epic 7 - Filter to cached-only when sources unreachable
- FR49: Epic 7 - Non-disruptive status messages during recovery

## Epic List

### Epic 1: Project Foundation & Infrastructure

Users (developers) can scaffold, build, and deploy the complete project stack locally and in production. This epic establishes the monorepo structure, Docker Compose orchestration, CI/CD pipeline, database schema, and all shared infrastructure (logging, error handling, middleware, Redis) that every subsequent epic depends on.
**FRs covered:** None directly (enables all FRs)
**ARs covered:** AR1, AR2, AR3, AR4, AR5, AR6, AR7, AR8, AR9, AR10, AR11, AR12, AR13, AR14
**NFRs addressed:** NFR7, NFR14, NFR17, NFR18, NFR27, NFR28, NFR29, NFR30, NFR31

### Epic 2: User Authentication & Registration

Visitors can register via invite code (instant activation) or open sign-up (pending admin approval), log in securely, and maintain auto-renewing sessions. Admins can generate invite codes, approve/reject pending users, and manage user accounts. Email notifications sent on approval/rejection.
**FRs covered:** FR1, FR2, FR3, FR4, FR5, FR30, FR31, FR32, FR45
**NFRs addressed:** NFR8, NFR9, NFR10, NFR11, NFR13, NFR15, NFR16
**UX-DRs:** UX-DR21

### Epic 3: TikTok Data Pipeline & Audio Caching

The system automatically fetches trending sounds from TikTok Vietnam at configurable intervals, extracts and stores sound metadata, pre-downloads audio for top trending sounds, handles on-demand caching, manages disk storage with LRU eviction, and retrieves audio from alternative sources (yt-dlp) when primary URLs expire.
**FRs covered:** FR36, FR37, FR38, FR39, FR40, FR41
**ARs covered:** AR15
**NFRs addressed:** NFR20, NFR21, NFR22

### Epic 4: Sound Discovery & Browsing

Members can browse a paginated trending sounds list (SSR), view sound metadata (title, artist, cover art, duration, usage count, trend rank), search by title/artist with instant results, see helpful no-results messages, and view sound details with trending history. This is the core content discovery experience.
**FRs covered:** FR6, FR7, FR8, FR9, FR10
**NFRs addressed:** NFR3, NFR4, NFR5
**UX-DRs:** UX-DR1, UX-DR2, UX-DR6, UX-DR7, UX-DR8, UX-DR10, UX-DR12, UX-DR13, UX-DR22

### Epic 5: Audio Playback & Persistent Player

Members can play any sound with full controls (play/pause, skip, volume, seek), manage a play queue with auto-queue behavior, and enjoy uninterrupted playback across all page navigation. Includes the persistent PlayerBar, full-screen NowPlaying view, QueueDrawer, signed URL streaming, and audio proxy. This is the core listening experience.
**FRs covered:** FR11, FR12, FR13, FR14, FR15, FR16, FR17, FR42, FR43, FR44
**NFRs addressed:** NFR1, NFR2, NFR12
**UX-DRs:** UX-DR3, UX-DR4, UX-DR5, UX-DR9, UX-DR14, UX-DR15, UX-DR16, UX-DR17, UX-DR18, UX-DR19, UX-DR23, UX-DR24

### Epic 6: Favorites & Playlists

Members can mark/unmark sounds as favorites, view their favorites list, play all favorites continuously, create/rename/delete playlists, add/remove sounds from playlists, and play entire playlists. This makes the app feel personal and curated.
**FRs covered:** FR18, FR19, FR20, FR21, FR22, FR23, FR24, FR25, FR26, FR27, FR28
**UX-DRs:** UX-DR22

### Epic 7: Playback Resilience

The system gracefully handles playback failures: auto-retry from alternative sources, automatic skip to next sound after failed retries, cached-only fallback mode when external sources are unreachable, and non-disruptive status messages throughout recovery. Users experience uninterrupted listening even during TikTok outages.
**FRs covered:** FR46, FR47, FR48, FR49
**UX-DRs:** UX-DR11, UX-DR20

### Epic 8: Admin Dashboard & System Management

Admins can view a comprehensive dashboard (system health, user stats, cache stats, scraper status), browse audit logs with filters (event type, user, date range), monitor TikTok-Api scraper health, and trigger manual trending data refreshes. Full operational visibility and control.
**FRs covered:** FR29, FR33, FR34, FR35
**NFRs addressed:** NFR6, NFR15, NFR19, NFR23, NFR24, NFR25, NFR26

## Epic 1: Project Foundation & Infrastructure

Scaffold, build, and deploy the complete project stack locally and in production. Establishes monorepo structure, Docker Compose orchestration, CI/CD pipeline, database setup, and all shared infrastructure.

### Story 1.1: Backend Project Scaffolding

As a developer,
I want to initialize the FastAPI backend project with proper structure and dependencies,
So that I have a working backend foundation to build features on.

**Acceptance Criteria:**

**Given** no backend project exists
**When** I run `uv init backend --python 3.14` and install core dependencies
**Then** the backend has the modular monolith structure (app/auth/, app/sounds/, app/scraper/, app/admin/, app/core/) with `__init__.py` files
**And** `pyproject.toml` contains all core and dev dependencies
**And** `.python-version` is set to `3.14`
**And** `uv sync` creates `.venv` and installs all dependencies successfully
**And** a minimal `app/main.py` creates a FastAPI app with a `/health` endpoint returning `{"status": "ok"}`
**And** `app/config.py` uses pydantic-settings to load configuration from environment variables
**And** `.env.example` contains all required environment variable placeholders

### Story 1.2: Frontend Project Scaffolding

As a developer,
I want to initialize the Next.js frontend project with TypeScript and Tailwind CSS,
So that I have a working frontend foundation to build UI on.

**Acceptance Criteria:**

**Given** no frontend project exists
**When** I run `npx create-next-app@latest frontend` with TypeScript, Tailwind, ESLint, App Router, src directory, and Turbopack options
**Then** the frontend has the App Router structure under `src/app/`
**And** Tailwind CSS is configured with the TikTok-inspired color token system (CSS variables for primary, secondary, bg, surface, text, etc.) in `globals.css`
**And** `tailwind.config.ts` extends theme with custom colors, spacing, and `darkMode: 'class'`
**And** Inter variable font is configured as the primary font
**And** the root `layout.tsx` includes dark mode class on `<html>` and basic page structure
**And** `next.config.ts` includes rewrites for `/api/*` → `http://localhost:8000/api/*` (BFF proxy)
**And** `.env.example` contains required environment variable placeholders
**And** `npm run dev` starts the development server successfully

### Story 1.3: Database Setup & Initial Migration

As a developer,
I want to set up MySQL database connection with async SQLAlchemy and Alembic migrations,
So that I have a working database layer for all modules.

**Acceptance Criteria:**

**Given** the backend project exists from Story 1.1
**When** I configure the database connection
**Then** `app/database.py` creates an async SQLAlchemy engine with `aiomysql` driver and connection pooling (pool_size=10, max_overflow=20, pool_recycle=3600)
**And** Alembic is initialized with `alembic/` directory, `alembic.ini`, and async-compatible `env.py`
**And** a health check endpoint `/health/ready` verifies database connectivity
**And** `alembic revision --autogenerate` and `alembic upgrade head` work correctly

### Story 1.4: Redis Setup & Core Infrastructure

As a developer,
I want to set up Redis connection and shared core infrastructure (logging, exceptions, middleware),
So that all modules have consistent error handling, logging, and caching.

**Acceptance Criteria:**

**Given** the backend project exists
**When** I configure core infrastructure
**Then** `app/core/redis.py` creates an async Redis client with connection helpers
**And** `app/core/logging.py` configures structlog with JSON output, correlation IDs, and log levels
**And** `app/core/exceptions.py` defines `AppException` base class and global exception handler returning consistent error envelope
**And** `app/core/middleware.py` injects `X-Request-ID` correlation ID into every request
**And** all API responses follow the envelope format `{"data": ..., "pagination": {...}, "error": null}`
**And** Redis health is included in `/health/ready` endpoint

### Story 1.5: Docker Compose & Local Development Environment

As a developer,
I want a Docker Compose setup that runs all services locally,
So that I can develop and test the full stack on my machine.

**Acceptance Criteria:**

**Given** backend and frontend projects exist
**When** I run `docker compose -f docker-compose.dev.yml up`
**Then** all 5 services start: nginx, frontend, backend, mysql, redis
**And** MySQL is accessible with the configured credentials and database
**And** Redis is accessible on the configured port
**And** Backend `/health` and `/health/ready` endpoints return success
**And** Frontend dev server is accessible through Nginx
**And** BFF proxy works: frontend `/api/health` routes to backend `/health`
**And** Hot reload works for both backend (uvicorn --reload) and frontend (Turbopack)

### Story 1.6: CI/CD Pipeline

As a developer,
I want automated CI/CD via GitHub Actions,
So that every push is linted, tested, built, and deployable.

**Acceptance Criteria:**

**Given** the project is in a GitHub repository
**When** a push or PR is made
**Then** `ci-backend.yml` runs: ruff check → mypy → pytest with MySQL service container
**And** `ci-frontend.yml` runs: npm run lint → tsc --noEmit → npm run build
**And** on merge to main, Docker images are built and pushed to container registry
**And** pipeline fails fast on first error with clear error messages

## Epic 2: User Authentication & Registration

Visitors can register via invite code or open sign-up, log in securely, and maintain auto-renewing sessions. Admins can manage invite codes, approve/reject pending users, and manage accounts. Email notifications on approval/rejection.

### Story 2.1: User Registration with Invite Code

As a visitor,
I want to register using an invite code for instant account activation,
So that I can immediately start using the app.

**Acceptance Criteria:**

**Given** I have a valid, unexpired invite code
**When** I submit registration with username, email, password, and invite code
**Then** my account is created with role "member" and status "active"
**And** the invite code is marked as used with my user ID and timestamp
**And** passwords are hashed with bcrypt (12 rounds)
**And** the `users` and `invite_codes` tables are created via Alembic migration
**And** duplicate username or email returns 409 Conflict with appropriate error code
**And** expired or already-used invite codes return 400 with clear error message

### Story 2.2: User Registration without Invite Code (Pending Approval)

As a visitor,
I want to register without an invite code and await admin approval,
So that I can request access even without an invitation.

**Acceptance Criteria:**

**Given** I do not have an invite code
**When** I submit registration with username, email, and password (no invite code)
**Then** my account is created with role "member" and status "pending"
**And** I see a message: "Account created. Awaiting admin approval."
**And** attempting to log in with a pending account returns 403 with message "Account pending approval"

### Story 2.3: User Login & JWT Session Management

As a registered user,
I want to log in with my username/email and password and maintain a secure session,
So that I can access the app without re-authenticating frequently.

**Acceptance Criteria:**

**Given** I have an active account
**When** I submit valid credentials (username or email + password)
**Then** I receive a JWT access token (30 min expiry) in the response body
**And** a refresh token (7 day expiry) is set as an httpOnly secure cookie
**And** the `refresh_tokens` table is created via Alembic migration
**And** failed login attempts are tracked per IP and username
**And** after 5 failed attempts, the account is locked for 15 minutes with 429 response
**And** all login attempts (success and failure) are logged to `audit_logs` table

### Story 2.4: Token Refresh & Logout

As an authenticated user,
I want my session to renew automatically and to log out when needed,
So that I stay logged in seamlessly but can end my session securely.

**Acceptance Criteria:**

**Given** I have a valid refresh token cookie
**When** my access token expires and the frontend calls `/api/auth/refresh`
**Then** a new access token is returned and the refresh token is rotated (old one revoked)
**And** if the refresh token is expired or revoked, 401 is returned
**When** I call `/api/auth/logout`
**Then** my refresh token is revoked in the database
**And** the httpOnly cookie is cleared
**And** logout is logged to audit trail

### Story 2.5: Admin Invite Code Management

As an admin,
I want to generate invite codes with configurable expiration,
So that I can control who gets access to the app.

**Acceptance Criteria:**

**Given** I am authenticated as an admin
**When** I call POST `/api/admin/invite-codes` with expiration days
**Then** a unique invite code is generated and stored with expiry timestamp
**And** I can view all invite codes with their status (unused, used, expired)
**And** non-admin users receive 403 Forbidden
**And** invite code generation is logged to audit trail

### Story 2.6: Admin User Approval & Account Management

As an admin,
I want to approve/reject pending users and activate/deactivate accounts,
So that I control who can access the app.

**Acceptance Criteria:**

**Given** I am authenticated as an admin
**When** I view pending users via GET `/api/admin/users?status=pending`
**Then** I see a list of pending registrations with username, email, and registration date
**When** I approve a pending user via PUT `/api/admin/users/{id}/approve`
**Then** the user's status changes to "active" and an approval email is sent via SMTP
**When** I reject a pending user via PUT `/api/admin/users/{id}/reject`
**Then** the user's status changes to "rejected" and a rejection email is sent
**And** I can deactivate active users (status → "inactive") and reactivate them
**And** all admin actions are logged to audit trail

### Story 2.7: Registration & Login Frontend Pages

As a visitor,
I want registration and login pages with intuitive UI,
So that I can create an account and sign in easily.

**Acceptance Criteria:**

**Given** I navigate to the app
**When** I visit `/login`
**Then** I see a login form with username/email and password fields and a "Log in" button
**And** a link to the registration page
**When** I visit `/register`
**Then** I see two paths: "I have an invite code" and "Sign up for approval"
**And** the invite code path shows: username, email, password, invite code (pre-filled from URL query param if present)
**And** the approval path shows: username, email, password
**And** form validation shows errors below inputs in red on blur
**And** submit button shows loading spinner during API call
**And** successful invite registration redirects to home page
**And** successful approval registration shows "Pending approval" screen
**And** the pages follow kebab-case file naming and use Tailwind with dark mode support

## Epic 3: TikTok Data Pipeline & Audio Caching

The system automatically fetches trending sounds from TikTok Vietnam, extracts metadata, downloads and caches audio, with fallback sources and cache management.

### Story 3.1: TikTok-Api Session Management & Trending Fetcher

As the system,
I want to connect to TikTok-Api with Vietnam proxy and fetch trending sounds on a schedule,
So that the database always has fresh trending data from TikTok Vietnam.

**Acceptance Criteria:**

**Given** the backend is running with valid ms_token and VN proxy configured
**When** the APScheduler cron job triggers (configurable interval, default 30 min)
**Then** TikTok-Api creates a Playwright session with the VN proxy
**And** trending videos are fetched with `region="VN"` (configurable count, default 50)
**And** sound metadata is extracted from each video's `musicInfos` (musicId, musicName, authorName, playUrl, covers, duration, original flag)
**And** the `sounds` table is created via Alembic migration with all metadata fields
**And** sounds are upserted (insert new, update existing) with `trend_rank` and `last_trending_at`
**And** `usage_count` is updated from TikTok data
**And** errors are caught with retry (3 attempts, exponential backoff) and logged
**And** `EmptyResponseException` triggers session rotation logic
**And** fetcher status (last run, success/failure, sounds fetched) is stored in Redis for admin dashboard

### Story 3.2: Audio Download & Pre-Cache System

As the system,
I want to download and cache audio files for top trending sounds,
So that playback is instant for popular content.

**Acceptance Criteria:**

**Given** trending sounds have been fetched and stored in the database
**When** the fetcher completes a cycle
**Then** the top N uncached trending sounds (configurable, default 20) are queued for download
**And** audio is downloaded from `playUrl` via httpx async and saved to `sounds/{tiktok_sound_id}.{ext}` preserving original format
**And** the `sounds` table is updated: `cached=true`, `file_path=path`, `cached_at=now`
**And** if `playUrl` download fails (expired URL), yt-dlp is used as fallback
**And** download errors are logged with sound ID and error details
**And** the `sounds/` directory is created if it doesn't exist

### Story 3.3: On-Demand Audio Caching

As the system,
I want to download and cache audio on-demand when a user plays an uncached sound,
So that any sound becomes cached after first play.

**Acceptance Criteria:**

**Given** a user requests playback of an uncached sound
**When** the streaming endpoint detects the sound is not cached
**Then** the audio is downloaded from `playUrl` (or yt-dlp fallback) and saved to filesystem
**And** the sound record is updated with `cached=true` and `file_path`
**And** the audio is streamed to the user while downloading (or after download completes)
**And** concurrent requests for the same uncached sound don't trigger duplicate downloads

### Story 3.4: Cache Storage Management & Eviction

As the system,
I want to manage audio cache storage with automatic eviction,
So that disk usage stays within limits.

**Acceptance Criteria:**

**Given** audio files are being cached on the filesystem
**When** total cache size exceeds the configured threshold (default 10GB)
**Then** the least recently accessed files are evicted (LRU by `last_accessed_at` timestamp)
**And** evicted files have their `cached` flag set to `false` and `file_path` cleared in the database
**And** currently playing files are not evicted
**And** cache stats (total size, file count, eviction count) are available via Redis for admin dashboard

## Epic 4: Sound Discovery & Browsing

Members can browse trending sounds, view metadata, search by title/artist, and see sound details — the core content discovery experience.

### Story 4.1: Trending Sounds API & SSR Page

As a member,
I want to see a paginated list of trending sounds from TikTok Vietnam,
So that I can discover what's popular right now.

**Acceptance Criteria:**

**Given** I am authenticated and trending data exists in the database
**When** I visit the home page
**Then** I see a paginated list of trending sounds sorted by `trend_rank`
**And** the trending list is server-side rendered (SSR) for fast initial load (FCP < 1.5s target)
**And** the API endpoint GET `/api/sounds/trending` returns paginated results with the standard envelope format
**And** trending data is served from Redis cache (5 min TTL) with fallback to database
**And** pagination supports `page` and `page_size` query params (default page_size=20)

### Story 4.2: Sound Card Component & Metadata Display

As a member,
I want to see sound metadata in an attractive card format,
So that I can quickly identify sounds I want to listen to.

**Acceptance Criteria:**

**Given** trending sounds are displayed on the page
**When** I view the sound list
**Then** each sound shows: cover art (48px mobile, 56px desktop), title, artist, duration, usage count, and trend rank badge
**And** the SoundCard component (`sound-card.tsx`) follows kebab-case naming
**And** trend rank badges show #1, #2, #3 with highlighted style, standard style for others
**And** cover art uses Next.js Image component with lazy loading and responsive sizes
**And** the component supports states: default, playing (cyan left border), hover, loading (skeleton)
**And** dark mode and light mode render correctly using CSS variable tokens

### Story 4.3: Sound Search

As a member,
I want to search sounds by title or artist name,
So that I can find specific sounds I'm looking for.

**Acceptance Criteria:**

**Given** I am on any page with the search bar visible
**When** I type a query in the search bar
**Then** results appear as I type (debounced, 300ms delay)
**And** the API endpoint GET `/api/sounds/search?q={query}` searches title and artist using MySQL FULLTEXT
**And** search results are cached in Redis (10 min TTL)
**And** results return within 1 second
**And** the SearchBar component (`search-bar.tsx`) is sticky at the top, always visible
**And** it includes a clear button and loading indicator
**When** search returns no results
**Then** I see: "No sounds found. Trending updates every 30-60 min." with a "Browse Trending" CTA

### Story 4.4: Navigation Components (TabBar & Sidebar)

As a member,
I want consistent navigation across the app,
So that I can easily switch between Home, Search, Library, and Admin sections.

**Acceptance Criteria:**

**Given** I am authenticated
**When** I view the app on mobile (< 768px)
**Then** I see a bottom TabBar with 4 tabs: Home, Search, Library, Admin (admin tab only visible for admin role)
**And** the active tab has a cyan indicator
**And** the TabBar is fixed above the PlayerBar (when visible)
**When** I view the app on desktop (≥ 1024px)
**Then** I see a left Sidebar (256px) with navigation links
**And** the active link has a cyan left border indicator
**And** navigation components use Lucide React icons
**And** page transitions use Framer Motion fade + slide (200ms)

## Epic 5: Audio Playback & Persistent Player

Members can play sounds with full controls, manage a play queue, and enjoy uninterrupted playback across all navigation — the core listening experience.

### Story 5.1: Audio Streaming Backend (Signed URLs & Proxy)

As the system,
I want to serve audio securely through signed URLs with proxy streaming,
So that only authenticated users can access audio and TikTok CDN URLs are never exposed.

**Acceptance Criteria:**

**Given** a member requests audio playback
**When** the frontend requests a stream URL
**Then** the backend generates a signed URL: `/api/stream/{sound_id}?token={hmac}&expires={ts}`
**And** the HMAC-SHA256 signature is computed from `secret + sound_id + user_id + expires`
**And** signed URLs expire after 2 hours
**And** `core/security.py` contains the HMAC signing and verification logic
**And** `sounds/stream.py` serves cached files with `Content-Type: audio/mpeg` or `audio/mp4` based on format
**And** HTTP Range requests are supported for audio seeking
**And** uncached sounds are proxy-streamed from TikTok CDN through the backend
**And** expired or invalid tokens return 403 Forbidden
**And** stream access is logged to audit trail

### Story 5.2: Persistent PlayerBar & Audio Engine

As a member,
I want a persistent player bar at the bottom of every page that never interrupts when I navigate,
So that I can browse the app while music keeps playing.

**Acceptance Criteria:**

**Given** I tap any sound to play
**When** the sound starts playing
**Then** the PlayerBar slides up from the bottom (Framer Motion, 200ms ease-out)
**And** the PlayerBar shows: cover art (40px), title/artist (truncated), play/pause button, heart button, progress bar
**And** the PlayerBar is fixed at the bottom: 64px on mobile, 90px on desktop
**And** the HTML5 `<audio>` element is rendered in the root `layout.tsx` and persists across all page navigation
**And** Zustand `player-store.ts` manages: current track, queue, volume, progress, play/pause state
**And** the currently playing sound is highlighted in any visible list (cyan left border)
**And** Media Session API is integrated for OS-level controls (lock screen, notification center)

### Story 5.3: Full-Screen Now Playing View

As a member,
I want to expand the player to a full-screen view with large cover art and full controls,
So that I can enjoy an immersive listening experience.

**Acceptance Criteria:**

**Given** the PlayerBar is visible and a sound is playing
**When** I swipe up on the PlayerBar (mobile) or click to expand (desktop)
**Then** a full-screen NowPlaying view appears with Framer Motion slide-up animation
**And** it shows: large cover art (280px mobile, 320px desktop), title, artist, full progress bar (seekable), play/pause, skip next/previous, volume control, queue access button
**And** I can dismiss it by swiping down (mobile) or clicking outside/pressing Escape (desktop)
**And** focus is trapped within the NowPlaying view when open
**And** `prefers-reduced-motion` disables animations and uses instant state changes

### Story 5.4: Play Queue & Auto-Queue Behavior

As a member,
I want sounds to auto-queue when I tap one from a list, and to manage my queue,
So that music plays continuously without me having to manually queue each sound.

**Acceptance Criteria:**

**Given** I am viewing a list of sounds (trending, search results, playlist, favorites)
**When** I tap a sound to play
**Then** that sound starts playing and all subsequent sounds in the list are added to the queue
**And** the QueueDrawer (`queue-drawer.tsx`) slides from the right showing the ordered queue
**And** I can view the current queue with the playing sound highlighted
**And** I can remove sounds from the queue
**And** when the queue exhausts, the PlayerBar stays visible showing the last played sound
**And** the queue state persists in Zustand store (survives navigation, lost on browser close)

### Story 5.5: Player Controls & Accessibility

As a member,
I want full playback controls with keyboard and screen reader support,
So that I can control playback regardless of how I interact with the app.

**Acceptance Criteria:**

**Given** a sound is playing
**When** I interact with player controls
**Then** play/pause toggles playback, skip next/previous navigate the queue, volume slider adjusts volume, progress bar is seekable to any position
**And** sound crossfade transitions (200ms overlap) play between tracks for seamless listening
**And** keyboard navigation works: Space/Enter for play/pause, arrow keys for volume/seek, Escape to close NowPlaying
**And** all player buttons have ARIA labels ("Play", "Pause", "Skip to next", etc.)
**And** player state changes are announced to screen readers via live regions
**And** all interactive elements meet minimum 44x44px tap target
**And** visible focus ring (2px cyan, 2px offset) appears on keyboard navigation

## Epic 6: Favorites & Playlists

Members can save favorite sounds and create/manage personal playlists — making the app feel personal and curated.

### Story 6.1: Favorites Backend & Heart Button

As a member,
I want to mark sounds as favorites with a single tap,
So that I can save sounds I love for quick access.

**Acceptance Criteria:**

**Given** I am authenticated and viewing a sound
**When** I tap the heart icon on a SoundCard or PlayerBar
**Then** the sound is added to my favorites (POST `/api/sounds/{id}/favorite`)
**And** the heart fills red (#FE2C55) with Framer Motion scale animation
**And** tapping again removes the favorite (DELETE `/api/sounds/{id}/favorite`)
**And** the `favorites` table is created via Alembic migration (user_id, sound_id, created_at)
**And** duplicate favorites return 409 Conflict
**And** optimistic UI: heart toggles immediately, reverts on API error
**And** the HeartButton component (`heart-button.tsx`) works in SoundCard, PlayerBar, and NowPlaying

### Story 6.2: Favorites List Page

As a member,
I want to view all my favorite sounds and play them continuously,
So that I can enjoy my curated collection.

**Acceptance Criteria:**

**Given** I have favorited sounds
**When** I navigate to Library → Favorites (`/library/favorites`)
**Then** I see all my favorited sounds in a list using SoundCard components
**And** the API endpoint GET `/api/sounds/favorites` returns my favorites sorted by most recently added
**And** I can play all favorites as a continuous playlist (auto-queue all)
**When** I have no favorites
**Then** I see empty state: "No favorites yet. Tap ❤️ on any sound to save it here." with "Browse Trending" CTA

### Story 6.3: Playlist CRUD

As a member,
I want to create, rename, and delete playlists,
So that I can organize my sounds into collections.

**Acceptance Criteria:**

**Given** I am authenticated
**When** I create a playlist via POST `/api/playlists` with a name
**Then** the playlist is created and I see it in my playlists list
**And** the `playlists` and `playlist_sounds` tables are created via Alembic migration
**When** I rename a playlist via PUT `/api/playlists/{id}`
**Then** the playlist name is updated
**When** I delete a playlist via DELETE `/api/playlists/{id}`
**Then** the playlist and its sound associations are removed
**And** I can view all my playlists via GET `/api/playlists` showing name, sound count, and cover art mosaic
**And** the Library page (`/library`) shows both Playlists and Favorites sections
**When** I have no playlists
**Then** I see empty state: "No playlists yet. Create one to organize your sounds." with "Create Playlist" CTA

### Story 6.4: Playlist Sound Management & Playback

As a member,
I want to add/remove sounds from playlists and play entire playlists,
So that I can curate and enjoy my collections.

**Acceptance Criteria:**

**Given** I have a playlist
**When** I add a sound via POST `/api/playlists/{id}/sounds` with sound_id
**Then** the sound is added to the playlist
**And** duplicate additions return 409 Conflict
**When** I remove a sound via DELETE `/api/playlists/{id}/sounds/{sound_id}`
**Then** the sound is removed from the playlist
**When** I tap play on a playlist
**Then** all sounds in the playlist are queued and playback starts from the first sound
**And** the playlist detail page (`/library/playlists/[id]`) shows all sounds with SoundCard components
**And** long press on a SoundCard shows context menu with "Add to Playlist" option listing available playlists

## Epic 7: Playback Resilience

The system gracefully handles playback failures with auto-retry, skip, and cached-only fallback — users experience uninterrupted listening even during TikTok outages.

### Story 7.1: Auto-Retry & Alternative Source Fallback

As a member,
I want playback to automatically retry from alternative sources when it fails,
So that I experience minimal interruption.

**Acceptance Criteria:**

**Given** a sound is playing and the audio source fails
**When** the primary source (cached file or TikTok CDN proxy) returns an error
**Then** the system automatically retries from an alternative source (yt-dlp download or different TikTok URL)
**And** the player shows a subtle inline message: "Đang thử lại..." during retry
**And** if retry succeeds, the message changes to "Đã khôi phục playback ✓" and fades out after 3 seconds
**And** retry logic uses exponential backoff (max 3 attempts)
**And** retry attempts are logged with sound ID and error details

### Story 7.2: Graceful Skip & Cached-Only Fallback

As a member,
I want the player to skip unavailable sounds and fall back to cached-only mode,
So that music never stops completely even during major outages.

**Acceptance Criteria:**

**Given** a sound fails after all retry attempts
**When** the sound is temporarily unavailable
**Then** the player automatically skips to the next sound in the queue
**And** the skipped sound shows a ⚠️ icon in the queue
**When** 3 or more consecutive sounds fail
**Then** a toast notification appears: "Đang gặp sự cố kết nối nguồn nhạc. Các bài đã cache vẫn phát được bình thường."
**And** the queue is automatically filtered to cached-only sounds
**And** playback continues with cached sounds
**And** the Toast component (`toast.tsx`) supports info, success, warning, error variants
**And** toasts slide from top, auto-dismiss (3s info, 5s error), and are tappable to dismiss

## Epic 8: Admin Dashboard & System Management

Admins can monitor system health, view audit logs, manage scraper status, and trigger manual refreshes — full operational visibility and control.

### Story 8.1: Admin Dashboard Overview

As an admin,
I want a dashboard showing system health, user stats, cache stats, and scraper status,
So that I can monitor the system at a glance.

**Acceptance Criteria:**

**Given** I am authenticated as an admin
**When** I navigate to `/admin`
**Then** I see a dashboard with cards showing:

- User stats: total users, active users this week, pending approvals count
- Cache stats: total cached sounds, disk usage, cache hit ratio
- Scraper status: last fetch time, success/failure, sounds fetched, TikTok-Api health
- System health: API uptime, database status, Redis status
  **And** stats are fetched from GET `/api/admin/dashboard` which aggregates data from Redis and database
  **And** the admin layout (`admin/layout.tsx`) includes an admin-only route guard (redirects non-admins to home)
  **And** non-admin users receive 403 on all `/api/admin/*` endpoints

### Story 8.2: Audit Log Viewer

As an admin,
I want to view audit logs filtered by event type, user, or date range,
So that I can investigate security events and user activity.

**Acceptance Criteria:**

**Given** I am on the admin dashboard
**When** I navigate to `/admin/audit-logs`
**Then** I see a filterable table of audit log entries
**And** I can filter by event type (login, registration, admin action, stream access, rate limit)
**And** I can filter by user (username or user ID)
**And** I can filter by date range
**And** the API endpoint GET `/api/admin/audit-logs` supports query params: `event_type`, `user_id`, `date_from`, `date_to`, `page`, `page_size`
**And** each entry shows: timestamp, event type, user, IP address, details
**And** the AuditLogViewer component uses monospace font (JetBrains Mono) for log details

### Story 8.3: Scraper Management & Manual Refresh

As an admin,
I want to view scraper status and trigger manual trending data refreshes,
So that I can manage the data pipeline when issues arise.

**Acceptance Criteria:**

**Given** I am on the admin dashboard
**When** I view the scraper status section
**Then** I see: session health (active/error), last fetch time, failure rate, last error message
**And** I can trigger a manual trending refresh via POST `/api/admin/scraper/refresh`
**And** the manual refresh runs the trending fetcher immediately (outside the scheduled cycle)
**And** I see a loading indicator during the refresh and success/failure result
**And** scraper status is fetched from Redis (updated by the fetcher after each cycle)
**And** the ScraperStatus component (`scraper-status.tsx`) shows health with color-coded indicators (green=healthy, yellow=degraded, red=error)
