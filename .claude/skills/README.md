# SmartPaperCheck — Claude Code Skills (whole project)

Project-scoped skills for the SmartPaperCheck AI support chatbot — backend, frontend,
testing, and infra — committed to the repo so every teammate shares the same conventions.
Each skill is its own folder as `SKILL.md` (folder name = kebab-case `name` in frontmatter).

## Install

Place the skill folders **directly** under your repo's `.claude/skills/` (no extra wrapper
folder, no domain grouping — nesting deeper than one level breaks discovery). Commit them.

```
.claude/skills/
├── project-architecture/SKILL.md   # scope, module layout, chat + escalation flow (READ FIRST)
├── fastapi-backend/SKILL.md
├── postgresql-database/SKILL.md     # + pgvector note
├── claude-ai-integration/SKILL.md   # Anthropic SDK chat loop + escalation tool-use
├── rag-retrieval/SKILL.md           # Retriever interface, embeddings, pgvector, ingestion
├── brevo-email/SKILL.md             # transactional email, background sends, isolation
├── frontend-development/SKILL.md    # React/Vite/Tailwind chat widget + escalation form
├── frontend-review/SKILL.md
├── webapp-testing/SKILL.md          # Playwright E2E of chat + escalation flows
├── docker-devops/SKILL.md           # optional; Railway uses nixpacks by default
├── ci-cd-pipeline/SKILL.md          # GitHub Actions quality gate (Railway/Vercel deploy)
└── README.md                        # human-only; ignored by the loader
```

## Roles

- **Backend** (owner): project-architecture, fastapi-backend, postgresql-database,
  claude-ai-integration, rag-retrieval, brevo-email.
- **Frontend**: frontend-development, frontend-review.
- **QA / any**: webapp-testing.
- **Infra**: docker-devops, ci-cd-pipeline.

## Changes from the original set

- **Kept + lightly project-tagged:** fastapi-backend, postgresql-database, frontend-development,
  webapp-testing, docker-devops, ci-cd-pipeline, frontend-review. Restructured into
  folder/`SKILL.md` form (the original `Backend/FastAPI.md` grouping would not have loaded).
- **Added (project-specific AI core):** project-architecture, claude-ai-integration,
  rag-retrieval, brevo-email.
- **Held out:** authentication — the MVP is a public chatbot with no login. Re-add when the
  admin dashboard/auth work begins.

Start every task from `project-architecture`; it hands off to the others by name.
