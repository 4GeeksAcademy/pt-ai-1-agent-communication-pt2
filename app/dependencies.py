import hashlib
from collections.abc import AsyncGenerator
from datetime import datetime, timezone

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import get_session
from app.models.api_key import ApiKey
from app.models.user import User


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session():
        yield session


def get_session_user(request: Request) -> dict | None:
    return request.session.get("user")


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_db),
) -> User:
    session_user = get_session_user(request)
    if not session_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    result = await session.execute(select(User).where(User.id == session_user["id"]))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


async def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


async def require_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    session: AsyncSession = Depends(get_db),
) -> User:
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing API key")

    key_hash = hashlib.sha256(x_api_key.encode()).hexdigest()
    result = await session.execute(
        select(ApiKey).where(ApiKey.key_hash == key_hash, ApiKey.revoked_at.is_(None))
    )
    api_key = result.scalar_one_or_none()
    if not api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    user_result = await session.execute(select(User).where(User.id == api_key.user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return user


def hash_api_key(plaintext_key: str) -> str:
    return hashlib.sha256(plaintext_key.encode()).hexdigest()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
