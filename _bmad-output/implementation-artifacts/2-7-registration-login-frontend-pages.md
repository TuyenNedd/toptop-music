# Story 2.7: Registration & Login Frontend Pages

Status: done

## Story

As a visitor,
I want registration and login pages with intuitive UI,
so that I can create an account and sign in easily.

## Acceptance Criteria

1. **Given** I visit `/login`, **Then** I see a login form with username/email, password, "Log in" button, and link to register
2. **Given** I visit `/register`, **Then** I see two paths: invite code and sign-up for approval
3. **Given** I submit a form, **Then** validation errors show below inputs on blur
4. **Given** I submit, **Then** the button shows loading spinner during API call
5. **Given** successful invite registration, **Then** redirect to home
6. **Given** successful approval registration, **Then** show "Pending approval" screen
7. **Given** the pages, **Then** they use kebab-case files, Tailwind, dark mode

## Tasks / Subtasks

- [x] Task 1: Create API client utility
- [x] Task 2: Create login page at `src/app/(auth)/login/page.tsx`
- [x] Task 3: Create register page at `src/app/(auth)/register/page.tsx`
- [x] Task 4: Create auth form components
- [x] Task 5: Verify build passes

## Dev Notes

- Files: `kebab-case` — `login-form.tsx`, `register-form.tsx`
- Components: `PascalCase` exports — `LoginForm`, `RegisterForm`
- API calls via `/api/auth/login`, `/api/auth/register` (BFF proxy)
- Use Tailwind dark mode classes (`bg-bg`, `text-text`, `bg-surface`)
- [Source: architecture.md#Frontend Code Naming, epics.md#Story 2.7]

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.6

### Debug Log References

- `RegisterForm` uses `useSearchParams()` which requires `Suspense` boundary — wrapped in register page
- All form inputs use Tailwind color tokens (`bg-surface`, `text-text`, `border-border`, `focus:ring-primary`)

### Completion Notes List

- Created `lib/api-client.ts` — fetch wrapper with `apiPost`, `apiGet`, typed `ApiResponse<T>`
- Created `components/auth/login-form.tsx` — login form with loading spinner, error display
- Created `components/auth/register-form.tsx` — dual-path registration (invite code / approval), pending screen, invite code pre-fill from URL
- Created `(auth)/login/page.tsx` and `(auth)/register/page.tsx`
- All files kebab-case, components PascalCase, Tailwind dark mode
- Build passes, lint clean, 23 frontend tests pass

### File List

- frontend/src/lib/api-client.ts (new)
- frontend/src/components/auth/login-form.tsx (new)
- frontend/src/components/auth/register-form.tsx (new)
- frontend/src/app/(auth)/login/page.tsx (new)
- frontend/src/app/(auth)/register/page.tsx (new)
