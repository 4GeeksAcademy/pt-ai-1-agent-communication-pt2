from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql+asyncpg://fictionary:fictionary@localhost:5432/fictionary"
    session_secret: str = "dev-secret-change-in-production"
    github_client_id: str = ""
    github_client_secret: str = ""
    app_url: str = "http://localhost:8000"


@lru_cache
def get_settings() -> Settings:
    return Settings()
