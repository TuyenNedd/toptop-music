# Story 2.5: Admin Invite Code Management

Status: done

## Story

As an admin,
I want to generate invite codes with configurable expiration,
so that I can control who gets access to the app.

## Acceptance Criteria

1. **Given** I am authenticated as admin, **When** I POST `/api/admin/invite-codes` with expiration_days, **Then** a unique invite code is generated and stored
2. **Given** I am authenticated as admin, **When** I GET `/api/admin/invite-codes`, **Then** I see all invite codes with status (unused/used/expired)
3. **Given** I am NOT admin, **When** I call admin endpoints, **Then** I get 403 Forbidden
4. **Given** invite code is generated, **When** it completes, **Then** it is logged to audit trail
5. **Given** the project is complete, **When** I run ruff + mypy, **Then** both pass

## Tasks / Subtasks

- [x] Task 1: Create admin router and invite code endpoints (AC: #1, #2, #3)
  - [x] Create `app/admin/router.py` with `require_role("admin")` dependency
  - [x] POST `/api/admin/invite-codes` — generate code, store with expiry
  - [x] GET `/api/admin/invite-codes` — list all codes with computed status
- [x] Task 2: Create admin service (AC: #1, #4)
  - [x] Create `app/admin/service.py` with invite code generation logic
  - [x] Generate unique code via `secrets.token_hex(16)`
  - [x] Log to audit trail
- [x] Task 3: Create admin schemas
  - [x] `InviteCodeCreateRequest` (expiration_days: int)
  - [x] `InviteCodeResponse` (code, status, created_at, expires_at, used_by)
- [x] Task 4: Register admin router in main.py
- [x] Task 5: Verify ruff + mypy (AC: #5)

## Dev Notes

- Admin module: `admin/router.py`, `admin/service.py`, `admin/schemas.py`
- Use `require_role("admin")` from `auth/dependencies.py` for RBAC
- InviteCode model already exists from Story 2.1
- InviteCodeRepository already has `get_by_code` — add `get_all` method
- Audit logging via `AuditLogRepository` from Story 2.3
- [Source: architecture.md#Project Structure, epics.md#Story 2.5]

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.6

### Debug Log References

No issues.

### Completion Notes List

- Created `admin/schemas.py`, `admin/service.py`, `admin/router.py`
- POST `/api/admin/invite-codes` generates code with configurable expiry, audit logged
- GET `/api/admin/invite-codes` lists all codes with computed status (unused/used/expired)
- Both endpoints protected by `require_role("admin")`
- Added `get_all()` to InviteCodeRepository
- 54 tests passing (2 new)

### File List

- backend/app/admin/schemas.py (new)
- backend/app/admin/service.py (new)
- backend/app/admin/router.py (new)
- backend/app/auth/repository.py (modified — added get_all to InviteCodeRepository)
- backend/app/main.py (modified — registered admin router)
- backend/tests/admin/**init**.py (new)
- backend/tests/admin/test_invite_codes.py (new)
