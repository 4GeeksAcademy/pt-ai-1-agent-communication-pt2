# Fictionary Decisions

Architectural and product decisions in ADR (Architecture Decision Record) format. New entries are appended; superseded decisions are marked but not deleted.

---

## ADR-001: URL path versioning (`/api/v1`, `/api/v2`)

**Status:** Accepted

**Context:** Students need to experience API evolution without breaking early assignments.

**Decision:** Version the API in the URL path. v1 and v2 are separate FastAPI routers. v1 remains available indefinitely after v2 ships.

**Consequences:**
- Assignments can target a stable v1 surface while advanced work moves to v2
- Some endpoint duplication between routers is expected and acceptable
- OpenAPI docs show both versions side by side

---

## ADR-002: v1 is unauthenticated

**Status:** Accepted

**Context:** The first student assignment should require no account setup, OAuth flow, or API key management.

**Decision:** The v1 router has no auth middleware or dependencies. All v1 endpoints are publicly accessible.

**Consequences:**
- Students can start with curl alone on day one
- v1 is not suitable for sensitive data (acceptable — catalog content is fictional and public)
- v2 must be used for any authenticated or relationship-heavy work

---

## ADR-003: API keys for v2 programmatic access

**Status:** Accepted

**Context:** v2 requires authentication. Students need a simple, copy-paste credential for scripts and Postman.

**Decision:** Issue per-user API keys via the student dashboard. Keys are sent in the `X-API-Key` header. Only a SHA-256 hash is stored in the database.

**Alternatives considered:**
- OAuth tokens for API access — rejected; too complex for introductory REST exercises
- JWT sessions shared between web and API — rejected; blurs the browser vs programmatic distinction

**Consequences:**
- Clear teaching moment: browser auth (cookies) vs API auth (headers) are separate mechanisms
- Key regeneration revokes the previous key (one active key per user)
- Plaintext key is shown once at creation; students must copy it immediately

---

## ADR-004: GitHub OAuth for web sign-in

**Status:** Accepted

**Context:** Students and instructors need accounts for the dashboard and admin panel. Password management is out of scope.

**Decision:** Use GitHub OAuth as the sole sign-in method for the web UI.

**Alternatives considered:**
- Email/password — rejected; adds credential storage, reset flows, and security burden
- No auth on web UI — rejected; API key management requires identity

**Consequences:**
- Students need a GitHub account (acceptable for CS courses)
- No password hashing or email verification to build or maintain
- `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` required in all environments

---

## ADR-005: Admin role set manually, not self-service

**Status:** Accepted

**Context:** The admin panel must be restricted to instructors. There is no registration flow.

**Decision:** `User.is_admin` is a boolean column defaulting to `false`. Admins are promoted via seed script or direct database update. The admin panel returns 403 for non-admin users.

**Consequences:**
- No role-management UI needed for v1 of the project
- Instructors must be seeded before the first admin panel use
- Students who sign in via GitHub get `is_admin=false` automatically

---

## ADR-006: Jinja2 server-rendered UI (no SPA)

**Status:** Accepted

**Context:** The project needs a student dashboard and admin panel. A separate frontend adds build tooling and deployment complexity.

**Decision:** Render all web pages as Jinja2 templates inside the FastAPI app. No React, Vue, or separate frontend build step.

**Alternatives considered:**
- React SPA on Vercel — rejected; two deployments, CORS, and auth cookie complexity for minimal UI needs
- HTMX — acceptable future enhancement; start with plain forms

**Consequences:**
- Single repo, single deployment artifact
- Admin CRUD is HTML forms, not a JSON admin API
- UI will be functional, not polished — appropriate for an API-teaching project

---

## ADR-007: FastAPI on Vercel with Neon PostgreSQL

**Status:** Accepted

**Context:** Production hosting should be free-tier friendly and familiar to students deploying class projects.

**Decision:** Deploy the FastAPI app as Vercel Python serverless functions. Use Neon for managed PostgreSQL in production.

**Alternatives considered:**
- Docker on Railway/Fly.io — viable fallback if Vercel serverless constraints become blocking
- SQLite — rejected; not suitable for multi-user classroom deployment

**Consequences:**
- Must use async database access and serverless-safe connection handling (Neon serverless driver or short-lived connections)
- Cold starts possible on Vercel; acceptable for a teaching API
- `vercel.json` required to route requests to the FastAPI entry point
- Local dev uses Docker Compose with a standard Postgres container instead of Neon

---

## ADR-008: Docker Compose for local development only

**Status:** Accepted

**Context:** Students and contributors need a one-command local setup without cloud accounts.

**Decision:** `docker compose up` runs the app and a local Postgres 16 container. Production uses Vercel + Neon and does not rely on Docker.

**Consequences:**
- `.env.example` documents all required variables for local use
- Local and production databases are separate; schema kept in sync via Alembic migrations
- Contributors without a Neon account can develop fully offline

---

## ADR-009: SQLModel as the ORM

**Status:** Accepted

**Context:** The project needs database models that also serve as Pydantic request/response schemas.

**Decision:** Use SQLModel for table definitions. Create separate `*Create`, `*Update`, and `*Read` schema classes where shapes diverge.

**Alternatives considered:**
- Raw SQLAlchemy + separate Pydantic models — more boilerplate for a small project
- Tortoise ORM — less ecosystem alignment with FastAPI docs students will read

**Consequences:**
- Shared typing between DB and API layers reduces duplication
- Must still define explicit read schemas to avoid leaking internal fields (e.g., `key_hash`)

---

## ADR-010: PUT for updates, no PATCH

**Status:** Accepted

**Context:** Students are learning REST fundamentals. Supporting both PUT and PATCH adds confusion about partial vs full updates.

**Decision:** All update endpoints use `PUT` with a complete resource body. `PATCH` is not implemented.

**Consequences:**
- Assignments can say "send the full object" without explaining partial update semantics
- Clients must read-then-write for edits (good practice for beginners)
- v1 and v2 update behavior is consistent

---

## ADR-011: Admin CRUD via web UI only (no admin API)

**Status:** Accepted

**Context:** Instructors need to manage catalog data. A separate admin API would expand the surface students must learn.

**Decision:** All admin data management happens through Jinja2 form pages under `/admin`. There is no `/api/admin/...` router.

**Consequences:**
- Students interact only with `/api/v1` and `/api/v2` — the documented learning surface
- Admin operations are not testable via the same Postman collection students use
- Simpler auth model: admin panel uses session cookies, API uses API keys

---

## ADR-012: Flat v1 MediaItem, relationships in v2 only

**Status:** Accepted

**Context:** v1 is the introductory assignment surface. Related resources (`Creator`, `Genre`, etc.) add complexity.

**Decision:** v1 `MediaItem` responses contain only scalar fields (`title`, `description`, `release_year`). Foreign keys and nested objects appear in v2 only.

**Consequences:**
- v1 assignments stay focused on HTTP verbs and JSON
- v2 introduces foreign keys, association endpoints, and join concepts as a second unit
- The same `media_items` table backs both versions; v1 serializers simply omit relationship fields

---

## ADR-013: No rate limiting or usage metering

**Status:** Accepted

**Context:** This is a classroom teaching tool, not a production SaaS.

**Decision:** Do not implement rate limiting, quotas, or usage dashboards in the initial build.

**Consequences:**
- Simpler deployment and fewer moving parts
- Instructors should reset or reseed data between course runs if needed
- Can be revisited if the API is ever exposed beyond a controlled classroom
