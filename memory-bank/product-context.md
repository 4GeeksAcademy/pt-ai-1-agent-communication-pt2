# Fictionary API

## Overview

Fictionary API is a REST API for students learning how to interact with HTTP APIs. It exposes a catalog of fictional media — books, films, TV shows, and similar works — through progressively richer API versions so students can start with basic CRUD and grow into authentication, relationships, and error handling.

The project also includes a small web UI: a student dashboard for obtaining API keys and an admin panel for managing catalog data.

## Learning Goals

Students using Fictionary should practice:

- Making REST requests with curl, Postman, or a client library (GET, POST, PUT/PATCH, DELETE)
- Reading auto-generated OpenAPI docs and interpreting status codes and error responses
- Understanding API versioning (`/api/v1` vs `/api/v2`) and why behavior changes between versions
- Authenticating programmatic requests with an API key header
- Working with related resources (linking creators, genres, and other metadata to a media item)

## User Roles

### Student (normal user)

- Signs in via GitHub OAuth on the web UI
- Views a personal dashboard showing their account and issued API key
- Uses the API key to call v2 endpoints from scripts, assignments, or API clients
- Does not need access to the admin panel

### Admin (instructor or operator)

- Signs in via GitHub OAuth (accounts flagged as admin in the database)
- Uses the admin panel to create, edit, and delete catalog data
- Manages seed content and corrects bad data during a course run
- Can perform the same operations students can, plus full data management via the UI

## Domain Model

Fictionary tracks fictional media and the metadata that describes it.

| Model | Description | Example |
|-------|-------------|---------|
| `MediaItem` | A specific fictional work | *The Fellowship of the Ring* |
| `Creator` | A person or organization that made a work | J.R.R. Tolkien |
| `Franchise` | A series or shared fictional universe | *The Lord of the Rings* |
| `Medium` | The format or type of a work | novel, film, TV series, video game |
| `Genre` | A descriptive category | fantasy, science fiction, horror |

### Relationships (v2)

- A `MediaItem` belongs to one `Franchise` (optional) and one `Medium`
- A `MediaItem` can have many `Genre` tags
- A `MediaItem` can have many `Creator` associations (e.g., author, director)
- `Creator`, `Franchise`, `Medium`, and `Genre` are shared lookup resources managed by admins and referenced by students when enriching media items

## API Versions

### v1 — `/api/v1`

Intentionally simple. No authentication required.

Students learn core REST patterns against a single resource:

| Method | Endpoint | Action |
|--------|----------|--------|
| GET | `/api/v1/media-items` | List all media items |
| GET | `/api/v1/media-items/{id}` | Retrieve one media item |
| POST | `/api/v1/media-items` | Create a media item |
| PUT | `/api/v1/media-items/{id}` | Replace a media item |
| DELETE | `/api/v1/media-items/{id}` | Delete a media item |

v1 `MediaItem` fields are flat (title, description, release year, etc.) with no related-resource links. v1 remains available after v2 ships so assignments can scaffold gradually.

### v2 — `/api/v2`

Requires a valid API key (issued from the student dashboard). Builds on v1 with relationships and additional resources.

Additional capabilities:

- CRUD on `Creator`, `Franchise`, `Medium`, and `Genre`
- Associate creators and genres with a media item
- Set franchise and medium on a media item
- Stricter validation and more detailed error responses

Authentication: students pass their API key in the `X-API-Key` request header.

## Web UI

### Student dashboard

- GitHub OAuth sign-in
- Display account info (name, GitHub username)
- Show or regenerate a personal API key for v2 access
- Link to the interactive API docs at `/docs`

### Admin panel

- GitHub OAuth sign-in (admin accounts only)
- CRUD interface for all catalog models
- Intended for instructors, not students — keeps the public API surface clean while allowing data maintenance

## Core Features

- **v1 API** — unauthenticated CRUD on `MediaItem`
- **v2 API** — authenticated CRUD on all models plus relationship management
- **Interactive docs** — FastAPI auto-generated Swagger UI at `/docs`
- **Student dashboard** — sign-in and API key management
- **Admin panel** — web-based data editing for operators

## Non-Goals

The following are out of scope for the initial build:

- File uploads (cover art, attachments)
- Full-text search or filtering beyond basic list endpoints
- Rate limiting, billing, or usage metering
- OAuth for API access (API keys only for programmatic v2 calls)
- Public user registration beyond GitHub OAuth
- Mobile apps or native clients

## Success Criteria

The project is ready for classroom use when:

1. A student can complete a v1 assignment using only curl or Postman (no account needed)
2. A student can sign in, copy an API key, and call a v2 relationship endpoint
3. An admin can seed and edit catalog data through the admin panel without touching the database directly
4. Local development runs with a single `docker compose up` command
