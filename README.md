# Fictionary API

A REST API for students learning HTTP and API interaction. See `memory-bank/` for full product and architecture docs.

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

The API is available at [http://localhost:8000](http://localhost:8000).

- **Home:** `/`
- **API docs:** `/docs`
- **v1 API:** `/api/v1/media-items` (no auth)
- **v2 API:** `/api/v2/...` (requires `X-API-Key` header)
- **Student dashboard:** `/dashboard` (GitHub OAuth)
- **Admin panel:** `/admin` (GitHub OAuth, admin users only)

## Seed demo data

```bash
docker compose exec app python scripts/seed.py
```

## Run tests

```bash
pip install -e ".[dev]"
pytest
```

Tests expect a running Postgres instance (use `docker compose up db` or full stack).

## Environment variables

Copy `.env.example` to `.env` and fill in GitHub OAuth credentials for web sign-in:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string (`postgresql+asyncpg://...`) |
| `SESSION_SECRET` | Secret for signing session cookies |
| `GITHUB_CLIENT_ID` | GitHub OAuth app client ID |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth app client secret |
| `APP_URL` | Public base URL (e.g. `http://localhost:8000`) |
