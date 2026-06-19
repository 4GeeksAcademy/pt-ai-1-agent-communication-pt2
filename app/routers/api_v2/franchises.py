from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.dependencies import get_db, require_api_key
from app.models.franchise import Franchise, FranchiseCreate, FranchiseRead, FranchiseUpdate
from app.models.user import User

router = APIRouter(prefix="/franchises", tags=["v2"])


@router.get("", response_model=list[FranchiseRead])
async def list_franchises(
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_api_key),
) -> list[Franchise]:
    result = await session.execute(select(Franchise).order_by(Franchise.id))
    return list(result.scalars().all())


@router.get("/{franchise_id}", response_model=FranchiseRead)
async def get_franchise(
    franchise_id: int,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_api_key),
) -> Franchise:
    franchise = await session.get(Franchise, franchise_id)
    if not franchise:
        raise HTTPException(status_code=404, detail="Franchise not found")
    return franchise


@router.post("", response_model=FranchiseRead, status_code=status.HTTP_201_CREATED)
async def create_franchise(
    body: FranchiseCreate,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_api_key),
) -> Franchise:
    franchise = Franchise.model_validate(body)
    session.add(franchise)
    await session.commit()
    await session.refresh(franchise)
    return franchise


@router.put("/{franchise_id}", response_model=FranchiseRead)
async def update_franchise(
    franchise_id: int,
    body: FranchiseUpdate,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_api_key),
) -> Franchise:
    franchise = await session.get(Franchise, franchise_id)
    if not franchise:
        raise HTTPException(status_code=404, detail="Franchise not found")
    franchise.name = body.name
    franchise.description = body.description
    session.add(franchise)
    await session.commit()
    await session.refresh(franchise)
    return franchise


@router.delete("/{franchise_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_franchise(
    franchise_id: int,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_api_key),
) -> None:
    franchise = await session.get(Franchise, franchise_id)
    if not franchise:
        raise HTTPException(status_code=404, detail="Franchise not found")
    await session.delete(franchise)
    await session.commit()
