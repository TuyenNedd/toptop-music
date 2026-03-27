# Story 2.3: User Login & JWT Session Management

Status: done

## Story

As a registered user,
I want to log in with my username/email and password and maintain a secure session,
so that I can access the app without re-authenticating frequently.

## Acceptance Criteria

1. **Given** I have an active account, **When** I POST `/api/auth/login` with valid credentials (username or email + password), **Then** I receive a JWT access token (30 min expiry) in the response body

2. **Given** login succeeds, **When** I check the response, **Then** a refresh token (7 day expiry) is set as an httpOnly secure cookie

3. **Given** no refresh_tokens table exists, **When** I run Alembic migration, **Then** `refresh_tokens` and `audit_logs` tables are created

4. **Given** I submit wrong credentials, **When** failed attempts reach 5 for same IP/username, **Then** I get 429 Too Many Requests with 15 minute lockout

5. **Given** any login attempt, **When** it completes (success or failure), **Then** it is logged to `audit_logs` table

6. **Given** I have a pending account, **When** I try to login, **Then** I get 403 with message "Account pending approval"

7. **Given** the project is complete, **When** I run `uv run ruff check .` and `uv run mypy .`, **Then** both pass with zero errors

## Tasks / Subtasks

- [x] Task 1: Create RefreshToken and AuditLog models (AC: #3)
  - [x] Add `RefreshToken` model to `app/auth/models.py`: id, token (unique), user_id (FK), expires_at, revoked (bool), created_at
  - [x] Add `AuditLog` model to `app/auth/models.py`: id, event_type, user_id (nullable FK), ip_address, details (JSON/text), created_at
  - [x] Run Alembic migration to create both tables
- [x] Task 2: Add JWT encode/decode to `core/security.py` (AC: #1)
  - [x] Implement `create_access_token(user_id, role)` — JWT with 30 min expiry using `python-jose`
  - [x] Implement `decode_access_token(token)` — returns payload or raises
  - [x] Use `settings.JWT_SECRET_KEY` and `settings.JWT_EXPIRY_MINUTES`
- [x] Task 3: Create auth dependencies (AC: #1)
  - [x] Create `app/auth/dependencies.py` with `get_current_user(token)` — extracts user from JWT Bearer token
  - [x] Create `require_role(role)` dependency factory for RBAC
- [x] Task 4: Implement login service logic (AC: #1, #2, #4, #5, #6)
  - [x] Add `login(username_or_email, password, ip_address)` to `AuthService`
  - [x] Verify credentials: find user by username OR email, verify password
  - [x] Check user status: pending → 403, inactive → 403
  - [x] Generate access token + refresh token
  - [x] Store refresh token in DB
  - [x] Track failed attempts per IP/username in Redis (5 attempts → 15 min lockout)
  - [x] Log all attempts to audit_logs
- [x] Task 5: Create login endpoint (AC: #1, #2)
  - [x] Add `POST /api/auth/login` to router
  - [x] Accept `LoginRequest` (username_or_email, password)
  - [x] Return access token in body, set refresh token as httpOnly cookie
- [x] Task 6: Add LoginRequest schema
  - [x] Create `LoginRequest` in schemas.py: username_or_email (str), password (str)
  - [x] Create `TokenResponse`: access_token (str), token_type (str)
- [x] Task 7: Verify linting and type checking (AC: #7)
  - [x] Run `uv run ruff check .` — zero errors
  - [x] Run `uv run mypy .` — zero errors

## Dev Notes

### Architecture Compliance

- **JWT:** `python-jose[cryptography]` for encode/decode. Access token 30 min, refresh token 7 days.
- **Refresh token:** Stored in DB (`refresh_tokens` table), set as httpOnly secure cookie
- **RBAC:** `get_current_user` + `require_role("admin")` / `require_role("member")` dependencies
- **Login lockout:** 5 failed attempts → 15 min cooldown, tracked in Redis per IP+username
- **Audit logging:** All login attempts (success/failure) logged to `audit_logs` MySQL table
- [Source: architecture.md#Authentication & Security]

### JWT Token Pattern

```python
from jose import jwt
from datetime import datetime, timedelta, UTC

def create_access_token(user_id: int, role: str) -> str:
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": datetime.now(UTC) + timedelta(minutes=settings.JWT_EXPIRY_MINUTES),
        "iat": datetime.now(UTC),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
```

### Login Lockout Pattern (Redis)

```python
key = f"login_attempts:{ip}:{username}"
attempts = await redis.incr(key)
if attempts == 1:
    await redis.expire(key, 900)  # 15 min TTL
if attempts > 5:
    raise AppException("AUTH_LOGIN_LOCKED", "Too many attempts", 429)
```

### Audit Log Pattern

```python
audit = AuditLog(
    event_type="login_success" | "login_failed",
    user_id=user.id if user else None,
    ip_address=request.client.host,
    details=json.dumps({"username": username}),
)
```

### Previous Story Context (Story 2.1-2.2)

- User model exists with status field (active/pending/inactive/rejected)
- `verify_password()` in `core/security.py` ready for login
- `AppException` for structured errors
- `get_redis()` available for rate limiting
- [Source: Stories 2.1-2.2]

### Anti-Patterns to Avoid

- ❌ Do NOT store access tokens in DB — they are stateless JWT
- ❌ Do NOT return refresh token in response body — httpOnly cookie only
- ❌ Do NOT log passwords in audit trail — only event type and metadata
- ❌ Do NOT use `HS384` or `HS512` — use `HS256` as specified

### References

- [Source: architecture.md#Authentication & Security — JWT, RBAC, login lockout]
- [Source: epics.md#Story 2.3 — Acceptance criteria]

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.6

### Debug Log References

- `jose.jwt.encode` returns `Any` — added `type: ignore[no-any-return]`
- `payload.get("sub")` returns `object` — added isinstance check for mypy
- Reorganized `core/security.py` to fix E402 (imports not at top of file) after appending JWT functions

### Completion Notes List

- Added `RefreshToken` and `AuditLog` models with Alembic migration `d3b22cbfa4e1`
- Added JWT `create_access_token`, `decode_access_token`, `create_refresh_token` to `core/security.py`
- Created `auth/dependencies.py` with `get_current_user` (JWT Bearer) and `require_role` (RBAC factory)
- Implemented `AuthService.login()` with credential verification, status checks, token generation, Redis lockout tracking, audit logging
- Created `POST /api/auth/login` endpoint — returns access token in body, refresh token as httpOnly cookie
- Added `LoginRequest`, `TokenResponse` schemas
- Added `get_by_id` to UserRepository, `RefreshTokenRepository`, `AuditLogRepository`
- 47 tests passing (7 new: 4 login service, 3 JWT)

### File List

- backend/app/auth/models.py (modified — added RefreshToken, AuditLog)
- backend/app/auth/schemas.py (modified — added LoginRequest, TokenResponse)
- backend/app/auth/repository.py (modified — added get_by_id, RefreshTokenRepository, AuditLogRepository)
- backend/app/auth/service.py (modified — added login method with lockout, audit)
- backend/app/auth/router.py (modified — added POST /api/auth/login)
- backend/app/auth/dependencies.py (new — get_current_user, require_role)
- backend/app/core/security.py (modified — added JWT and refresh token functions)
- backend/alembic/versions/d3b22cbfa4e1_add_refresh_tokens_and_audit_logs.py (new)
- backend/tests/auth/test_login.py (new)
- backend/tests/test_jwt.py (new)
