# Story 2.4: Token Refresh & Logout

Status: done

## Story

As an authenticated user,
I want my session to renew automatically and to log out when needed,
so that I stay logged in seamlessly but can end my session securely.

## Acceptance Criteria

1. **Given** I have a valid refresh token cookie, **When** I POST `/api/auth/refresh`, **Then** a new access token is returned and the refresh token is rotated (old revoked, new issued)
2. **Given** the refresh token is expired or revoked, **When** I POST `/api/auth/refresh`, **Then** I get 401 Unauthorized
3. **Given** I am authenticated, **When** I POST `/api/auth/logout`, **Then** my refresh token is revoked and the httpOnly cookie is cleared
4. **Given** any logout, **When** it completes, **Then** it is logged to audit trail
5. **Given** the project is complete, **When** I run ruff + mypy, **Then** both pass with zero errors

## Tasks / Subtasks

- [x] Task 1: Add refresh service method (AC: #1, #2)
  - [x] Add `refresh_token(token_str)` to AuthService
  - [x] Validate token exists, not revoked, not expired
  - [x] Revoke old token, create new refresh token + new access token
  - [x] Return (access_token, new_refresh_token, expires_at)
- [x] Task 2: Add logout service method (AC: #3, #4)
  - [x] Add `logout(token_str, ip_address)` to AuthService
  - [x] Revoke refresh token in DB
  - [x] Log logout to audit trail
- [x] Task 3: Add refresh and logout endpoints (AC: #1, #2, #3)
  - [x] POST `/api/auth/refresh` — read refresh_token from cookie, return new access token, set new cookie
  - [x] POST `/api/auth/logout` — read refresh_token from cookie, revoke, clear cookie
- [x] Task 4: Verify ruff + mypy (AC: #5)

## Dev Notes

### Previous Story Context

- `RefreshTokenRepository` already has `get_by_token`, `create`, `revoke` methods
- `AuditLogRepository` has `create` method
- `create_access_token`, `create_refresh_token` in `core/security.py`
- Cookie set with `path="/api/auth"` — refresh/logout endpoints are under this path
- [Source: Story 2.3]

### References

- [Source: epics.md#Story 2.4, architecture.md#Authentication & Security]

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.6

### Debug Log References

No issues encountered.

### Completion Notes List

- Added `refresh_token()` to AuthService — validates, revokes old, issues new tokens, checks user status
- Added `logout()` to AuthService — revokes token, logs audit, graceful no-op if token not found
- Added POST `/api/auth/refresh` and POST `/api/auth/logout` endpoints
- Extracted `_is_production()` helper for cookie secure flag
- 52 tests passing (5 new: refresh success/invalid/expired, logout revoke/noop)

### File List

- backend/app/auth/service.py (modified — added refresh_token, logout methods)
- backend/app/auth/router.py (modified — added /refresh, /logout endpoints)
- backend/tests/auth/test_refresh_logout.py (new)
