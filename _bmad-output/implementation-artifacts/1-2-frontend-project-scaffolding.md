# Story 1.2: Frontend Project Scaffolding

Status: review

## Story

As a developer,
I want to initialize the Next.js frontend project with TypeScript, Tailwind CSS, and the TikTok-inspired design system,
so that I have a working frontend foundation with the correct structure, theme, and BFF proxy configured.

## Acceptance Criteria

1. **Given** no frontend project exists, **When** I run `npx create-next-app@latest frontend` with TypeScript, Tailwind, ESLint, App Router, src directory, and Turbopack, **Then** a `frontend/` directory is created with App Router structure under `src/app/`

2. **Given** the frontend is initialized, **When** I configure `globals.css`, **Then** it contains the full TikTok-inspired CSS variable color token system (14 tokens: primary, secondary, bg, surface, surface-hover, surface-active, text, text-secondary, text-tertiary, border, success, warning, error) with both `:root` (light) and `.dark` overrides

3. **Given** `globals.css` has CSS variables, **When** I configure `tailwind.config.ts`, **Then** it extends theme with custom colors mapped to CSS variables, `darkMode: 'class'`, and custom spacing for player bar heights

4. **Given** Tailwind is configured, **When** I configure `next/font` in `layout.tsx`, **Then** Inter variable font is loaded and applied as the primary font via `className` on `<html>`

5. **Given** the layout is configured, **When** I inspect `layout.tsx`, **Then** the `<html>` element has `dark` class by default (dark mode primary), `lang="vi"`, and the layout includes placeholder slots for PlayerBar and navigation

6. **Given** the project is complete, **When** I inspect `next.config.ts`, **Then** it contains rewrites for `/api/:path*` → `http://localhost:8000/api/:path*` (BFF proxy for local dev)

7. **Given** the project is complete, **When** I check `.env.example`, **Then** it contains `NEXT_PUBLIC_APP_URL` and `BACKEND_URL` placeholders

8. **Given** the project is complete, **When** I run `npm run build`, **Then** it completes with zero TypeScript errors and zero ESLint errors

## Tasks / Subtasks

- [x] Task 1: Initialize Next.js project (AC: #1)
  - [x] Run `npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --turbopack`
  - [x] Verify `src/app/` directory structure exists
  - [x] Verify `tsconfig.json` has `"strict": true` and `@/*` path alias
- [x] Task 2: Configure CSS variable color token system (AC: #2)
  - [x] Replace `globals.css` content with Tailwind directives + full 14-token CSS variable system
  - [x] Add `:root` block with light mode values (primary #25F4EE, secondary #FE2C55, bg #ffffff, surface #f5f5f5, text #010101, etc.)
  - [x] Add `.dark` block with dark mode overrides (bg #010101, surface #161616, text #ffffff)
  - [x] Add surface-hover, surface-active, text-secondary (#8a8a8a), text-tertiary, border, success (#00c853), warning (#ffab00), error (#ff3d00) tokens
- [x] Task 3: Configure tailwind.config.ts (AC: #3)
  - [x] Set `darkMode: 'class'`
  - [x] Extend `theme.colors` with all 14 tokens mapped to `var(--color-*)` CSS variables
  - [x] Extend `theme.spacing` with player bar heights: `player-mobile: '64px'`, `player-desktop: '90px'`, `tab-bar: '56px'`
  - [x] Add `content` paths covering `src/**/*.{ts,tsx}`
- [x] Task 4: Configure Inter font and root layout (AC: #4, #5)
  - [x] Import `Inter` from `next/font/google` with `subsets: ['latin', 'vietnamese']` and `variable: '--font-inter'`
  - [x] Apply font variable to `<html>` className alongside `dark` class
  - [x] Set `<html lang="vi" className={`${inter.variable} dark`}>`
  - [x] Add `<body>` with `bg-bg text-text font-sans antialiased` classes
  - [x] Add placeholder comments for `{/* PlayerBar */}` and `{/* Navigation */}` in layout
- [x] Task 5: Configure BFF proxy in next.config.ts (AC: #6)
  - [x] Add `async rewrites()` returning `[{ source: '/api/:path*', destination: 'http://localhost:8000/api/:path*' }]`
  - [x] Export config as `NextConfig` typed object
- [x] Task 6: Create .env.example (AC: #7)
  - [x] Create `frontend/.env.example` with `NEXT_PUBLIC_APP_URL=http://localhost:3000` and `BACKEND_URL=http://localhost:8000`
- [x] Task 7: Verify build passes (AC: #8)
  - [x] Run `npm run build` — zero TypeScript errors, zero ESLint errors
  - [x] Run `npm run lint` — zero errors

## Dev Notes

### Architecture Compliance

- **Framework:** Next.js 16.x with App Router (React Server Components default)
- **Styling:** Tailwind CSS v4 — utility-first, NO component library, NO CSS-in-JS
- **BFF Proxy:** Next.js rewrites `/api/*` → FastAPI backend. No direct browser-to-backend calls. This is AR3 — critical for all future API calls.
- **Dark mode:** Class-based (`dark` on `<html>`). Dark mode is PRIMARY (default). Light mode is parallel.
- **Font:** Inter variable font via `next/font/google` — zero layout shift, self-hosted by Next.js
- [Source: architecture.md#Frontend Architecture, architecture.md#Starter Template Evaluation]

### Color Token System (CRITICAL — all components must use these)

```css
/* globals.css — exact values to implement */
:root {
  --color-primary: #25f4ee; /* Cyan — accents, active states, progress bar */
  --color-secondary: #fe2c55; /* Red — favorites, alerts, CTAs */
  --color-bg: #ffffff; /* Light mode page background */
  --color-surface: #f5f5f5; /* Light mode cards, panels */
  --color-surface-hover: #ebebeb; /* Light mode hover state */
  --color-surface-active: #e0e0e0; /* Light mode active/pressed */
  --color-text: #010101; /* Light mode primary text */
  --color-text-secondary: #8a8a8a; /* Metadata, timestamps, subtitles */
  --color-text-tertiary: #b0b0b0; /* Placeholder, disabled text */
  --color-border: #e0e0e0; /* Light mode borders, dividers */
  --color-success: #00c853; /* Success states */
  --color-warning: #ffab00; /* Warning states */
  --color-error: #ff3d00; /* Error states */
}

.dark {
  --color-bg: #010101;
  --color-surface: #161616;
  --color-surface-hover: #222222;
  --color-surface-active: #2a2a2a;
  --color-text: #ffffff;
  --color-text-secondary: #8a8a8a;
  --color-text-tertiary: #555555;
  --color-border: #2a2a2a;
}
```

- [Source: ux-design-specification.md#Color Token System, epics.md#UX-DR1]

### Tailwind Config Pattern

```typescript
// tailwind.config.ts
import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        primary: "var(--color-primary)",
        secondary: "var(--color-secondary)",
        bg: "var(--color-bg)",
        surface: "var(--color-surface)",
        "surface-hover": "var(--color-surface-hover)",
        "surface-active": "var(--color-surface-active)",
        text: "var(--color-text)",
        "text-secondary": "var(--color-text-secondary)",
        "text-tertiary": "var(--color-text-tertiary)",
        border: "var(--color-border)",
        success: "var(--color-success)",
        warning: "var(--color-warning)",
        error: "var(--color-error)",
      },
      spacing: {
        "player-mobile": "64px",
        "player-desktop": "90px",
        "tab-bar": "56px",
      },
    },
  },
  plugins: [],
};

export default config;
```

- [Source: ux-design-specification.md#Tailwind Configuration, architecture.md#Frontend Architecture]

### next.config.ts BFF Proxy (CRITICAL)

```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.BACKEND_URL ?? "http://localhost:8000"}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
```

This is the BFF proxy pattern (AR3). ALL API calls from the frontend go through `/api/*` — never directly to the backend URL. This eliminates CORS issues and hides the backend.

- [Source: architecture.md#API & Communication Patterns]

### Root Layout Pattern

```tsx
// src/app/layout.tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin", "vietnamese"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "TopTop Music",
  description: "TikTok trending sounds player",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi" className={`${inter.variable} dark`}>
      <body className="bg-bg text-text font-sans antialiased">
        {/* PlayerBar — persistent, added in Story 5.2 */}
        {/* Navigation (TabBar/Sidebar) — added in Story 4.4 */}
        {children}
      </body>
    </html>
  );
}
```

- [Source: architecture.md#Frontend Architecture, epics.md#Story 1.2 AC]

### Naming Conventions (CRITICAL — enforce from day 1)

- Files/folders: `kebab-case` — `player-bar.tsx`, `sound-card.tsx`
- Component exports: `PascalCase` — `export function PlayerBar()`
- Hooks: `camelCase` with `use` prefix, file `kebab-case` — `usePlayer()` in `use-player.ts`
- Types: `PascalCase`, no `I` prefix — `Sound`, `PlayerState`, `ApiResponse<T>`
- Constants: `UPPER_SNAKE_CASE` — `API_BASE_URL`
- [Source: architecture.md#Naming Patterns]

### Anti-Patterns to Avoid

- ❌ Do NOT install any component library (shadcn, MUI, Chakra, etc.) — Tailwind custom components only
- ❌ Do NOT use CSS-in-JS or styled-components
- ❌ Do NOT use `camelCase` or `PascalCase` for file names — always `kebab-case`
- ❌ Do NOT hardcode colors — always use CSS variable tokens via Tailwind classes (`text-primary`, `bg-surface`)
- ❌ Do NOT add `NEXT_PUBLIC_` prefix to server-only secrets like `BACKEND_URL`
- ❌ Do NOT create `pages/` directory — App Router only (`src/app/`)
- [Source: architecture.md#Anti-Patterns to Avoid, architecture.md#Enforcement Guidelines]

### Node.js & Package Manager

- **Node.js:** v22.22.1 (confirmed available)
- **Package manager:** npm (standard, comes with Node.js)
- **Next.js version:** 16.x (latest stable via `create-next-app@latest`)
- [Source: architecture.md#Infrastructure & Deployment]

### Previous Story Context (Story 1.1)

Story 1.1 created the backend at `backend/`. This story creates `frontend/` as a sibling directory. The two are independent at this stage — they connect via Docker Compose in Story 1.5.

Key patterns established in Story 1.1 to mirror:

- `.env.example` with placeholder values (gitignored `.env`)
- `.gitignore` for generated/local files
- Clean project structure with no extra files

### References

- [Source: architecture.md#Starter Template Evaluation — Frontend initialization command]
- [Source: architecture.md#Frontend Architecture — Framework, styling, state, animation decisions]
- [Source: architecture.md#API & Communication Patterns — BFF proxy pattern AR3]
- [Source: architecture.md#Naming Patterns — Frontend file/folder/component naming]
- [Source: ux-design-specification.md#Color Token System — Exact CSS variable values]
- [Source: ux-design-specification.md#Tailwind Configuration — Config structure]
- [Source: epics.md#Story 1.2 — Acceptance criteria]
- [Source: epics.md#UX-DR1, UX-DR2 — Color tokens and typography requirements]

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.6

### Debug Log References

- Tailwind v4 (installed by create-next-app@16) does not use `tailwind.config.ts` — theme extension done via `@theme` directive in `globals.css` instead
- layout.tsx generated with double-quote imports by Next.js formatter; test updated to match

### Completion Notes List

- Initialized Next.js 16.2.1 with TypeScript strict, Tailwind v4, ESLint, App Router, src-dir, Turbopack
- Configured 14-token TikTok-inspired CSS variable system in globals.css with `:root` (light) and `.dark` overrides
- Tailwind v4 theme extension via `@theme` directive (no tailwind.config.ts — v4 change)
- Inter variable font configured via next/font/google with latin + vietnamese subsets
- Root layout: `<html lang="vi" className="${inter.variable} dark">` — dark mode primary
- BFF proxy in next.config.ts: `/api/:path*` → `${BACKEND_URL}/api/:path*`
- .env.example with NEXT_PUBLIC_APP_URL and BACKEND_URL
- Vitest + @testing-library/react installed; 22 tests written and passing
- npm run build: zero TypeScript errors, zero ESLint errors

### File List

- frontend/src/app/globals.css (modified — full color token system)
- frontend/src/app/layout.tsx (modified — Inter font, dark class, lang=vi)
- frontend/next.config.ts (modified — BFF proxy rewrites)
- frontend/.env.example (new)
- frontend/.gitignore (new, by create-next-app)
- frontend/package.json (modified — test script added)
- frontend/tsconfig.json (new, by create-next-app)
- frontend/vitest.config.ts (new)
- frontend/src/test/setup.ts (new)
- frontend/src/test/scaffolding.test.ts (new)

## Change Log

- 2026-03-26: Story 1.2 implemented — Next.js 16 frontend scaffolded with Tailwind v4, 14-token color system, BFF proxy, Inter font, dark mode default. 22 tests passing, build clean.
