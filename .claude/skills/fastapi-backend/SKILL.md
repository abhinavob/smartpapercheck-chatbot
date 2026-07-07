---
name: fastapi-backend
description: Builds production-grade Python backends with FastAPI, covering async endpoints, Pydantic V2 schemas, dependency injection, async SQLAlchemy, Alembic migrations, REST/API design, error handling, security, and pytest. This skill should be used whenever a user builds or modifies a backend API, server, REST endpoint, FastAPI application, request/response models, or backend business logic in Python — even if "FastAPI" is not stated explicitly.
---

# FastAPI Backend

Build backends that are async-correct, well-layered, and safe to run in production. Favor explicit structure and validation over clever shortcuts.

> **Project note (SmartPaperCheck):** this skill owns generic FastAPI conventions. For this project's concrete module layout, MVP scope, and escalation flow, defer to `project-architecture`; for the Claude chat/tool loop defer to `claude-ai-integration`; for retrieval defer to `rag-retrieval`; for email defer to `brevo-email`.

## Purpose

Provide a repeatable standard for FastAPI services so generated backends are production-ready: typed end to end, properly layered, migration-driven, secured, and tested.

## When to use

Use when creating or changing any Python backend: endpoints, routers, request/response schemas, database access, business logic, or API structure. For database modeling and query specifics, defer to the `postgresql-database` skill; for auth flows and access control, defer to the `authentication` skill; for containerizing the service, use `docker-devops`.

## Requirements

Assume this stack unless the project specifies otherwise:

- Python 3.11+, FastAPI, Pydantic V2.
- async SQLAlchemy 2.0 (`AsyncSession`) + Alembic migrations.
- uvicorn (dev) / gunicorn + uvicorn workers (prod).
- pytest + pytest-asyncio + httpx.AsyncClient for tests.
- Config via environment variables through `pydantic-settings` — never hardcoded.

Before coding, confirm: database (Postgres assumed), sync vs. async (default async), and whether an existing project layout should be matched.

## Project structure

Use a layered layout that separates transport, logic, and data:

```
app/
├── main.py          # app factory, router registration, middleware
├── core/            # config, security, settings
├── api/v1/          # routers (transport) — kept thin
├── schemas/         # Pydantic request/response models
├── models/          # SQLAlchemy ORM models
├── services/        # business logic
├── repositories/    # data access (DB queries)
└── db/              # session, engine, base
tests/   alembic/
```

Keep routers thin: validate input, call a service, shape the response. Business logic lives in `services/`; raw DB access lives in `repositories/`. This keeps logic testable without HTTP.

## Workflow

1. Define the schema first: write the Pydantic request and response models — they are the API contract and drive validation and OpenAPI docs.
2. Define/extend the ORM model and create an Alembic migration for any schema change (never hand-edit the DB).
3. Write the repository method (data access), then the service method (business logic).
4. Add the router/endpoint, wiring dependencies (DB session, current user) via `Depends`.
5. Write async tests with `httpx.AsyncClient` covering success and the main error paths.
6. Verify: run `pytest`, confirm `/docs` reflects the intended surface, and check status codes.

Checkpoint after each endpoint group: schemas validate, endpoints return expected status codes, `/docs` is accurate.

## Pydantic V2 schemas

- Separate input and output models: `UserCreate` (accepts password) vs. `UserRead` (never exposes it). Never return an ORM model that carries secrets.
- Use `model_config = ConfigDict(from_attributes=True)` on read models.
- Validate at the boundary with constrained types, `EmailStr`, and `field_validator`/`model_validator` (V2 syntax, not deprecated V1 `@validator`/`class Config`).

## Async and database

- Endpoints touching the DB or external services are `async def`. Never call blocking I/O inside an async endpoint — it stalls the event loop; offload via `await asyncio.to_thread(...)` or a background task.
- Inject the session with a dependency that yields an `AsyncSession` and closes it after the request; commit at the service boundary, roll back on error.
- Avoid N+1 queries: eager-load relationships (`selectinload`) when they will be used. (Query tuning details: see `postgresql-database`.)

## API design

- Version from day one (`/api/v1/...`).
- Use REST conventions: nouns for resources, correct verbs (GET/POST/PUT/PATCH/DELETE), correct status codes (201 create, 204 no-content, 404/409 for not-found/conflict).
- Always declare `response_model=...` so the contract and docs stay accurate.
- Paginate list endpoints (cursor/keyset preferred over large offsets).
- Make mutating endpoints idempotent where feasible (e.g. idempotency keys for create).

## Error handling

- Raise `HTTPException` with the correct status and a clear, non-leaky message (FastAPI handles 422 validation automatically).
- Register handlers so services can raise typed domain exceptions that map to responses.
- Never leak stack traces, SQL, or secrets in responses.

## Security

- Hash passwords with bcrypt/argon2; never store plaintext. (Full auth flows: see `authentication`.)
- Authenticate with OAuth2 + JWT (short-lived access + refresh), verified on every protected request via a dependency.
- Enforce authorization in the service layer, not just the router, including object-level ownership checks.
- Configure CORS explicitly (named origins, not `*` in production); rate-limit public endpoints; treat all input as hostile.
- Load secrets from the environment; keep them out of the repo and out of responses.

## Testing

- Use pytest-asyncio + httpx.AsyncClient against the app with an overridden test DB session (transactional rollback per test, or a disposable test database).
- Cover happy path, validation failure (422), auth failure (401/403), and not-found (404) per endpoint group; assert on status code and body shape.

## Anti-patterns

| Anti-pattern | Why it fails | Correct approach |
|---|---|---|
| Blocking I/O (`requests`, `time.sleep`) in `async def` | Stalls the event loop for every concurrent request | Use `httpx.AsyncClient`, or `await asyncio.to_thread(...)` for unavoidable blocking |
| Returning the ORM model directly | Leaks fields like `hashed_password`; contract drifts from docs | Return a `response_model` read schema that excludes secrets |
| Business logic inside the router | Untestable without HTTP; routers grow unmaintainable | Keep routers thin; put logic in `services/`, data access in `repositories/` |
| Hand-editing the database schema | Environments drift; no rollback path | Every schema change is a reviewed Alembic migration |
| `allow_origins=["*"]` in production | Any site can call the API with credentials | Configure CORS with an explicit named-origin allowlist |
| Authorization only at the route level | Misses object ownership (IDOR) — any user edits any record | Enforce role + object-level checks in the service layer |

## Examples

**Example 1 — input/output schema separation**
```python
class UserCreate(BaseModel):
    email: EmailStr; password: str; name: str

class UserRead(BaseModel):
    id: UUID; email: EmailStr; name: str
    model_config = ConfigDict(from_attributes=True)

@router.post("/users", response_model=UserRead, status_code=201)
async def create_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    return await user_service.create(db, payload)
```
Rationale: the password is accepted but never returned; the contract is explicit and reflected in `/docs`.

**Example 2 — blocking call anti-pattern**
Calling `requests.get()` or `time.sleep()` inside an `async def` endpoint blocks the event loop for all requests. Fix: use `httpx.AsyncClient` for async I/O, or `await asyncio.to_thread(...)` for unavoidable blocking work.

## Definition of Done

- [ ] Input and output schemas are separate; no secrets in responses.
- [ ] Every DB/external call is `async`; no blocking I/O in the event loop.
- [ ] Routers are thin; logic in services, data access in repositories.
- [ ] Schema changes ship as reviewed Alembic migrations.
- [ ] `response_model` declared; status codes correct; list endpoints paginated.
- [ ] Authorization enforced in the service layer (role + object-level).
- [ ] Tests cover 2xx, 422, 401/403, 404; `pytest` passes and `/docs` is accurate.

## Sources adapted and merged

- `wshobson/agents` → `api-scaffolding/skills/fastapi-templates` — https://github.com/wshobson/agents (layered structure, async session + test fixtures, references/assets pattern).
- `Jeffallan/claude-skills` → FastAPI Expert — https://github.com/Jeffallan/claude-skills (Pydantic V2, async SQLAlchemy, JWT, /docs verification).
- `Ashfaqbs/software-dev-ai-claude-toolkit` — https://github.com/Ashfaqbs/software-dev-ai-claude-toolkit (python/FastAPI standards). Note: Anthropic's official repo has no backend skill; content is community-sourced plus FastAPI/Starlette best practice.
