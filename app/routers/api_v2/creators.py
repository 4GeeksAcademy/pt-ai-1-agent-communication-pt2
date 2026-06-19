from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.dependencies import get_db, require_api_key
from app.models.creator import Creator, CreatorCreate, CreatorRead, CreatorUpdate
from app.models.user import User

router = APIRouter(prefix="/creators", tags=["v2"])


@router.get("", response_model=list[CreatorRead])
async def list_creators(
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_api_key),
) -> list[Creator]:
    result = await session.execute(select(Creator).order_by(Creator.id))
    return list(result.scalars().all())


@router.get("/{creator_id}", response_model=CreatorRead)
async def get_creator(
    creator_id: int,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_api_key),
) -> Creator:
    creator = await session.get(Creator, creator_id)
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")
    return creator


@router.post("", response_model=CreatorRead, status_code=status.HTTP_201_CREATED)
async def create_creator(
    body: CreatorCreate,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_api_key),
) -> Creator:
    creator = Creator.model_validate(body)
    session.add(creator)
    await session.commit()
    await session.refresh(creator)
    return creator


@router.put("/{creator_id}", response_model=CreatorRead)
async def update_creator(
    creator_id: int,
    body: CreatorUpdate,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_api_key),
) -> Creator:
    creator = await session.get(Creator, creator_id)
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")
    creator.name = body.name
    creator.bio = body.bio
    session.add(creator)
    await session.commit()
    await session.refresh(creator)
    return creator


@router.delete("/{creator_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_creator(
    creator_id: int,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_api_key),
) -> None:
    creator = await session.get(Creator, creator_id)
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")
    await session.delete(creator)
    await session.commit()
