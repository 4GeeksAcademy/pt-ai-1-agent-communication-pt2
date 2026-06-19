import secrets
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.dependencies import hash_api_key
from app.models.api_key import ApiKey


async def get_active_api_key(session: AsyncSession, user_id: int) -> ApiKey | None:
    result = await session.execute(
        select(ApiKey).where(ApiKey.user_id == user_id, ApiKey.revoked_at.is_(None))
    )
    return result.scalar_one_or_none()


async def regenerate_api_key(session: AsyncSession, user_id: int) -> tuple[ApiKey, str]:
    now = datetime.now(timezone.utc)
    result = await session.execute(
        select(ApiKey).where(ApiKey.user_id == user_id, ApiKey.revoked_at.is_(None))
    )
    for existing in result.scalars().all():
        existing.revoked_at = now
        session.add(existing)

    plaintext = secrets.token_urlsafe(32)
    api_key = ApiKey(
        user_id=user_id,
        key_hash=hash_api_key(plaintext),
        prefix=plaintext[:8],
    )
    session.add(api_key)
    await session.commit()
    await session.refresh(api_key)
    return api_key, plaintext
