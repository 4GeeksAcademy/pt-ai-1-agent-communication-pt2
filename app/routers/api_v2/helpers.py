from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.creator import Creator
from app.models.franchise import Franchise
from app.models.genre import Genre
from app.models.media_item import (
    MediaItem,
    MediaItemCreatorLink,
    MediaItemGenreLink,
    MediaItemV2Read,
)
from app.models.medium import Medium


async def get_media_item_or_404(session: AsyncSession, media_item_id: int) -> MediaItem:
    media_item = await session.get(MediaItem, media_item_id)
    if not media_item:
        raise HTTPException(status_code=404, detail="Media item not found")
    return media_item


async def build_media_item_v2_read(session: AsyncSession, media_item: MediaItem) -> MediaItemV2Read:
    creator_result = await session.execute(
        select(MediaItemCreatorLink.creator_id).where(
            MediaItemCreatorLink.media_item_id == media_item.id
        )
    )
    genre_result = await session.execute(
        select(MediaItemGenreLink.genre_id).where(
            MediaItemGenreLink.media_item_id == media_item.id
        )
    )
    return MediaItemV2Read(
        id=media_item.id,
        title=media_item.title,
        description=media_item.description,
        release_year=media_item.release_year,
        franchise_id=media_item.franchise_id,
        medium_id=media_item.medium_id,
        creator_ids=list(creator_result.scalars().all()),
        genre_ids=list(genre_result.scalars().all()),
    )


async def ensure_medium_exists(session: AsyncSession, medium_id: int) -> None:
    if not await session.get(Medium, medium_id):
        raise HTTPException(status_code=404, detail="Medium not found")


async def ensure_franchise_exists(session: AsyncSession, franchise_id: int | None) -> None:
    if franchise_id is not None and not await session.get(Franchise, franchise_id):
        raise HTTPException(status_code=404, detail="Franchise not found")


async def ensure_creator_exists(session: AsyncSession, creator_id: int) -> Creator:
    creator = await session.get(Creator, creator_id)
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")
    return creator


async def ensure_genre_exists(session: AsyncSession, genre_id: int) -> Genre:
    genre = await session.get(Genre, genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    return genre
