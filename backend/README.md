# SmartPaperCheck Chatbot — Backend

FastAPI service that answers product questions about SmartPaperCheck and escalates to a
human when it can't. Architecture: `../.claude/skills/project-architecture/SKILL.md`.

## Prerequisites

Install these once. `uv` manages the Python version itself, so a system Python is not required.

- **Docker Desktop** — runs the PostgreSQL database. https://www.docker.com/products/docker-desktop/
- **uv** — Python dependency and environment manager.

  | OS | Install command |
  |---|---|
  | macOS / Linux | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
  | Windows (PowerShell) | `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 \| iex"` |

## Setup

Run from the repository root unless noted.

```bash
# 1. Start PostgreSQL (pgvector image) in the background
docker compose up -d

# 2. Move into the backend
cd backend

# 3. Create your local env file from the template
cp .env.example .env              # macOS / Linux
Copy-Item .env.example .env       # Windows (PowerShell)

# 4. Install dependencies (also installs the correct Python and creates .venv)
uv sync

# 5. Run the API with autoreload
uv run uvicorn app.main:app --reload
```

The API is at http://localhost:8000, interactive docs at http://localhost:8000/docs.

## Common commands

Run from `backend/`.

| Task | Command |
|---|---|
| Run the API | `uv run uvicorn app.main:app --reload` |
| Run tests | `uv run pytest` |
| Lint | `uv run ruff check .` |
| Format | `uv run ruff format .` |
| Stop the database | `docker compose down` (from repo root) |
| Reset the database | `docker compose down -v` (from repo root; deletes all data) |

## Notes

- `.env` is git-ignored; never commit real secrets. Keep `.env.example` current when adding settings.
- Database credentials in `docker-compose.yml` are for local development only.
