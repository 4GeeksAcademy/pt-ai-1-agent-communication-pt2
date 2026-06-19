from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.dependencies import get_db, require_api_key
from app.models.medium import Medium, MediumCreate, MediumRead, MediumUpdate
from app.models.user import User

router = APIRouter(prefix="/media-types", tags=["v2"])


@router.get("", response_model=list[MediumRead])
async def list_media_types(
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_api_key),
) -> list[Medium]:
    result = await session.execute(select(Medium).order_by(Medium.id))
    return list(result.scalars().all())


@router.get("/{medium_id}", response_model=MediumRead)
async def get_media_type(
    medium_id: int,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_api_key),
) -> Medium:
    medium = await session.get(Medium, medium_id)
    if not medium:
        raise HTTPException(status_code=404, detail="Medium not found")
    return medium


@router.post("", response_model=MediumRead, status_code=status.HTTP_201_CREATED)
async def create_media_type(
    body: MediumCreate,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_api_key),
) -> Medium:
    medium = Medium.model_validate(body)
    session.add(medium)
    await session.commit()
    await session.refresh(medium)
    return medium


@router.put("/{medium_id}", response_model=MediumRead)
async def update_media_type(
    medium_id: int,
    body: MediumUpdate,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_api_key),
) -> Medium:
    medium = await session.get(Medium, medium_id)
    if not medium:
        raise HTTPException(status_code=404, detail="Medium not found")
    medium.name = body.name
    session.add(medium)
    await session.commit()
    await session.refresh(medium)
    return medium


@router.delete("/{medium_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media_type(
    medium_id: int,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_api_key),
) -> None:
    medium = await session.get(Medium, medium_id)
    if not medium:
        raise HTTPException(status_code=404, detail="Medium not found")
    await session.delete(medium)
    await session.commit()
