---
name: project-architecture
description: Defines the architecture, MVP scope, and module boundaries for the SmartPaperCheck AI support chatbot backend — the layered folder layout, the end-to-end chat and escalation flows, what is in the MVP versus deferred, and the seams left for future features. This skill should be used whenever work touches how the SmartPaperCheck backend is structured, where a piece of code belongs, what to build now versus later, or how the chat/escalation/email pieces fit together — even if "architecture" is not stated explicitly.
---

# SmartPaperCheck — Project Architecture

The backend is a FastAPI service that answers product questions about SmartPaperCheck (an online exam conducting/evaluation platform) and escalates to humans when it cannot. Build a clean MVP with explicit seams for later features. Prefer boring, obvious structure over cleverness.

## Purpose

Give every piece of code one obvious home, fix the MVP boundary so the build stays incremental, and keep future features (LangGraph, agents, WhatsApp, admin dashboard, tickets) addable without rework.

## When to use

Use when deciding where code belongs, defining folder structure, wiring the chat or escalation flow end to end, or judging whether something is in scope for the MVP. Defers generic FastAPI/DB conventions to `fastapi-backend` and `postgresql-database`; the AI loop to `claude-ai-integration`; retrieval to `rag-retrieval`; email to `brevo-email`.

## MVP scope (build now)

1. `POST /api/v1/chat` — accept a user message + conversation id, return the assistant reply.
2. Persist every user message and assistant reply to Postgres.
3. Lead capture: the primary path is a deterministic button → form (`POST /api/v1/leads`); the model may also invoke the `escalate_to_human` tool (low confidence, or user asks for demo/sales/support/human). Both write a `leads` row and trigger notifications.
4. Brevo notifications: internal alert to the support team + confirmation email to the user.
5. Retrieval behind an interface — ship a trivial implementation; real RAG comes later.

## Explicitly deferred (leave a seam, do NOT build)

LangGraph / multi-step agents, WhatsApp channel, admin dashboard, ticket management, authentication/user accounts, advanced RAG (re-ranking, hybrid search). Each maps to a named boundary below so it slots in without touching unrelated code.

## Module layout

```
app/
├── main.py            # app factory, router registration, middleware, lifespan
├── core/              # settings (pydantic-settings), logging, constants
├── api/v1/            # routers — thin: validate, call service, shape response
├── schemas/           # Pydantic request/response models (API contract)
├── models/            # SQLAlchemy ORM models
├── repositories/      # data access (all DB queries live here)
├── services/          # business logic: chat_service, escalation_service
├── ai/                # Claude client, prompts, tools, escalation tool defn
├── retrieval/         # Retriever interface + implementations (see rag-retrieval)
└── integrations/      # external APIs: brevo/ (and future whatsapp/)
tests/   alembic/
```

Dependency direction is one-way: `api → services → (repositories | ai | retrieval | integrations)`. Nothing lower reaches back up. Routers never touch the DB, the Claude client, or Brevo directly — only services do.

## Chat flow (end to end)

1. Router validates the request and calls `chat_service.handle_message(...)`.
2. Service loads conversation history via the repository, calls `retrieval` for context, then calls the `ai` layer (Claude with tools).
3. If Claude returns a normal reply → persist user + assistant messages, return the reply.
4. If Claude invokes the escalate tool → hand the tool input to `escalation_service`.

## Escalation flow

1. `escalation_service` validates collected contact details, writes a `leads` row (`source` = `ai_tool`).
2. It schedules Brevo sends (internal + user confirmation) as **background tasks** so the HTTP response is not blocked.
3. It returns a user-facing acknowledgement for the assistant to relay.

Escalation is triggered by the model as a **tool call**, never by string-matching the model's prose (see `claude-ai-integration`).

## Data model (MVP)

`conversations (id, created_at, ...)` · `messages (id, conversation_id FK, role, content, created_at)` · `leads (id, conversation_id FK NULL, name, email, phone NULL, preferred_demo_time NULL, reason, source, status, created_at)` — both the deterministic form and the `escalate_to_human` tool insert here, distinguished by `source` (`form` | `ai_tool`). RAG chunks live in `doc_chunks (id, content, embedding vector(1024), source, title, ...)` (see `rag-retrieval`). Types/constraints/indexing per `postgresql-database`.

## Incremental build discipline

This is a learning-first project built step by step. Do not scaffold the whole app in one shot. Build one vertical slice at a time (schema → model → migration → repository → service → route → test), explain the reasoning before writing code, and stop at each slice for review. Owner works on the backend; do not scaffold React/Vercel/CI unless asked.

## Anti-patterns

| Anti-pattern | Why it fails | Correct approach |
|---|---|---|
| Building deferred features "while we're here" | Bloats the MVP, delays a working slice, adds untested surface | Leave the named seam; build only MVP scope |
| Router calling Claude/Brevo/DB directly | Collapses layers; untestable; logic scattered | Router → service only; service orchestrates the rest |
| Escalation decided by parsing model prose | Brittle, silently misfires | Model invokes an escalate tool; branch on the tool call |
| Sending email inside the request path | Blocks the response on a third-party API | Schedule Brevo via background tasks |
| Hard-wiring a concrete retriever into services | Can't swap trivial → real RAG later | Depend on the `Retriever` interface |

## Definition of Done

- [ ] New code lives in the correct layer; dependency direction is one-way.
- [ ] Work is a single reviewable vertical slice, not a bulk scaffold.
- [ ] Only MVP scope is implemented; deferred features remain seams.
- [ ] Escalation is tool-driven; emails are backgrounded; retrieval is behind the interface.
- [ ] Reasoning was explained before code was written.
