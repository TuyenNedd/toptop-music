"""Tests for scraper data extraction (Story 3.1)."""

from app.scraper.schemas import extract_sound_from_video


def test_extract_sound_from_video_with_music() -> None:
    """Extracts sound metadata from video with music dict."""
    video = {
        "music": {
            "id": "12345",
            "title": "Test Song",
            "authorName": "Test Artist",
            "playUrl": "https://example.com/audio.mp3",
            "coverLarge": "https://example.com/cover.jpg",
            "duration": 30,
            "original": True,
        }
    }
    result = extract_sound_from_video(video)
    assert result is not None
    assert result["tiktok_sound_id"] == "12345"
    assert result["title"] == "Test Song"
    assert result["artist"] == "Test Artist"
    assert result["play_url"] == "https://example.com/audio.mp3"
    assert result["duration"] == 30
    assert result["is_original"] is True


def test_extract_sound_from_video_no_music() -> None:
    """Returns None when video has no music info."""
    video = {"id": "video123", "desc": "No music"}
    result = extract_sound_from_video(video)
    assert result is None


def test_extract_sound_fallback_cover() -> None:
    """Falls back to coverMedium when coverLarge missing."""
    video = {
        "music": {
            "id": "67890",
            "title": "Song",
            "authorName": "Artist",
            "coverMedium": "https://example.com/medium.jpg",
            "duration": 15,
        }
    }
    result = extract_sound_from_video(video)
    assert result is not None
    assert result["cover_url"] == "https://example.com/medium.jpg"
