from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.dependencies import get_db, require_api_key
from app.models.media_item import (
    CreatorLink,
    GenreLink,
    MediaItem,
    MediaItemCreatorLink,
    MediaItemGenreLink,
    MediaItemV2Create,
    MediaItemV2Read,
    MediaItemV2Update,
)
from app.models.user import User
from app.routers.api_v2.helpers import (
    build_media_item_v2_read,
    ensure_creator_exists,
    ensure_franchise_exists,
    ensure_genre_exists,
    ensure_medium_exists,
    get_media_item_or_404,
)

router = APIRouter(prefix="/media-items", tags=["v2"])


@router.get("", response_model=list[MediaItemV2Read])
async def list_media_items(
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_api_key),
) -> list[MediaItemV2Read]:
    result = await session.execute(select(MediaItem).order_by(MediaItem.id))
    items = list(result.scalars().all())
    return [await build_media_item_v2_read(session, item) for item in items]


@router.get("/{media_item_id}", response_model=MediaItemV2Read)
async def get_media_item(
    media_item_id: int,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_api_key),
) -> MediaItemV2Read:
    media_item = await get_media_item_or_404(session, media_item_id)
    return await build_media_item_v2_read(session, media_item)


@router.post("", response_model=MediaItemV2Read, status_code=status.HTTP_201_CREATED)
async def create_media_item(
    body: MediaItemV2Create,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_api_key),
) -> MediaItemV2Read:
    await ensure_medium_exists(session, body.medium_id)
    await ensure_franchise_exists(session, body.franchise_id)

    media_item = MediaItem.model_validate(body)
    session.add(media_item)
    await session.commit()
    await session.refresh(media_item)
    return await build_media_item_v2_read(session, media_item)


@router.put("/{media_item_id}", response_model=MediaItemV2Read)
async def update_media_item(
    media_item_id: int,
    body: MediaItemV2Update,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_api_key),
) -> MediaItemV2Read:
    media_item = await get_media_item_or_404(session, media_item_id)
    await ensure_medium_exists(session, body.medium_id)
    await ensure_franchise_exists(session, body.franchise_id)

    media_item.title = body.title
    media_item.description = body.description
    media_item.release_year = body.release_year
    media_item.franchise_id = body.franchise_id
    media_item.medium_id = body.medium_id
    session.add(media_item)
    await session.commit()
    await session.refresh(media_item)
    return await build_media_item_v2_read(session, media_item)


@router.delete("/{media_item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media_item(
    media_item_id: int,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_api_key),
) -> None:
    media_item = await get_media_item_or_404(session, media_item_id)
    await session.delete(media_item)
    await session.commit()


@router.post(
    "/{media_item_id}/creators",
    response_model=MediaItemV2Read,
    status_code=status.HTTP_201_CREATED,
)
async def link_creator(
    media_item_id: int,
    body: CreatorLink,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_api_key),
) -> MediaItemV2Read:
    media_item = await get_media_item_or_404(session, media_item_id)
    await ensure_creator_exists(session, body.creator_id)

    existing = await session.get(
        MediaItemCreatorLink,
        {"media_item_id": media_item_id, "creator_id": body.creator_id},
    )
    if existing:
        raise HTTPException(status_code=400, detail="Creator already linked")

    session.add(MediaItemCreatorLink(media_item_id=media_item_id, creator_id=body.creator_id))
    await session.commit()
    return await build_media_item_v2_read(session, media_item)


@router.delete("/{media_item_id}/creators/{creator_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unlink_creator(
    media_item_id: int,
    creator_id: int,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_api_key),
) -> None:
    await get_media_item_or_404(session, media_item_id)
    link = await session.get(
        MediaItemCreatorLink,
        {"media_item_id": media_item_id, "creator_id": creator_id},
    )
    if not link:
        raise HTTPException(status_code=404, detail="Creator link not found")
    await session.delete(link)
    await session.commit()


@router.post(
    "/{media_item_id}/genres",
    response_model=MediaItemV2Read,
    status_code=status.HTTP_201_CREATED,
)
async def link_genre(
    media_item_id: int,
    body: GenreLink,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_api_key),
) -> MediaItemV2Read:
    media_item = await get_media_item_or_404(session, media_item_id)
    await ensure_genre_exists(session, body.genre_id)

    existing = await session.get(
        MediaItemGenreLink,
        {"media_item_id": media_item_id, "genre_id": body.genre_id},
    )
    if existing:
        raise HTTPException(status_code=400, detail="Genre already linked")

    session.add(MediaItemGenreLink(media_item_id=media_item_id, genre_id=body.genre_id))
    await session.commit()
    return await build_media_item_v2_read(session, media_item)


@router.delete("/{media_item_id}/genres/{genre_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unlink_genre(
    media_item_id: int,
    genre_id: int,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_api_key),
) -> None:
    await get_media_item_or_404(session, media_item_id)
    link = await session.get(
        MediaItemGenreLink,
        {"media_item_id": media_item_id, "genre_id": genre_id},
    )
    if not link:
        raise HTTPException(status_code=404, detail="Genre link not found")
    await session.delete(link)
    await session.commit()
