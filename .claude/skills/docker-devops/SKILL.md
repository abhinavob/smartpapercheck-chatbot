---
name: docker-devops
description: Containerizes applications for production with Docker, covering multi-stage builds, small and secure images, layer caching, non-root hardening, Docker Compose stacks, healthchecks, and deployment-ready configuration. This skill should be used whenever a user writes a Dockerfile, containerizes an application, sets up docker-compose, optimizes image size or build speed, or works on container deployment / DevOps tasks — even if "Docker" is not stated explicitly.
---

# Docker & Containerization

Produce container images that are small, secure, reproducible, and ready to run under an orchestrator. A good image builds fast, ships only what it needs, and runs as an unprivileged user.

> **Project note (SmartPaperCheck):** deployment is Railway (backend + Postgres) and Vercel (frontend). Railway builds from nixpacks by default, so a Dockerfile is **optional** — add one only if you outgrow nixpacks or want reproducible local parity. Vercel builds the frontend directly; it is not containerized.

## Purpose

Provide a repeatable standard for containerization so generated Dockerfiles and Compose stacks are production-grade: multi-stage, minimal, hardened, healthchecked, and configurable via environment.

## When to use

Use when authoring a Dockerfile, defining a local multi-service stack, reducing image size or build time, or preparing a container for deployment. To build, test, and ship these images automatically, pair with the `ci-cd-pipeline` skill — this skill makes the artifact, that one promotes it.

## Requirements

- Docker, and Docker Compose v2 for local multi-service stacks.
- A `.dockerignore` to keep build context (and image) small and free of secrets.
- Pinned base image versions (e.g. `python:3.12-slim`), never bare `latest`.

Before writing a Dockerfile, confirm: language/runtime, build vs. runtime dependencies, the listening port, and how config/secrets are supplied.

## Multi-stage build pattern

Always use multi-stage builds to keep build tools out of the final image:

```dockerfile
# ---- build stage ----
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- runtime stage ----
FROM python:3.12-slim AS runtime
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .
RUN useradd -m appuser
USER appuser
EXPOSE 8000
HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

The runtime stage carries only installed dependencies and app code — no compilers, no build cache.

## Layer and cache optimization

- Order instructions least- to most-frequently-changing. Copy dependency manifests and install before copying source, so dependency layers stay cached when only code changes.
- Combine related `RUN` commands and clean up in the same layer (`apt-get ... && rm -rf /var/lib/apt/lists/*`) so cleanup actually shrinks the image.
- Use `--no-cache-dir` (pip) / `npm ci --omit=dev` to avoid bundling caches and dev dependencies.
- Choose minimal bases: `-slim` or `distroless` over full OS images; `alpine` only when its musl tradeoffs are acceptable.

## Security hardening

- Run as a non-root user: create a dedicated user and `USER` it before `CMD`.
- Pin base image tags (ideally by digest) for reproducibility.
- Keep secrets out of images and build args — they persist in layers/history. Inject at runtime via environment variables or a secrets manager.
- Copy only what is needed; rely on `.dockerignore` to exclude `.git`, `.env`, `node_modules`, test data, credentials.
- Scan images for CVEs (Trivy, Docker Scout) in CI; rebuild on base-image security updates.

## Healthchecks and runtime config

- Add a `HEALTHCHECK` (or rely on orchestrator liveness/readiness probes) so the platform knows when the container is actually ready, not merely started.
- Configure the app entirely through environment variables; never bake environment-specific config into the image. One image, many environments.
- Handle shutdown gracefully (forward signals; use `tini` if the process doesn't reap children) so deploys don't drop in-flight requests.
- Log to stdout/stderr, not to files inside the container.

## Docker Compose (local development)

- Define the full local stack (app, database, cache) in `docker-compose.yml`.
- Use named volumes for database persistence and bind mounts for source during development.
- Add `depends_on` with `condition: service_healthy` so the app waits for the database to be ready, not just started.
- Keep secrets in a gitignored `.env` referenced by Compose — never commit real credentials.

## Production readiness

- Tag images meaningfully (git SHA or semver), not `latest`, so deploys are traceable and rollbacks precise.
- Set resource requests/limits at the orchestrator level; design the container stateless and horizontally scalable.
- Expose liveness and readiness endpoints the platform can probe.
- Build images in CI from a clean context; don't hand-push locally-built images. (See `ci-cd-pipeline`.)

## Anti-patterns

| Anti-pattern | Why it fails | Correct approach |
|---|---|---|
| `FROM node:latest` (or bare `:latest`) | Builds are irreproducible; the base shifts under you | Pin a specific tag, ideally by digest |
| Running the container as root | A container escape runs as host root | Create a user and `USER` it before `CMD` |
| Secrets in `ENV`/build args | They persist in image layers and history | Inject at runtime via env/secrets manager |
| `COPY . .` before installing deps | Every code edit busts the dependency layer; slow rebuilds | Copy manifests, install, then copy source |
| No `.dockerignore` | `.git`, `.env`, `node_modules` bloat the image and leak secrets | Add `.dockerignore` excluding them |
| Single-stage image with build tools | Ships compilers and caches; large attack surface | Multi-stage; final stage carries only runtime deps + code |

## Examples

**Example 1 — dependency caching**
Anti-pattern: `COPY . .` then `RUN pip install -r requirements.txt` — every source change busts the dependency layer.
Fix: `COPY requirements.txt .` → `RUN pip install ...` → then `COPY . .`. Dependencies reinstall only when the manifest changes.

**Example 2 — Compose waiting for a healthy database**
```yaml
services:
  db:
    image: postgres:16
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 5s
      retries: 5
  api:
    build: .
    depends_on:
      db: { condition: service_healthy }
    environment:
      DATABASE_URL: postgresql+asyncpg://app:secret@db:5432/app
```
Rationale: the API starts only once Postgres reports healthy, eliminating start-order races.

## Definition of Done

- [ ] Multi-stage build; final image has no compilers/build cache.
- [ ] Runs as a non-root user; base image pinned (digest preferred).
- [ ] `.dockerignore` present; no secrets in the image, `ENV`, or build args.
- [ ] Dependency layers cached before source copy.
- [ ] `HEALTHCHECK` (or orchestrator probes) and graceful shutdown handled.
- [ ] Config is entirely environment-driven; logs go to stdout/stderr.
- [ ] Image tagged by git SHA/semver, not `latest`.

## Sources adapted and merged

- `Ashfaqbs/software-dev-ai-claude-toolkit` → infra rules (Docker multi-stage, K8s probes/HPA/PDB) — https://github.com/Ashfaqbs/software-dev-ai-claude-toolkit
- `rohitg00/awesome-claude-code-toolkit` → DevOps automation references — https://github.com/rohitg00/awesome-claude-code-toolkit
- Docker official documentation (multi-stage builds, Dockerfile best practices). Note: Anthropic's official repo has no Docker skill; content is community-sourced plus Docker best practice.
