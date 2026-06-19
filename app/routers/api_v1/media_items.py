from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.dependencies import get_db
from app.models.media_item import (
    MediaItem,
    MediaItemCreate,
    MediaItemV1Read,
    MediaItemV1Update,
)

router = APIRouter(prefix="/media-items", tags=["v1"])


@router.get("", response_model=list[MediaItemV1Read])
async def list_media_items(session: AsyncSession = Depends(get_db)) -> list[MediaItem]:
    result = await session.execute(select(MediaItem).order_by(MediaItem.id))
    return list(result.scalars().all())


@router.get("/{media_item_id}", response_model=MediaItemV1Read)
async def get_media_item(
    media_item_id: int,
    session: AsyncSession = Depends(get_db),
) -> MediaItem:
    media_item = await session.get(MediaItem, media_item_id)
    if not media_item:
        raise HTTPException(status_code=404, detail="Media item not found")
    return media_item


@router.post("", response_model=MediaItemV1Read, status_code=status.HTTP_201_CREATED)
async def create_media_item(
    body: MediaItemCreate,
    session: AsyncSession = Depends(get_db),
) -> MediaItem:
    media_item = MediaItem.model_validate(body)
    session.add(media_item)
    await session.commit()
    await session.refresh(media_item)
    return media_item


@router.put("/{media_item_id}", response_model=MediaItemV1Read)
async def update_media_item(
    media_item_id: int,
    body: MediaItemV1Update,
    session: AsyncSession = Depends(get_db),
) -> MediaItem:
    media_item = await session.get(MediaItem, media_item_id)
    if not media_item:
        raise HTTPException(status_code=404, detail="Media item not found")

    media_item.title = body.title
    media_item.description = body.description
    media_item.release_year = body.release_year
    session.add(media_item)
    await session.commit()
    await session.refresh(media_item)
    return media_item


@router.delete("/{media_item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media_item(
    media_item_id: int,
    session: AsyncSession = Depends(get_db),
) -> None:
    media_item = await session.get(MediaItem, media_item_id)
    if not media_item:
        raise HTTPException(status_code=404, detail="Media item not found")
    await session.delete(media_item)
    await session.commit()
