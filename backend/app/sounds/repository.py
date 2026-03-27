"""Repository layer for sounds module."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.sounds.models import Sound


class SoundRepository:
    """Database operations for Sound model."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_tiktok_id(self, tiktok_sound_id: str) -> Sound | None:
        """Find sound by TikTok sound ID."""
        result = await self.db.execute(
            select(Sound).where(Sound.tiktok_sound_id == tiktok_sound_id)
        )
        return result.scalar_one_or_none()

    async def upsert(
        self,
        tiktok_sound_id: str,
        title: str,
        artist: str,
        play_url: str | None,
        cover_url: str | None,
        duration: int,
        usage_count: int,
        trend_rank: int | None,
        is_original: bool,
        last_trending_at: datetime,
    ) -> Sound:
        """Insert or update a sound by tiktok_sound_id."""
        sound = await self.get_by_tiktok_id(tiktok_sound_id)
        if sound:
            sound.title = title
            sound.artist = artist
            sound.play_url = play_url
            sound.cover_url = cover_url
            sound.duration = duration
            sound.usage_count = usage_count
            sound.trend_rank = trend_rank
            sound.is_original = is_original
            sound.last_trending_at = last_trending_at
        else:
            sound = Sound(
                tiktok_sound_id=tiktok_sound_id,
                title=title,
                artist=artist,
                play_url=play_url,
                cover_url=cover_url,
                duration=duration,
                usage_count=usage_count,
                trend_rank=trend_rank,
                is_original=is_original,
                last_trending_at=last_trending_at,
            )
            self.db.add(sound)
        await self.db.flush()
        return sound

    async def get_trending(
        self, page: int = 1, page_size: int = 20
    ) -> tuple[list[Sound], int]:
        """Get trending sounds sorted by trend_rank, paginated.

        Returns (sounds, total_count).
        """
        from sqlalchemy import func as sa_func

        # Count
        count_result = await self.db.execute(
            select(sa_func.count())
            .select_from(Sound)
            .where(Sound.trend_rank.isnot(None))
        )
        total = count_result.scalar_one()

        # Paginated results
        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(Sound)
            .where(Sound.trend_rank.isnot(None))
            .order_by(Sound.trend_rank.asc())
            .offset(offset)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def search(
        self, query: str, page: int = 1, page_size: int = 20
    ) -> tuple[list[Sound], int]:
        """Search sounds by title or artist (LIKE query for MVP).

        Returns (sounds, total_count).
        """
        from sqlalchemy import func as sa_func
        from sqlalchemy import or_

        like_pattern = f"%{query}%"
        where_clause = or_(
            Sound.title.ilike(like_pattern),
            Sound.artist.ilike(like_pattern),
        )

        count_result = await self.db.execute(
            select(sa_func.count()).select_from(Sound).where(where_clause)
        )
        total = count_result.scalar_one()

        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(Sound)
            .where(where_clause)
            .order_by(Sound.trend_rank.asc().nullslast())
            .offset(offset)
            .limit(page_size)
        )
        return list(result.scalars().all()), total
