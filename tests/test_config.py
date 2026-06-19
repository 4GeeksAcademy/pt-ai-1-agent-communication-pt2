from app.config import normalize_database_url


def test_normalize_postgres_url() -> None:
    assert (
        normalize_database_url("postgres://user:pass@host/db")
        == "postgresql+asyncpg://user:pass@host/db"
    )


def test_normalize_postgresql_url() -> None:
    assert (
        normalize_database_url("postgresql://user:pass@host/db")
        == "postgresql+asyncpg://user:pass@host/db"
    )


def test_preserve_asyncpg_url() -> None:
    url = "postgresql+asyncpg://user:pass@host/db"
    assert normalize_database_url(url) == url
