# Story 3.2: Audio Download & Pre-Cache System

Status: done

## Story

As the system, I want to download and cache audio files for top trending sounds.

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.6

### File List

- backend/app/scraper/downloader.py (new — httpx download + yt-dlp fallback + pre_cache_top_sounds)
- backend/tests/scraper/test_downloader.py (new)
