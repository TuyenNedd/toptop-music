"""Playlist endpoints — CRUD and sound management."""

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import delete, select
from sqlalchemy import func as sa_func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.core.exceptions import AppException
from app.database import get_db
from app.sounds.models import Playlist, PlaylistSound, Sound
from app.sounds.schemas import SoundResponse

router = APIRouter(prefix="/api/playlists", tags=["playlists"])


@router.post("", status_code=201)
async def create_playlist(
    name: str = Query(min_length=1, max_length=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Create a new playlist."""
    playlist = Playlist(user_id=current_user.id, name=name)
    db.add(playlist)
    await db.flush()
    await db.refresh(playlist)
    await db.commit()
    return {
        "data": {"id": playlist.id, "name": playlist.name},
        "error": None,
    }


@router.get("")
async def list_playlists(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """List user's playlists with sound count."""
    result = await db.execute(
        select(Playlist)
        .where(Playlist.user_id == current_user.id)
        .order_by(Playlist.updated_at.desc())
    )
    playlists = list(result.scalars().all())

    data = []
    for p in playlists:
        count_q = (
            select(sa_func.count())
            .select_from(PlaylistSound)
            .where(PlaylistSound.playlist_id == p.id)
        )
        count = (await db.execute(count_q)).scalar_one()
        data.append({"id": p.id, "name": p.name, "sound_count": count})

    return {"data": data, "error": None}


@router.put("/{playlist_id}")
async def rename_playlist(
    playlist_id: int,
    name: str = Query(min_length=1, max_length=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Rename a playlist."""
    result = await db.execute(
        select(Playlist).where(
            Playlist.id == playlist_id, Playlist.user_id == current_user.id
        )
    )
    playlist = result.scalar_one_or_none()
    if not playlist:
        raise AppException(
            code="PLAYLIST_NOT_FOUND", message="Playlist not found", status_code=404
        )
    playlist.name = name
    await db.commit()
    return {"data": {"id": playlist.id, "name": playlist.name}, "error": None}


@router.delete("/{playlist_id}", status_code=204)
async def delete_playlist(
    playlist_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a playlist and its sound associations."""
    await db.execute(
        delete(PlaylistSound).where(PlaylistSound.playlist_id == playlist_id)
    )
    await db.execute(
        delete(Playlist).where(
            Playlist.id == playlist_id, Playlist.user_id == current_user.id
        )
    )
    await db.commit()


@router.post("/{playlist_id}/sounds", status_code=201)
async def add_sound_to_playlist(
    playlist_id: int,
    sound_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Add a sound to a playlist."""
    ps = PlaylistSound(playlist_id=playlist_id, sound_id=sound_id)
    db.add(ps)
    try:
        await db.flush()
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise AppException(
            code="PLAYLIST_SOUND_DUPLICATE",
            message="Sound already in playlist",
            status_code=409,
        )
    return {"data": {"playlist_id": playlist_id, "sound_id": sound_id}, "error": None}


@router.delete("/{playlist_id}/sounds/{sound_id}")
async def remove_sound_from_playlist(
    playlist_id: int,
    sound_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Remove a sound from a playlist."""
    await db.execute(
        delete(PlaylistSound).where(
            PlaylistSound.playlist_id == playlist_id,
            PlaylistSound.sound_id == sound_id,
        )
    )
    await db.commit()
    return {"data": {"removed": True}, "error": None}


@router.get("/{playlist_id}/sounds")
async def get_playlist_sounds(
    playlist_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Get all sounds in a playlist."""
    result = await db.execute(
        select(Sound)
        .join(PlaylistSound, PlaylistSound.sound_id == Sound.id)
        .where(PlaylistSound.playlist_id == playlist_id)
        .order_by(PlaylistSound.position.asc())
    )
    sounds = list(result.scalars().all())
    return {
        "data": [SoundResponse.model_validate(s).model_dump() for s in sounds],
        "error": None,
    }
