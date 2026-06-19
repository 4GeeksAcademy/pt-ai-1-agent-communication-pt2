from app.config import Settings, normalize_database_url


def test_normalize_postgres_url() -> None:
    url, connect_args = normalize_database_url("postgres://user:pass@host/db")
    assert url == "postgresql+asyncpg://user:pass@host/db"
    assert connect_args == {}


def test_normalize_postgresql_url() -> None:
    url, connect_args = normalize_database_url("postgresql://user:pass@host/db")
    assert url == "postgresql+asyncpg://user:pass@host/db"
    assert connect_args == {}


def test_preserve_asyncpg_url() -> None:
    raw = "postgresql+asyncpg://user:pass@host/db"
    url, connect_args = normalize_database_url(raw)
    assert url == raw
    assert connect_args == {}


def test_strip_neon_query_params_and_enable_ssl() -> None:
    raw = (
        "postgresql://user:pass@ep-example.neon.tech/neondb"
        "?channel_binding=require&sslmode=require"
    )
    url, connect_args = normalize_database_url(raw)
    assert url == "postgresql+asyncpg://user:pass@ep-example.neon.tech/neondb"
    assert connect_args == {"ssl": "require"}


def test_settings_apply_neon_connect_args() -> None:
    settings = Settings(
        database_url=(
            "postgresql://user:pass@ep-example.neon.tech/neondb"
            "?channel_binding=require&sslmode=require"
        )
    )
    assert settings.database_url == "postgresql+asyncpg://user:pass@ep-example.neon.tech/neondb"
    assert settings.database_connect_args == {"ssl": "require"}
