from functools import lru_cache
from typing import Any
from urllib.parse import parse_qs, urlparse

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_SSL_MODES_REQUIRING_TLS = frozenset({"require", "verify-full", "verify-ca"})


def normalize_database_url(url: str) -> tuple[str, dict]:
    """Prepare a Neon-style URL for SQLAlchemy + asyncpg.

    Neon connection strings use postgres:// or postgresql:// with query params
    like channel_binding and sslmode that are meant for psycopg. asyncpg does
    not accept those kwargs, so we strip the query string and map sslmode to
    asyncpg connect_args instead.
    """
    if url.startswith("postgresql+asyncpg://"):
        parse_url = "postgresql://" + url.removeprefix("postgresql+asyncpg://")
    elif url.startswith("postgres://"):
        parse_url = "postgresql://" + url.removeprefix("postgres://")
    elif url.startswith("postgresql://"):
        parse_url = url
    else:
        return url, {}

    parsed = urlparse(parse_url)
    query = parse_qs(parsed.query)
    ssl_mode = query.get("sslmode", [""])[0]

    clean = parsed._replace(query="")
    async_url = f"postgresql+asyncpg://{clean.netloc}{clean.path}"

    connect_args: dict = {}
    if ssl_mode in _SSL_MODES_REQUIRING_TLS:
        connect_args["ssl"] = "require"

    return async_url, connect_args


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql+asyncpg://fictionary:fictionary@localhost:5432/fictionary"
    database_connect_args: dict = {}
    session_secret: str = "dev-secret-change-in-production"
    github_client_id: str = ""
    github_client_secret: str = ""
    app_url: str = "http://localhost:8000"

    @model_validator(mode="before")
    @classmethod
    def prepare_database_config(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        raw_url = data.get("database_url")
        if not raw_url:
            return data
        url, connect_args = normalize_database_url(str(raw_url))
        data["database_url"] = url
        data["database_connect_args"] = connect_args
        return data


@lru_cache
def get_settings() -> Settings:
    return Settings()
