# Story 1.5: Docker Compose & Local Development Environment

Status: done

## Story

As a developer,
I want a Docker Compose setup that runs all services locally,
so that I can develop and test the full stack on my machine.

## Acceptance Criteria

1. **Given** backend and frontend projects exist, **When** I create `docker-compose.dev.yml`, **Then** it defines 5 services: `nginx`, `frontend`, `backend`, `mysql`, `redis`

2. **Given** `docker-compose.dev.yml` exists, **When** I create `backend/Dockerfile`, **Then** it builds a Python 3.14 image with `uv` for dependency management and runs uvicorn with `--reload` for hot reload in dev

3. **Given** `docker-compose.dev.yml` exists, **When** I create `frontend/Dockerfile`, **Then** it builds a Node.js 22 image and runs `npm run dev` with Turbopack for hot reload in dev

4. **Given** `docker-compose.dev.yml` exists, **When** I create `nginx/` config, **Then** Nginx reverse-proxies: `/` → frontend:3000, `/api/*` → backend:8000, with basic security headers

5. **Given** all configs exist, **When** I run `docker compose -f docker-compose.dev.yml up`, **Then** MySQL is accessible with configured credentials and the `toptop_music` database is created

6. **Given** all services are running, **When** I check connectivity, **Then** backend `/health` returns 200, `/health/ready` returns 200 (DB + Redis connected), and frontend is accessible through Nginx on port 80

7. **Given** all services are running, **When** I test BFF proxy, **Then** `http://localhost/api/health` routes through Nginx → frontend → backend and returns the health response

8. **Given** dev mode is active, **When** I edit backend Python files, **Then** uvicorn auto-reloads; **When** I edit frontend TSX files, **Then** Turbopack hot-reloads

## Tasks / Subtasks

- [x] Task 1: Create `backend/Dockerfile` (AC: #2)
  - [x] Use `python:3.14-slim` base image
  - [x] Install `uv` via pip or curl
  - [x] Copy `pyproject.toml`, `uv.lock`, install dependencies with `uv sync --frozen`
  - [x] Copy app source code
  - [x] CMD: `uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
- [x] Task 2: Create `frontend/Dockerfile` (AC: #3)
  - [x] Use `node:22-slim` base image
  - [x] Copy `package.json`, `package-lock.json`, run `npm ci`
  - [x] Copy source code
  - [x] CMD: `npm run dev -- --hostname 0.0.0.0`
  - [x] Expose port 3000
- [x] Task 3: Create `nginx/` config (AC: #4)
  - [x] Create `nginx/nginx.conf` with worker processes, events block
  - [x] Create `nginx/conf.d/default.conf` with upstream definitions and proxy rules
  - [x] Proxy `/` → `http://frontend:3000`
  - [x] Proxy `/api/` → `http://backend:8000/api/`
  - [x] Add basic security headers (X-Content-Type-Options, X-Frame-Options)
- [x] Task 4: Create `docker-compose.dev.yml` (AC: #1, #5)
  - [x] Define `mysql` service: MySQL 8.0, env vars for root password and database name, volume for data persistence, healthcheck
  - [x] Define `redis` service: Redis 7, healthcheck
  - [x] Define `backend` service: build from `backend/Dockerfile`, env vars, depends_on mysql + redis, volume mount for hot reload
  - [x] Define `frontend` service: build from `frontend/Dockerfile`, env vars, volume mount for hot reload
  - [x] Define `nginx` service: nginx:alpine, mount config, depends_on frontend + backend, expose port 80
- [x] Task 5: Create root `.env.example` for Docker Compose (AC: #5)
  - [x] Add `MYSQL_ROOT_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`
  - [x] Add `REDIS_URL`, `DATABASE_URL`, `JWT_SECRET_KEY`
  - [x] Add `BACKEND_URL` for frontend BFF proxy
- [x] Task 6: Verify services start and connect (AC: #6, #7, #8)
  - [x] Run `docker compose -f docker-compose.dev.yml build`
  - [x] Run `docker compose -f docker-compose.dev.yml up -d`
  - [x] Verify all 5 services are running
  - [x] Test backend health endpoints
  - [x] Test frontend accessibility through Nginx
  - [x] Test BFF proxy: `curl http://localhost/api/health`

### Review Follow-ups (AI)

- [x] [Review][Patch] Nginx strips `/api/` prefix — will break when backend adds `/api/*` routes in Epic 2+. Keep strip for now but add comment documenting the decision and future change needed [nginx/conf.d/default.conf]
- [x] [Review][Patch] No `restart: unless-stopped` on services — containers stay down after crash [docker-compose.dev.yml]
- [x] [Review][Defer] Dev deps installed in Docker image via `uv sync --frozen` without `--no-dev` — acceptable for dev Dockerfile [backend/Dockerfile] — deferred
- [x] [Review][Defer] `alembic/` directory not in volume mount — alembic changes require rebuild [docker-compose.dev.yml] — deferred
- [x] [Review][Defer] Root config files (next.config.ts, package.json) not in frontend volume mount — expected for dev [docker-compose.dev.yml] — deferred
- [x] [Review][Defer] MySQL healthcheck only checks mysqld process, not connection readiness [docker-compose.dev.yml] — deferred

## Dev Notes

### Architecture Compliance

- **5 services:** nginx, frontend, backend, mysql, redis — as specified in architecture
- **Nginx:** Reverse proxy, security headers. SSL termination deferred to production (Let's Encrypt)
- **BFF proxy:** In dev, Nginx proxies `/api/*` → backend directly. In production, Next.js rewrites handle this. For dev Docker, Nginx handles both frontend and API routing.
- **Hot reload:** Backend uses `uvicorn --reload` with volume mount. Frontend uses Turbopack with volume mount.
- [Source: architecture.md#Infrastructure & Deployment]

### Docker Compose Service Architecture

```
                    ┌─────────┐
                    │  Nginx  │ :80
                    └────┬────┘
                    ┌────┴────┐
              ┌─────┤         ├─────┐
              │     │         │     │
        ┌─────▼──┐  │    ┌────▼───┐
        │Frontend│  │    │Backend │ :8000
        │ :3000  │  │    └───┬────┘
        └────────┘  │    ┌───┴────┐
                    │  ┌─▼──┐ ┌──▼──┐
                    │  │MySQL│ │Redis│
                    │  │:3306│ │:6379│
                    │  └─────┘ └─────┘
                    └─────────────────┘
```

### Backend Dockerfile Pattern

```dockerfile
FROM python:3.14-slim
WORKDIR /app
# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
# Install dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
# Copy source
COPY . .
# Dev: --reload for hot reload (volume mount source)
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

Note: For dev, mount `./backend:/app` as volume so `--reload` picks up changes.

- [Source: architecture.md#Infrastructure & Deployment — Uvicorn 2-4 workers]

### Frontend Dockerfile Pattern

```dockerfile
FROM node:22-slim
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0"]
EXPOSE 3000
```

Note: For dev, mount `./frontend/src:/app/src` as volume so Turbopack picks up changes.

- [Source: architecture.md#Infrastructure & Deployment]

### Nginx Config Pattern

```nginx
# nginx/conf.d/default.conf
upstream frontend {
    server frontend:3000;
}

upstream backend {
    server backend:8000;
}

server {
    listen 80;
    server_name localhost;

    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";

    # API routes → backend
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Request-ID $request_id;
    }

    # Everything else → frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

WebSocket upgrade headers needed for Next.js HMR (Hot Module Replacement) in dev.

- [Source: architecture.md#Infrastructure & Deployment — Nginx]

### MySQL Service Config

```yaml
mysql:
  image: mysql:8.0
  environment:
    MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD:-rootpassword}
    MYSQL_DATABASE: ${MYSQL_DATABASE:-toptop_music}
  ports:
    - "3306:3306"
  volumes:
    - mysql_data:/var/lib/mysql
  healthcheck:
    test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
    interval: 10s
    timeout: 5s
    retries: 5
```

### Environment Variables for Docker

Backend container needs:

- `DATABASE_URL=mysql+aiomysql://root:rootpassword@mysql:3306/toptop_music`
- `REDIS_URL=redis://redis:6379/0`
- `JWT_SECRET_KEY=dev-secret-change-in-production`

Frontend container needs:

- `BACKEND_URL=http://backend:8000` (for Next.js rewrites in SSR)

Note: In Docker network, services reference each other by service name (`mysql`, `redis`, `backend`, `frontend`).

### Previous Story Learnings (Story 1.1-1.4)

- Backend config: `app/config.py` reads `DATABASE_URL`, `REDIS_URL` from env vars with localhost defaults
- Backend has `/health` (liveness) and `/health/ready` (DB + Redis check)
- Frontend `next.config.ts` reads `BACKEND_URL` env var for BFF proxy rewrites
- All dependencies already installed in both projects
- `uv.lock` exists in backend — use `uv sync --frozen` in Docker for reproducible builds
- [Source: Stories 1.1-1.4 completion notes]

### Anti-Patterns to Avoid

- ❌ Do NOT use `latest` tag for MySQL/Redis images — pin to specific major versions
- ❌ Do NOT expose MySQL/Redis ports to host in production — only in dev
- ❌ Do NOT hardcode passwords in docker-compose — use env vars with defaults
- ❌ Do NOT copy `node_modules` or `.venv` into Docker images — install fresh
- ❌ Do NOT use `npm install` in Docker — use `npm ci` for reproducible builds
- ❌ Do NOT skip healthchecks — backend should wait for MySQL/Redis to be ready

### Files to Create

- `backend/Dockerfile` — new
- `frontend/Dockerfile` — new
- `nginx/nginx.conf` — new
- `nginx/conf.d/default.conf` — new
- `docker-compose.dev.yml` — new (root level)
- `.env.example` — new (root level, for Docker Compose)

### References

- [Source: architecture.md#Infrastructure & Deployment — Docker Compose, Nginx, Uvicorn]
- [Source: architecture.md#Project Structure & Boundaries — docker-compose.yml, nginx/ directory]
- [Source: architecture.md#Data Flow — service communication diagram]
- [Source: epics.md#Story 1.5 — Acceptance criteria]

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.6

### Debug Log References

- Initial Nginx config proxied `/api/` to backend without stripping prefix — backend routes are at root (`/health` not `/api/health`). Fixed by adding trailing `/` to `proxy_pass http://backend/;` which strips the `/api/` prefix.
- Added `.dockerignore` files to both backend and frontend to keep images lean (exclude .venv, node_modules, .next, etc.)

### Completion Notes List

- Created `backend/Dockerfile` — Python 3.14-slim, uv for deps, uvicorn --reload for dev
- Created `frontend/Dockerfile` — Node 22-slim, npm ci, Next.js dev with Turbopack
- Created `nginx/nginx.conf` + `nginx/conf.d/default.conf` — reverse proxy with security headers, WebSocket support for HMR
- Created `docker-compose.dev.yml` — 5 services (mysql:8.0, redis:7-alpine, backend, frontend, nginx:alpine) with healthchecks, volume mounts for hot reload
- Created root `.env.example` for Docker Compose env vars
- Added `.dockerignore` for both backend and frontend
- All 5 services verified running: MySQL healthy, Redis healthy, backend /health 200, /health/ready 200 (DB + Redis connected), frontend 200 through Nginx, BFF proxy `/api/health` working

### File List

- backend/Dockerfile (new)
- backend/.dockerignore (new)
- frontend/Dockerfile (new)
- frontend/.dockerignore (new)
- nginx/nginx.conf (new)
- nginx/conf.d/default.conf (new)
- docker-compose.dev.yml (new)
- .env.example (new, root level)

## Change Log

- 2026-03-27: Story 1.5 implemented — Docker Compose dev environment with 5 services, all verified running and connected.
- 2026-03-27: Code review complete — 2 patches applied (Nginx prefix comment, restart policy), 4 deferred.
