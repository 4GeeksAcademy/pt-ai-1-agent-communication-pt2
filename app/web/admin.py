from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.dependencies import get_db, require_admin
from app.models.creator import Creator
from app.models.franchise import Franchise
from app.models.genre import Genre
from app.models.media_item import MediaItem
from app.models.medium import Medium
from app.models.user import User
from app.web.api_keys import get_active_api_key, regenerate_api_key
from app.web.users import get_bootstrap_admin_id, list_users

router = APIRouter(prefix="/admin", tags=["web"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def admin_home(
    request: Request,
    user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    media_items = list((await session.execute(select(MediaItem).order_by(MediaItem.id))).scalars().all())
    creators = list((await session.execute(select(Creator).order_by(Creator.id))).scalars().all())
    franchises = list((await session.execute(select(Franchise).order_by(Franchise.id))).scalars().all())
    media_types = list((await session.execute(select(Medium).order_by(Medium.id))).scalars().all())
    genres = list((await session.execute(select(Genre).order_by(Genre.id))).scalars().all())
    users = await list_users(session)
    bootstrap_admin_id = await get_bootstrap_admin_id(session)
    api_key = await get_active_api_key(session, user.id)
    message = request.query_params.get("message")
    new_key = request.query_params.get("new_key")
    return templates.TemplateResponse(
        request=request,
        name="admin/index.html",
        context={
            "user": user,
            "media_items": media_items,
            "creators": creators,
            "franchises": franchises,
            "media_types": media_types,
            "genres": genres,
            "users": users,
            "bootstrap_admin_id": bootstrap_admin_id,
            "api_key_prefix": api_key.prefix if api_key else None,
            "has_api_key": api_key is not None,
            "new_key": new_key,
            "message": message,
        },
    )


@router.post("/media-items")
async def create_media_item(
    title: str = Form(...),
    description: str = Form(""),
    release_year: int | None = Form(None),
    franchise_id: int | None = Form(None),
    medium_id: int | None = Form(None),
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    media_item = MediaItem(
        title=title,
        description=description or None,
        release_year=release_year,
        franchise_id=franchise_id,
        medium_id=medium_id,
    )
    session.add(media_item)
    await session.commit()
    return RedirectResponse(url="/admin?message=Media+item+created", status_code=303)


@router.post("/media-items/{media_item_id}/delete")
async def delete_media_item(
    media_item_id: int,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    media_item = await session.get(MediaItem, media_item_id)
    if media_item:
        await session.delete(media_item)
        await session.commit()
    return RedirectResponse(url="/admin?message=Media+item+deleted", status_code=303)


@router.post("/creators")
async def create_creator(
    name: str = Form(...),
    bio: str = Form(""),
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    session.add(Creator(name=name, bio=bio or None))
    await session.commit()
    return RedirectResponse(url="/admin?message=Creator+created", status_code=303)


@router.post("/creators/{creator_id}/delete")
async def delete_creator(
    creator_id: int,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    creator = await session.get(Creator, creator_id)
    if creator:
        await session.delete(creator)
        await session.commit()
    return RedirectResponse(url="/admin?message=Creator+deleted", status_code=303)


@router.post("/franchises")
async def create_franchise(
    name: str = Form(...),
    description: str = Form(""),
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    session.add(Franchise(name=name, description=description or None))
    await session.commit()
    return RedirectResponse(url="/admin?message=Franchise+created", status_code=303)


@router.post("/franchises/{franchise_id}/delete")
async def delete_franchise(
    franchise_id: int,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    franchise = await session.get(Franchise, franchise_id)
    if franchise:
        await session.delete(franchise)
        await session.commit()
    return RedirectResponse(url="/admin?message=Franchise+deleted", status_code=303)


@router.post("/media-types")
async def create_media_type(
    name: str = Form(...),
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    session.add(Medium(name=name))
    await session.commit()
    return RedirectResponse(url="/admin?message=Media+type+created", status_code=303)


@router.post("/media-types/{medium_id}/delete")
async def delete_media_type(
    medium_id: int,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    medium = await session.get(Medium, medium_id)
    if medium:
        await session.delete(medium)
        await session.commit()
    return RedirectResponse(url="/admin?message=Media+type+deleted", status_code=303)


@router.post("/genres")
async def create_genre(
    name: str = Form(...),
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    session.add(Genre(name=name))
    await session.commit()
    return RedirectResponse(url="/admin?message=Genre+created", status_code=303)


@router.post("/genres/{genre_id}/delete")
async def delete_genre(
    genre_id: int,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    genre = await session.get(Genre, genre_id)
    if genre:
        await session.delete(genre)
        await session.commit()
    return RedirectResponse(url="/admin?message=Genre+deleted", status_code=303)


@router.post("/users/{user_id}/promote")
async def promote_user(
    user_id: int,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    target = await session.get(User, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.is_admin:
        return RedirectResponse(url="/admin?message=User+is+already+an+admin", status_code=303)

    target.is_admin = True
    session.add(target)
    await session.commit()
    return RedirectResponse(
        url=f"/admin?message={target.username}+promoted+to+admin",
        status_code=303,
    )


@router.post("/users/{user_id}/demote")
async def demote_user(
    user_id: int,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    target = await session.get(User, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    bootstrap_admin_id = await get_bootstrap_admin_id(session)
    if target.id == bootstrap_admin_id:
        return RedirectResponse(
            url="/admin?message=Cannot+remove+the+first+admin",
            status_code=303,
        )
    if not target.is_admin:
        return RedirectResponse(url="/admin?message=User+is+not+an+admin", status_code=303)

    target.is_admin = False
    session.add(target)
    await session.commit()
    return RedirectResponse(
        url=f"/admin?message={target.username}+removed+from+admins",
        status_code=303,
    )


@router.post("/api-key")
async def create_or_regenerate_api_key(
    user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    _, plaintext = await regenerate_api_key(session, user.id)
    return RedirectResponse(url=f"/admin?new_key={plaintext}", status_code=303)
