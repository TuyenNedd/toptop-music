"""Tests for audio downloader (Story 3.2)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.scraper.downloader import download_audio


@pytest.mark.asyncio
@patch("app.scraper.downloader.httpx.AsyncClient")
async def test_download_audio_httpx_success(mock_client_cls: MagicMock) -> None:
    """Downloads audio via httpx when play_url is valid."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"content-type": "audio/mpeg"}
    mock_resp.content = b"fake audio data"
    mock_resp.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client_cls.return_value = mock_client

    with patch("builtins.open", MagicMock()):
        result = await download_audio("test123", "https://example.com/audio.mp3")

    assert result is not None
    assert "test123" in result


@pytest.mark.asyncio
async def test_download_audio_no_url_returns_none() -> None:
    """Returns None when no play_url and yt-dlp fails."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stderr="error")
        result = await download_audio("test456", None)
    assert result is None
