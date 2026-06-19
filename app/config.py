from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_database_url(url: str) -> str:
    """Ensure async SQLAlchemy uses asyncpg, not psycopg.

    Neon and other hosts often provide postgres:// or postgresql:// URLs.
    Without the +asyncpg driver, SQLAlchemy looks for psycopg instead.
    """
    if url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url.removeprefix("postgres://")
    if url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url.removeprefix("postgresql://")
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql+asyncpg://fictionary:fictionary@localhost:5432/fictionary"
    session_secret: str = "dev-secret-change-in-production"
    github_client_id: str = ""
    github_client_secret: str = ""
    app_url: str = "http://localhost:8000"

    @field_validator("database_url", mode="before")
    @classmethod
    def ensure_asyncpg_driver(cls, value: str) -> str:
        return normalize_database_url(value)


@lru_cache
def get_settings() -> Settings:
    return Settings()
