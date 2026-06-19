from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlmodel import select

from app.config import get_settings
from app.dependencies import get_db
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["web"])

oauth = OAuth()
oauth.register(
    name="github",
    client_id=get_settings().github_client_id,
    client_secret=get_settings().github_client_secret,
    access_token_url="https://github.com/login/oauth/access_token",
    authorize_url="https://github.com/login/oauth/authorize",
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "read:user user:email"},
)


@router.get("/login")
async def login(request: Request) -> RedirectResponse:
    settings = get_settings()
    if not settings.github_client_id or not settings.github_client_secret:
        raise HTTPException(
            status_code=503,
            detail="GitHub OAuth is not configured. Set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET.",
        )
    redirect_uri = f"{settings.app_url}/auth/callback"
    return await oauth.github.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def callback(
    request: Request,
    session: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    token = await oauth.github.authorize_access_token(request)
    response = await oauth.github.get("user", token=token)
    profile = response.json()

    github_id = profile["id"]
    username = profile["login"]
    display_name = profile.get("name") or username

    result = await session.execute(select(User).where(User.github_id == github_id))
    user = result.scalar_one_or_none()
    if not user:
        count_result = await session.execute(select(func.count()).select_from(User))
        is_first_user = count_result.scalar_one() == 0
        user = User(
            github_id=github_id,
            username=username,
            display_name=display_name,
            is_admin=is_first_user,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    else:
        user.username = username
        user.display_name = display_name
        session.add(user)
        await session.commit()

    request.session["user"] = {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "is_admin": user.is_admin,
    }

    if user.is_admin:
        return RedirectResponse(url="/admin", status_code=302)
    return RedirectResponse(url="/dashboard", status_code=302)


@router.get("/logout")
async def logout(request: Request) -> RedirectResponse:
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)
