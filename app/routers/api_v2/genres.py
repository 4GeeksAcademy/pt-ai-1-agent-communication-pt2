from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.dependencies import get_db, require_api_key
from app.models.genre import Genre, GenreCreate, GenreRead, GenreUpdate
from app.models.user import User

router = APIRouter(prefix="/genres", tags=["v2"])


@router.get("", response_model=list[GenreRead])
async def list_genres(
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_api_key),
) -> list[Genre]:
    result = await session.execute(select(Genre).order_by(Genre.id))
    return list(result.scalars().all())


@router.get("/{genre_id}", response_model=GenreRead)
async def get_genre(
    genre_id: int,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_api_key),
) -> Genre:
    genre = await session.get(Genre, genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    return genre


@router.post("", response_model=GenreRead, status_code=status.HTTP_201_CREATED)
async def create_genre(
    body: GenreCreate,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_api_key),
) -> Genre:
    genre = Genre.model_validate(body)
    session.add(genre)
    await session.commit()
    await session.refresh(genre)
    return genre


@router.put("/{genre_id}", response_model=GenreRead)
async def update_genre(
    genre_id: int,
    body: GenreUpdate,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_api_key),
) -> Genre:
    genre = await session.get(Genre, genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    genre.name = body.name
    session.add(genre)
    await session.commit()
    await session.refresh(genre)
    return genre


@router.delete("/{genre_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_genre(
    genre_id: int,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_api_key),
) -> None:
    genre = await session.get(Genre, genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    await session.delete(genre)
    await session.commit()
