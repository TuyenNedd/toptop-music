# Story 1.6: CI/CD Pipeline

Status: done

## Story

As a developer,
I want automated CI/CD via GitHub Actions,
so that every push is linted, tested, built, and deployable.

## Acceptance Criteria

1. **Given** the project is in a GitHub repository, **When** a push or PR is made to any branch, **Then** `.github/workflows/ci-backend.yml` runs: `ruff check` → `mypy` → `pytest` with a MySQL service container

2. **Given** the backend CI workflow exists, **When** it runs, **Then** it uses `uv` for dependency installation, Python 3.14, and a MySQL 8.0 service container for integration tests

3. **Given** the project is in a GitHub repository, **When** a push or PR is made to any branch, **Then** `.github/workflows/ci-frontend.yml` runs: `npm run lint` → `tsc --noEmit` → `npm run build`

4. **Given** the frontend CI workflow exists, **When** it runs, **Then** it uses Node.js 22 and caches `node_modules` for faster builds

5. **Given** both CI workflows exist, **When** any step fails, **Then** the pipeline fails fast with clear error output and does not continue to subsequent steps

6. **Given** the CI passes, **When** a merge to `main` occurs, **Then** Docker images for backend and frontend are built (build step only for MVP — push to registry deferred)

## Tasks / Subtasks

- [x] Task 1: Create `.github/workflows/ci-backend.yml` (AC: #1, #2, #5)
  - [x] Trigger on push and pull_request to all branches
  - [x] Set up Python 3.14 with `uv` for dependency management
  - [x] Add MySQL 8.0 service container with health check
  - [x] Run `uv sync --frozen` to install dependencies
  - [x] Run `uv run ruff check .` — fail fast on lint errors
  - [x] Run `uv run mypy .` — fail fast on type errors
  - [x] Run `uv run pytest tests/ -v` with `DATABASE_URL` pointing to MySQL service
  - [x] Set working-directory to `backend/`
- [x] Task 2: Create `.github/workflows/ci-frontend.yml` (AC: #3, #4, #5)
  - [x] Trigger on push and pull_request to all branches
  - [x] Set up Node.js 22 with npm cache
  - [x] Run `npm ci` to install dependencies
  - [x] Run `npm run lint` — fail fast on lint errors
  - [x] Run `npx tsc --noEmit` — fail fast on type errors
  - [x] Run `npm run build` — fail fast on build errors
  - [x] Set working-directory to `frontend/`
- [x] Task 3: Add Docker build step on main merge (AC: #6)
  - [x] Add job `docker-build` to `ci-backend.yml` that runs only on push to `main`
  - [x] Build backend Docker image: `docker build -t toptop-music-backend ./backend`
  - [x] Add job `docker-build` to `ci-frontend.yml` that runs only on push to `main`
  - [x] Build frontend Docker image: `docker build -t toptop-music-frontend ./frontend`
  - [x] Both jobs depend on their respective CI jobs passing first
- [x] Task 4: Verify workflows are valid
  - [x] Validate YAML syntax of both workflow files
  - [x] Ensure all paths and commands are correct

### Review Follow-ups (AI)

- [x] [Review][Patch] Backend CI sets `REDIS_URL` but no Redis service — remove env var or add comment that Redis is mocked in tests [.github/workflows/ci-backend.yml]
- [x] [Review][Patch] `setup-python@v5` may conflict with `setup-uv` for Python 3.14 — let `setup-uv` handle Python or pin `allow-prereleases: true` [.github/workflows/ci-backend.yml]
- [x] [Review][Patch] No `concurrency` group — parallel CI runs on same branch waste resources [.github/workflows/ci-backend.yml, .github/workflows/ci-frontend.yml]
- [x] [Review][Defer] `uv.lock` drift detection — `--frozen` fails if lock stale, desired behavior [.github/workflows/ci-backend.yml] — deferred
- [x] [Review][Defer] `npx tsc` version resolution — resolves from node_modules, fine [.github/workflows/ci-frontend.yml] — deferred
- [x] [Review][Defer] Docker build without BuildKit cache — acceptable for MVP [.github/workflows/ci-backend.yml, .github/workflows/ci-frontend.yml] — deferred

## Dev Notes

### Architecture Compliance

- **CI/CD:** GitHub Actions — Push/PR → lint → type check → test → build Docker
- **Backend pipeline:** ruff check → mypy → pytest (with MySQL service container)
- **Frontend pipeline:** npm run lint → tsc --noEmit → npm run build
- **Docker build:** On merge to main only. Push to container registry deferred to production setup.
- [Source: architecture.md#Infrastructure & Deployment — CI/CD row]

### Backend CI Workflow Pattern

```yaml
name: Backend CI
on:
  push:
    paths: ["backend/**"]
  pull_request:
    paths: ["backend/**"]

jobs:
  ci:
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: testpassword
          MYSQL_DATABASE: toptop_music_test
        ports:
          - 3306:3306
        options: >-
          --health-cmd="mysqladmin ping -h localhost"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=5
    defaults:
      run:
        working-directory: backend
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.14"
      - run: uv sync --frozen
      - run: uv run ruff check .
      - run: uv run mypy .
      - run: uv run pytest tests/ -v
        env:
          DATABASE_URL: mysql+aiomysql://root:testpassword@localhost:3306/toptop_music_test
          REDIS_URL: redis://localhost:6379/0
```

- [Source: architecture.md#Infrastructure & Deployment]

### Frontend CI Workflow Pattern

```yaml
name: Frontend CI
on:
  push:
    paths: ["frontend/**"]
  pull_request:
    paths: ["frontend/**"]

jobs:
  ci:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: "npm"
          cache-dependency-path: frontend/package-lock.json
      - run: npm ci
      - run: npm run lint
      - run: npx tsc --noEmit
      - run: npm run build
```

### Path Filtering

Both workflows use `paths` filter to only run when relevant files change:

- Backend CI: triggered by changes in `backend/**`
- Frontend CI: triggered by changes in `frontend/**`

This avoids unnecessary CI runs when only one side changes.

### MySQL Service Container Notes

- GitHub Actions supports service containers natively
- MySQL 8.0 with healthcheck ensures DB is ready before tests run
- `DATABASE_URL` env var overrides the default in `app/config.py`
- Redis service container NOT needed for current tests (all Redis calls are mocked)
- If future tests need Redis, add a Redis service container

### Docker Build on Main

- Build-only for MVP — no push to registry yet
- Uses `docker/build-push-action@v5` or simple `docker build`
- Depends on CI job passing first (`needs: ci`)
- Only runs on `push` to `main` (not on PRs)

### Previous Story Learnings (Story 1.1-1.5)

- Backend uses `uv` exclusively — `uv sync --frozen` for CI, `uv run` for commands
- Frontend uses `npm ci` for reproducible installs
- Backend tests: 29 passing, all use mocks (no live DB/Redis needed for unit tests)
- Frontend tests: 23 passing via Vitest
- Dockerfiles exist for both backend and frontend (Story 1.5)
- `astral-sh/setup-uv@v4` is the official GitHub Action for uv setup
- [Source: Stories 1.1-1.5 completion notes]

### Anti-Patterns to Avoid

- ❌ Do NOT use `pip install` in CI — use `uv sync --frozen`
- ❌ Do NOT use `npm install` in CI — use `npm ci`
- ❌ Do NOT run all workflows on every file change — use `paths` filter
- ❌ Do NOT continue after lint/type failures — fail fast
- ❌ Do NOT push Docker images on PRs — only on merge to main

### Files to Create

- `.github/workflows/ci-backend.yml` — new
- `.github/workflows/ci-frontend.yml` — new

### References

- [Source: architecture.md#Infrastructure & Deployment — CI/CD: GitHub Actions]
- [Source: architecture.md#Project Structure & Boundaries — .github/workflows/ directory]
- [Source: epics.md#Story 1.6 — Acceptance criteria]

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.6

### Debug Log References

No issues encountered. Both YAML files validated via pyyaml.

### Completion Notes List

- Created `ci-backend.yml` — Python 3.14 + uv + MySQL 8.0 service container, runs ruff → mypy → pytest, Docker build on main merge
- Created `ci-frontend.yml` — Node.js 22 + npm cache, runs lint → tsc --noEmit → build → test, Docker build on main merge
- Both workflows use `paths` filter for efficient CI (only run when relevant files change)
- Both workflows include `docker-build` job that runs only on push to `main`, depends on CI passing
- Added Vitest test step to frontend CI (not in original AC but consistent with backend having pytest)
- YAML syntax validated for both files
- All existing tests still pass: backend 29/29, frontend 23/23

### File List

- .github/workflows/ci-backend.yml (new)
- .github/workflows/ci-frontend.yml (new)

## Change Log

- 2026-03-27: Story 1.6 implemented — GitHub Actions CI/CD with backend and frontend workflows, Docker build on main merge.
- 2026-03-27: Code review complete — 3 patches applied (removed setup-python conflict, REDIS_URL comment, concurrency groups), 3 deferred.
