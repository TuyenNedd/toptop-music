# Story 2.6: Admin User Approval & Account Management

Status: done

## Story

As an admin,
I want to approve/reject pending users and activate/deactivate accounts,
so that I control who can access the app.

## Acceptance Criteria

1. **Given** I am admin, **When** I GET `/api/admin/users?status=pending`, **Then** I see pending users
2. **Given** I am admin, **When** I PUT `/api/admin/users/{id}/approve`, **Then** user status → active
3. **Given** I am admin, **When** I PUT `/api/admin/users/{id}/reject`, **Then** user status → rejected
4. **Given** I am admin, **When** I PUT `/api/admin/users/{id}/deactivate`, **Then** user status → inactive
5. **Given** any admin action, **When** it completes, **Then** it is logged to audit trail
6. **Given** the project is complete, **When** I run ruff + mypy, **Then** both pass

## Tasks / Subtasks

- [x] Task 1: Add user management methods to admin service
- [x] Task 2: Add user management endpoints to admin router
- [x] Task 3: Add user list/filter to UserRepository
- [x] Task 4: Add admin user schemas
- [x] Task 5: Verify ruff + mypy

## Dev Notes

- Email notifications (SMTP) for approval/rejection deferred — `core/email.py` not yet created
- Use `require_role("admin")` for all endpoints
- [Source: epics.md#Story 2.6]

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.6

### Debug Log References

- Forward reference `AdminUserResponse` in return type caused ruff F821 — moved imports to top level

### Completion Notes List

- Added GET `/api/admin/users?status=pending` — list users by status
- Added PUT `/api/admin/users/{id}/approve`, `/reject`, `/deactivate`, `/reactivate`
- All endpoints protected by `require_role("admin")`
- All actions audit logged
- Added `get_by_status`, `update_status` to UserRepository
- Added `AdminUserResponse` schema
- 56 tests passing (2 new)

### File List

- backend/app/admin/schemas.py (modified — added AdminUserResponse)
- backend/app/admin/service.py (modified — added list_users_by_status, update_user_status)
- backend/app/admin/router.py (modified — added user management endpoints)
- backend/app/auth/repository.py (modified — added get_by_status, update_status)
- backend/tests/admin/test_user_management.py (new)
