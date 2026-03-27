# Story 3.3: On-Demand Audio Caching

Status: done

## Story

As the system, I want to download and cache audio on-demand when a user plays an uncached sound.

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.6

### File List

- backend/app/sounds/stream.py (new — ensure_cached with per-sound locks to prevent duplicate downloads)
