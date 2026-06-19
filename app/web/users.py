from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.user import User


async def get_bootstrap_admin_id(session: AsyncSession) -> int | None:
    """The first registered user — auto-promoted on sign-up and cannot be demoted."""
    result = await session.execute(select(func.min(User.id)))
    return result.scalar_one_or_none()


async def list_users(session: AsyncSession) -> list[User]:
    result = await session.execute(select(User).order_by(User.id))
    return list(result.scalars().all())
