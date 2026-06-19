from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.web.api_keys import get_active_api_key, regenerate_api_key

router = APIRouter(prefix="/dashboard", tags=["web"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    api_key = await get_active_api_key(session, user.id)
    new_key = request.query_params.get("new_key")
    return templates.TemplateResponse(
        request=request,
        name="student/dashboard.html",
        context={
            "user": user,
            "api_key_prefix": api_key.prefix if api_key else None,
            "has_api_key": api_key is not None,
            "new_key": new_key,
        },
    )


@router.post("/api-key")
async def create_or_regenerate_api_key(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    _, plaintext = await regenerate_api_key(session, user.id)
    return RedirectResponse(url=f"/dashboard?new_key={plaintext}", status_code=303)
