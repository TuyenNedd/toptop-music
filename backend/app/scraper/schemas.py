"""Internal data models for scraped TikTok data."""

from typing import Any


def extract_sound_from_video(video: dict[str, Any]) -> dict[str, Any] | None:
    """Extract sound metadata from a TikTok video dict.

    Returns None if no music info found.
    """
    music = video.get("music") or video.get("musicInfos")
    if not music:
        return None

    # Handle both dict and nested structures
    if isinstance(music, dict):
        return {
            "tiktok_sound_id": str(music.get("id", "")),
            "title": music.get("title", "Unknown"),
            "artist": music.get("authorName", "Unknown"),
            "play_url": music.get("playUrl", ""),
            "cover_url": (music.get("coverLarge") or music.get("coverMedium") or ""),
            "duration": music.get("duration", 0),
            "is_original": music.get("original", False),
        }

    return None
