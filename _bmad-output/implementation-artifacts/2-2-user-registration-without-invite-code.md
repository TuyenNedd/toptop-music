# Story 2.2: User Registration without Invite Code (Pending Approval)

Status: done

## Story

As a visitor,
I want to register without an invite code and await admin approval,
so that I can request access even without an invitation.

## Acceptance Criteria

1. **Given** I do not have an invite code, **When** I POST `/api/auth/register` with username, email, and password (no invite_code), **Then** my account is created with role "member" and status "pending"

2. **Given** registration succeeds without invite code, **When** I check the response, **Then** it contains `{"data": {"status": "pending", ...}, "error": null}` with message context

3. **Given** I have a pending account, **When** I attempt to log in (Story 2.3), **Then** I get 403 with message "Account pending approval" (verified in Story 2.3, not this story)

4. **Given** the project is complete, **When** I run `uv run ruff check .` and `uv run mypy .`, **Then** both pass with zero errors

## Tasks / Subtasks

- [x] Task 1: Add test for registration without invite code (AC: #1, #2)
  - [x] Test that POST /api/auth/register without invite_code creates user with status "pending"
  - [x] Test response envelope contains correct user data with status "pending"
- [x] Task 2: Verify linting and type checking (AC: #4)
  - [x] Run `uv run ruff check .` — zero errors
  - [x] Run `uv run mypy .` — zero errors

## Dev Notes

### Implementation Note

The pending registration path is ALREADY IMPLEMENTED in Story 2.1's `AuthService.register()`. When `invite_code` is `None`, the user is created with `status = UserStatus.PENDING`. This story adds test coverage and verifies the behavior.

### Previous Story Context (Story 2.1)

- `AuthService.register()` handles both paths: invite code → active, no invite → pending
- `RegisterRequest.invite_code` is `str | None = None` — optional field
- All duplicate checks and password hashing apply to both paths
- [Source: backend/app/auth/service.py]

### References

- [Source: epics.md#Story 2.2 — Acceptance criteria]
- [Source: backend/app/auth/service.py — register() method]

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.6

### Debug Log References

No new code needed — pending path already implemented in Story 2.1. Only added test.

### Completion Notes List

- Added test `test_register_without_invite_creates_pending_user` verifying status=pending when no invite code
- 40 tests passing, ruff + mypy clean

### File List

- backend/tests/auth/test_service.py (modified — added pending registration test)
