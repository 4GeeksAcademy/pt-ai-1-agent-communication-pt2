# Fictionary Conventions

Coding and API standards for the Fictionary project. Follow these consistently so student exercises, generated docs, and agent-assisted changes all behave predictably.

## Python

- **Python version:** 3.12+
- **Package manager:** dependencies declared in `pyproject.toml`
- **Formatting:** follow PEP 8; use type hints on all function signatures
- **Imports:** stdlib → third-party → local, separated by blank lines
- **Async:** use `async def` for route handlers and database operations throughout
- **Settings:** load config via a `Settings` class in `app/config.py` (pydantic-settings); never read `os.environ` directly in route handlers

## Naming

| Context | Convention | Example |
|---------|------------|---------|
| Python modules | snake_case | `media_item.py` |
| Python classes | PascalCase | `MediaItem`, `MediaItemCreate` |
| Python functions/vars | snake_case | `get_media_item`, `release_year` |
| DB tables | snake_case, plural | `media_items`, `media_item_genres` |
| URL paths | kebab-case, plural nouns | `/media-items`, `/api/v2/creators` |
| JSON fields | snake_case | `release_year`, `franchise_id` |
| Environment variables | SCREAMING_SNAKE_CASE | `DATABASE_URL` |

### SQLModel schema naming

Use separate schema classes per purpose:

- `MediaItem` — table model (inherits `table=True`)
- `MediaItemCreate` — POST request body
- `MediaItemUpdate` — PUT request body
- `MediaItemRead` — response shape (used in `response_model`)

Do not expose table models directly as `response_model`.

## API Design

### Versioning

- Version in the URL path: `/api/v1/...`, `/api/v2/...`
- Never break v1 behavior once published; add new behavior in v2
- Tag routers in OpenAPI with version labels (`v1`, `v2`)

### HTTP methods

| Method | Use for |
|--------|---------|
| GET | Read one or many resources |
| POST | Create a resource or add a relationship |
| PUT | Full replacement of a resource |
| DELETE | Remove a resource or unlink a relationship |

Use `PUT` (not `PATCH`) for updates. Request bodies must include all required fields; omitted optional fields are set to `null` or default.

Do not use `PATCH` anywhere — keeps assignments simple and responses predictable for students.

### URL patterns

```
GET    /api/v2/media-items              # list
GET    /api/v2/media-items/{id}         # retrieve
POST   /api/v2/media-items              # create
PUT    /api/v2/media-items/{id}        # replace
DELETE /api/v2/media-items/{id}        # delete

POST   /api/v2/media-items/{id}/creators        # link (body: { "creator_id": 1 })
DELETE /api/v2/media-items/{id}/creators/{creator_id}  # unlink
POST   /api/v2/media-items/{id}/genres          # link (body: { "genre_id": 3 })
DELETE /api/v2/media-items/{id}/genres/{genre_id}      # unlink
```

- Collection paths are plural kebab-case nouns
- Resource IDs are integers in the path
- Relationship actions are sub-paths under the parent resource, not separate top-level routes

### Request and response format

- Content type: `application/json` for all API request and response bodies
- Return the resource directly — no wrapper envelope:

```json
{
  "id": 1,
  "title": "The Fellowship of the Ring",
  "description": "...",
  "release_year": 1954
}
```

- List endpoints return a JSON array at the top level:

```json
[
  { "id": 1, "title": "..." },
  { "id": 2, "title": "..." }
]
```

- Do not wrap responses in `{ "data": ... }` — students should see standard REST shapes

### Error responses

Use FastAPI's default `HTTPException` format:

```json
{
  "detail": "Media item not found"
}
```

Validation errors (422) use FastAPI's default array format — do not customize:

```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Status codes

| Code | When |
|------|------|
| 200 | Successful GET, PUT |
| 201 | Successful POST (create or link) |
| 204 | Successful DELETE with no response body |
| 400 | Malformed request or invalid relationship (e.g., duplicate link) |
| 401 | Missing or invalid API key (v2 only) |
| 403 | Authenticated but not authorized (admin panel) |
| 404 | Resource not found |
| 422 | Request body or params failed validation |

### Authentication headers

- v2 API key: `X-API-Key: <plaintext-key>`
- No `Authorization: Bearer` header — keep auth simple and explicit for teaching
- v1 endpoints ignore auth headers entirely (no error if present)

## Database

- **Primary keys:** auto-incrementing integers (`id`)
- **Timestamps:** `created_at` (UTC, set on insert) on `User` and `ApiKey`; omit from catalog models unless needed later
- **Foreign keys:** `{model}_id` suffix (`franchise_id`, `medium_id`)
- **Association tables:** `{parent}_{related}` plural (`media_item_creators`, `media_item_genres`)
- **Migrations:** all schema changes go through Alembic; never modify production tables by hand
- **Seeding:** provide a seed script (`scripts/seed.py`) for local dev and demo data; keep seed data fictional and clearly labeled

## Web UI (Jinja2)

- Templates live under `app/templates/`
- Extend `base.html` for all pages
- Use minimal inline CSS or a single static stylesheet — no frontend build toolchain
- Form submissions use standard HTML `POST`; handle with FastAPI form endpoints or HTMX only if needed
- Flash messages for success/error feedback after admin actions
- Route prefixes: `/dashboard` (student), `/admin` (admin), `/auth` (OAuth)

## Project Layout Rules

- One model per file in `app/models/`
- One router module per resource group in `app/routers/api_v1/` and `app/routers/api_v2/`
- Shared dependencies (DB session, auth) in `app/dependencies.py` — do not duplicate dependency logic in routers
- Business logic stays in router handlers or small service functions colocated with the router; no heavy service-layer abstraction unless a handler exceeds ~40 lines

## Testing

- **Framework:** pytest + httpx `AsyncClient`
- **Test location:** `tests/` mirroring `app/` structure
- **Naming:** `test_<action>_<scenario>.py` or `test_<resource>.py` with descriptive function names (`test_create_media_item_returns_201`)
- **Database:** use a separate test database or transaction rollback per test; never run tests against production Neon
- **Coverage priorities:** v1 CRUD happy paths, v2 auth rejection (401), relationship link/unlink, admin 403 for non-admin users

## Git

- **Branch naming:** `feat/...`, `fix/...`, `chore/...`
- **Commits:** imperative mood, concise subject (`add v1 media-items router`, not `added` or `adding`)
- **PR size:** prefer small, reviewable PRs aligned to a single resource or feature

## Documentation

- Docstrings on public router endpoints are optional — OpenAPI metadata (`summary`, `description`) is preferred since students use `/docs`
- Keep `memory-bank/` updated when making architectural or behavioral changes
- Record non-obvious choices in `decisions.md`, not inline in code comments
