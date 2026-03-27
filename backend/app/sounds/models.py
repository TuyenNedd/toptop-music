"""SQLAlchemy models for sounds module."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Sound(Base):
    """Sound metadata from TikTok trending data."""

    __tablename__ = "sounds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tiktok_sound_id: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    artist: Mapped[str] = mapped_column(String(255), nullable=False, default="Unknown")
    play_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration: Mapped[int] = mapped_column(Integer, default=0)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    trend_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_original: Mapped[bool] = mapped_column(Boolean, default=False)
    last_trending_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Cache fields
    cached: Mapped[bool] = mapped_column(Boolean, default=False)
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    cached_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_accessed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        Index("idx_sounds_tiktok_id", "tiktok_sound_id"),
        Index("idx_sounds_trend_rank", "trend_rank"),
        Index("idx_sounds_title_artist", "title", "artist"),
    )


class Favorite(Base):
    """User's favorite sound."""

    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    sound_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("idx_favorites_user_sound", "user_id", "sound_id", unique=True),
        Index("idx_favorites_user_id", "user_id"),
    )


class Playlist(Base):
    """User's playlist."""

    __tablename__ = "playlists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (Index("idx_playlists_user_id", "user_id"),)


class PlaylistSound(Base):
    """Sound in a playlist (many-to-many)."""

    __tablename__ = "playlist_sounds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    playlist_id: Mapped[int] = mapped_column(Integer, nullable=False)
    sound_id: Mapped[int] = mapped_column(Integer, nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("idx_playlist_sounds_playlist", "playlist_id"),
        Index("idx_playlist_sounds_unique", "playlist_id", "sound_id", unique=True),
    )
