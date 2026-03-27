# Story 2.1: User Registration with Invite Code

Status: done

## Story

As a visitor,
I want to register using an invite code for instant account activation,
so that I can immediately start using the app.

## Acceptance Criteria

1. **Given** no auth tables exist, **When** I run Alembic migration, **Then** `users` and `invite_codes` tables are created with correct schema

2. **Given** I have a valid, unexpired invite code, **When** I POST `/api/auth/register` with username, email, password, and invite_code, **Then** my account is created with role "member" and status "active"

3. **Given** registration succeeds, **When** I check the invite code, **Then** it is marked as used with my user_id and used_at timestamp

4. **Given** registration succeeds, **When** I check the stored password, **Then** it is hashed with bcrypt (minimum 12 rounds)

5. **Given** a user with the same username or email exists, **When** I try to register, **Then** I get 409 Conflict with error code `AUTH_REGISTER_DUPLICATE`

6. **Given** an expired or already-used invite code, **When** I try to register, **Then** I get 400 Bad Request with error code `AUTH_REGISTER_INVALID_INVITE`

7. **Given** the project is complete, **When** I run `uv run ruff check .` and `uv run mypy .`, **Then** both pass with zero errors

## Tasks / Subtasks

- [x] Task 1: Create SQLAlchemy models — `User` and `InviteCode` (AC: #1)
  - [x] Create `app/auth/models.py` with `User` model: id, username (unique), email (unique), hashed_password, role (enum: admin/member), status (enum: active/pending/inactive/rejected), created_at, updated_at
  - [x] Create `InviteCode` model: id, code (unique), created_by_id (FK→users), used_by_id (FK→users, nullable), expires_at, used_at (nullable), created_at
  - [x] Both models inherit from `Base` (from `app.database`)
- [x] Task 2: Create Alembic migration for users and invite_codes tables (AC: #1)
  - [x] Run `uv run alembic revision --autogenerate -m "add_users_and_invite_codes"` (requires MySQL running via Docker)
  - [x] Verify migration creates both tables with correct columns, indexes, and foreign keys
  - [x] Run `uv run alembic upgrade head` to apply migration
- [x] Task 3: Create Pydantic schemas (AC: #2)
  - [x] Create `app/auth/schemas.py` with `RegisterRequest` (username, email, password, invite_code: str | None)
  - [x] Create `RegisterResponse` with user data (id, username, email, role, status)
  - [x] Add password validation: minimum 8 characters
- [x] Task 4: Create auth repository (AC: #2, #3, #5)
  - [x] Create `app/auth/repository.py` with `UserRepository` class
  - [x] Implement `get_by_username(username)`, `get_by_email(email)`, `create_user(data)`
  - [x] Implement `InviteCodeRepository` with `get_by_code(code)`, `mark_used(code_id, user_id)`
- [x] Task 5: Create `core/security.py` — password hashing (AC: #4)
  - [x] Create `hash_password(password)` using bcrypt with 12 rounds
  - [x] Create `verify_password(plain, hashed)` for login (used in Story 2.3)
- [x] Task 6: Create auth service (AC: #2, #3, #5, #6)
  - [x] Create `app/auth/service.py` with `AuthService` class
  - [x] Implement `register_with_invite(data)`: validate invite code → check duplicates → hash password → create user → mark invite used
  - [x] Raise `AppException("AUTH_REGISTER_DUPLICATE", ..., 409)` for duplicate username/email
  - [x] Raise `AppException("AUTH_REGISTER_INVALID_INVITE", ..., 400)` for expired/used invite codes
- [x] Task 7: Create auth router (AC: #2)
  - [x] Create `app/auth/router.py` with `POST /api/auth/register` endpoint
  - [x] Accept `RegisterRequest` body, return `RegisterResponse` wrapped in API envelope
  - [x] Register router in `app/main.py`
- [x] Task 8: Verify linting and type checking (AC: #7)
  - [x] Run `uv run ruff check .` — zero errors
  - [x] Run `uv run mypy .` — zero errors

### Review Follow-ups (AI)

- [x] [Review][Patch] `datetime.utcnow()` deprecated in repository — replaced with `datetime.now(UTC)` [backend/app/auth/repository.py]
- [x] [Review][Patch] Username leaked in duplicate error message — use generic message [backend/app/auth/service.py]
- [x] [Review][Patch] No username format validation — added alphanumeric regex validator [backend/app/auth/schemas.py]
- [x] [Review][Patch] Timezone-aware vs naive comparison on invite expiry — added `replace(tzinfo=UTC)` [backend/app/auth/service.py]
- [x] [Review][Patch] Race condition on duplicate check — catch `IntegrityError` and return 409 [backend/app/auth/service.py]
- [x] [Review][Defer] `passlib[bcrypt]` still in pyproject.toml but unused — remove in future cleanup [backend/pyproject.toml] — deferred

## Dev Notes

### Architecture Compliance

- **Module:** `auth/` — Router → Service → Repository layers
- **Models:** `User`, `InviteCode` in `auth/models.py`, inherit from `Base`
- **Schemas:** `RegisterRequest`, `RegisterResponse` in `auth/schemas.py`
- **Security:** `core/security.py` — bcrypt via passlib, 12 rounds minimum
- **Errors:** Use `AppException` from `core/exceptions.py` — never bare `raise HTTPException`
- **API envelope:** All responses use `{"data": ..., "error": null}` format
- [Source: architecture.md#Authentication & Security, architecture.md#Project Structure]

### Database Schema

```sql
-- users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'member') DEFAULT 'member',
    status ENUM('active', 'pending', 'inactive', 'rejected') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_email (email),
    INDEX idx_users_username (username)
);

-- invite_codes table
CREATE TABLE invite_codes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,
    created_by_id INT NOT NULL,
    used_by_id INT NULL,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by_id) REFERENCES users(id),
    FOREIGN KEY (used_by_id) REFERENCES users(id),
    INDEX idx_invite_codes_code (code)
);
```

- [Source: architecture.md#Data Architecture — Database Naming Conventions]

### Error Codes

- `AUTH_REGISTER_DUPLICATE` (409) — username or email already exists
- `AUTH_REGISTER_INVALID_INVITE` (400) — invite code expired, used, or not found
- [Source: architecture.md#Format Patterns — Error Codes]

### Router Registration Pattern

```python
# app/auth/router.py
from fastapi import APIRouter
router = APIRouter(prefix="/api/auth", tags=["auth"])

# app/main.py — register in create_app()
from app.auth.router import router as auth_router
app.include_router(auth_router)
```

### Password Hashing Pattern

```python
# app/core/security.py
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

- [Source: architecture.md#Authentication & Security — bcrypt via passlib, 12 rounds]

### Previous Story Learnings (Epic 1)

- `Base` from `app.database` — all models inherit from this
- `get_db()` dependency for session injection
- `AppException` from `core/exceptions.py` for structured errors
- `get_logger()` from `core/logging.py` for structured logging
- Alembic async env.py configured — `alembic revision --autogenerate` works with MySQL
- MySQL available via Docker Compose: `docker compose -f docker-compose.dev.yml up mysql -d`
- [Source: Stories 1.1-1.5]

### Anti-Patterns to Avoid

- ❌ Do NOT store plain text passwords — always bcrypt hash
- ❌ Do NOT use bare `raise HTTPException` — use `raise AppException(...)`
- ❌ Do NOT access repository directly from router — go through service layer
- ❌ Do NOT return hashed_password in API responses — exclude from schemas
- ❌ Do NOT create admin endpoints in this story — those are Story 2.5/2.6

### References

- [Source: architecture.md#Authentication & Security]
- [Source: architecture.md#Project Structure — auth/ module files]
- [Source: architecture.md#Naming Patterns — Database, API, Python naming]
- [Source: epics.md#Story 2.1 — Acceptance criteria]

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.6

### Debug Log References

- `passlib[bcrypt]` incompatible with `bcrypt` 5.0 on Python 3.14 — passlib is unmaintained, bcrypt 5.0 removed `__about__` attribute. Switched to using `bcrypt` library directly instead of passlib wrapper.
- `StrEnum` used instead of `str, enum.Enum` — ruff UP042 rule, Python 3.14 native
- mypy `method-assign` errors in tests — added override in pyproject.toml for tests directory
- Alembic required running initial migration before autogenerate could work

### Completion Notes List

- Created `app/auth/models.py` — User (id, username, email, hashed_password, role, status, timestamps) and InviteCode (code, created_by, used_by, expires_at, used_at) with proper indexes
- Created `app/auth/schemas.py` — RegisterRequest (with validation) and UserResponse (excludes password)
- Created `app/auth/repository.py` — UserRepository and InviteCodeRepository with async queries
- Created `app/core/security.py` — bcrypt hash/verify using `bcrypt` library directly (not passlib)
- Created `app/auth/service.py` — AuthService with register() handling invite validation, duplicate checks, password hashing
- Created `app/auth/router.py` — POST /api/auth/register endpoint with API envelope response
- Alembic migration `0145abf1052c_add_users_and_invite_codes` generated and applied
- Registered auth router in app/main.py
- 39 tests passing (10 new: 6 auth service, 4 security)

### File List

- backend/app/auth/models.py (new)
- backend/app/auth/schemas.py (new)
- backend/app/auth/repository.py (new)
- backend/app/auth/service.py (new)
- backend/app/auth/router.py (new)
- backend/app/core/security.py (new)
- backend/app/main.py (modified — auth router registered)
- backend/alembic/env.py (modified — import auth models)
- backend/alembic/versions/0145abf1052c_add_users_and_invite_codes.py (new)
- backend/pyproject.toml (modified — mypy override for tests)
- backend/tests/auth/**init**.py (new)
- backend/tests/auth/test_service.py (new)
- backend/tests/test_security.py (new)
