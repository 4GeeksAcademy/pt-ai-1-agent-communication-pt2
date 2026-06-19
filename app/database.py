from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from sqlalchemy.pool import NullPool

from app.config import get_settings

import app.models  # noqa: F401 — register tables with SQLModel metadata

_settings = get_settings()
_engine_kwargs: dict = {
    "echo": False,
    "connect_args": _settings.database_connect_args,
    "pool_pre_ping": True,
}
if _settings.database_connect_args:
    # Serverless: avoid holding connections across invocations
    _engine_kwargs["poolclass"] = NullPool

engine = create_async_engine(_settings.database_url, **_engine_kwargs)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
