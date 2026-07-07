---
name: postgresql-database
description: Designs and operates production PostgreSQL databases, covering schema modeling, normalization, data types, indexing, query optimization, safe migrations, transactions, concurrency, and least-privilege access. This skill should be used whenever a user designs a database schema, writes or optimizes SQL, adds indexes or migrations, models data relationships, or works with PostgreSQL or any relational database — even if "PostgreSQL" is not stated explicitly.
---

# PostgreSQL Database

Design relational schemas that stay correct and fast as data grows. Treat the schema as a long-lived contract: changes go through migrations, and queries are written to use indexes.

> **Project note (SmartPaperCheck):** the same Postgres instance also serves vector search via the **`pgvector`** extension (enable it in an Alembic migration: `CREATE EXTENSION IF NOT EXISTS vector`). Core MVP tables are `conversations`, `messages`, and `escalation_requests` (see `project-architecture`). Embedding storage/indexing specifics live in `rag-retrieval`.

## Purpose

Provide a repeatable standard for PostgreSQL work so schemas are well-modeled, queries are performant, migrations are safe, and integrity is enforced by the database rather than hoped for in application code.

## When to use

Use when designing tables and relationships, choosing keys and types, writing or tuning SQL, adding indexes, or authoring migrations. Pairs with `fastapi-backend` for the application's data layer; that skill owns the API surface, this one owns the data model.

## Requirements

- PostgreSQL 14+.
- Schema changes managed through a migration tool (Alembic, Prisma Migrate, Flyway) — never ad-hoc DDL against production.
- A connection pooler (PgBouncer) in production.

Before designing, confirm: expected scale, read/write ratio, and the access patterns (which queries must be fast). Schema design follows from how data will be queried.

## Schema design

- Normalize to 3NF by default; denormalize deliberately only when a measured read pattern requires it, and document why.
- Choose primary keys intentionally: `BIGINT GENERATED ALWAYS AS IDENTITY` for internal keys, or `UUID` (v7 for index locality) when IDs are client-generated or externally exposed.
- Use correct types: `TIMESTAMPTZ` (never naive `TIMESTAMP`), `NUMERIC` for money (never `FLOAT`), `TEXT` over arbitrary `VARCHAR(n)`, native `BOOLEAN`, `JSONB` (not `JSON`) for semi-structured data, `ENUM` or a lookup table for fixed sets.
- Enforce integrity in the database: `NOT NULL`, `UNIQUE`, `CHECK`, and `FOREIGN KEY` with explicit `ON DELETE`. Constraints are cheaper than bugs.
- Name consistently: `snake_case`, plural tables, `<table>_id` foreign keys, `created_at`/`updated_at TIMESTAMPTZ` on most tables.

## Indexing

- Index foreign keys and any column used in `WHERE`, `JOIN`, `ORDER BY`, or `GROUP BY` on hot queries.
- Build composite indexes in filter order: equality columns first, then range/sort columns.
- Use partial indexes for queries that always filter a subset (e.g. `WHERE deleted_at IS NULL`).
- Use GIN indexes for `JSONB` and full-text search.
- Don't over-index: every index slows writes and consumes space. Add indexes for real queries, then verify with `EXPLAIN`.

## Query optimization

- Use `EXPLAIN (ANALYZE, BUFFERS)` to read the real plan; watch for sequential scans on large tables, bad row estimates, and nested loops over big sets.
- Select only needed columns — avoid `SELECT *` in application queries.
- Eliminate N+1 patterns with a `JOIN` or one batched query rather than a query per row.
- Paginate with keyset/cursor pagination (`WHERE id > :last ORDER BY id LIMIT n`) rather than large `OFFSET`, which degrades linearly.
- Keep statistics fresh so the planner estimates well (autovacuum/ANALYZE running).

## Migrations

- Every schema change is a versioned, reviewed migration with a tested rollback path.
- Make migrations safe on live tables: add a column with a non-volatile default freely; add `NOT NULL` to a populated table in steps (add nullable → backfill → validate constraint).
- Create indexes on large production tables with `CREATE INDEX CONCURRENTLY` to avoid locking writes.
- Separate schema migrations from large data backfills; run backfills in batches.

## Transactions and concurrency

- Wrap multi-statement units of work in a transaction; keep transactions short to reduce lock contention.
- Choose isolation deliberately (`READ COMMITTED` default; `SERIALIZABLE` when correctness under concurrency demands it, with retry-on-conflict).
- Prevent lost updates with row locks (`SELECT ... FOR UPDATE`) or optimistic concurrency (a `version` column), depending on contention.

## Safety and access

- The application connects with a least-privilege role, not a superuser; grant only needed privileges.
- Always use parameterized queries / bound parameters — never build SQL by string concatenation (SQL injection).
- For history/audit needs, prefer soft delete (`deleted_at` + partial indexes) over hard delete.
- Back up regularly and test restores; an untested backup is a hope, not a backup.

## Anti-patterns

| Anti-pattern | Why it fails | Correct approach |
|---|---|---|
| `SELECT *` in application queries | Fetches unused columns; breaks when the schema changes | Select only the columns the code uses |
| `LIMIT n OFFSET 100000` pagination | Scans and discards every skipped row; degrades linearly | Keyset pagination: `WHERE id > :last ORDER BY id LIMIT n` |
| Naive `TIMESTAMP` (no time zone) | Ambiguous instants; DST and cross-region bugs | Always `TIMESTAMPTZ` |
| `FLOAT`/`DOUBLE` for money | Binary floating point can't represent decimals exactly | `NUMERIC(precision, scale)` |
| Unindexed foreign key | Joins and cascade checks do sequential scans | Index every FK used in joins/filters |
| String-concatenated SQL | SQL injection; one unsanitized input owns the DB | Parameterized queries / bound parameters only |

## Examples

**Example 1 — composite index matching a query**
Query: `SELECT id, total FROM orders WHERE customer_id = $1 AND status = $2 ORDER BY created_at DESC;`
Index: `CREATE INDEX ON orders (customer_id, status, created_at DESC);`
Rationale: equality columns lead, the sort column follows, so one index serves both the filter and the ordering.

**Example 2 — keyset pagination instead of OFFSET**
Anti-pattern: `... ORDER BY id LIMIT 20 OFFSET 100000;` scans and discards 100k rows per page.
Fix: `... WHERE id > :last_seen_id ORDER BY id LIMIT 20;` — constant-time per page using the primary-key index.

## Definition of Done

- [ ] Keys and types chosen intentionally (`TIMESTAMPTZ`, `NUMERIC` for money, `JSONB`, deliberate PK).
- [ ] Integrity enforced in the DB (`NOT NULL`, `UNIQUE`, `CHECK`, `FOREIGN KEY` with `ON DELETE`).
- [ ] Indexes exist for hot-query filters/joins/sorts; FKs indexed; no speculative over-indexing.
- [ ] Hot queries checked with `EXPLAIN (ANALYZE, BUFFERS)`; no `SELECT *`; keyset pagination.
- [ ] Every schema change is a reviewed, reversible migration; large indexes built `CONCURRENTLY`.
- [ ] All queries parameterized; app uses a least-privilege role.

## Sources adapted and merged

- `Jeffallan/claude-skills` → Postgres Pro / SQL Pro — https://github.com/Jeffallan/claude-skills (indexing, query optimization, migration patterns).
- `Ashfaqbs/software-dev-ai-claude-toolkit` → databases rules (migrations, indexes, UUIDs) — https://github.com/Ashfaqbs/software-dev-ai-claude-toolkit
- PostgreSQL documentation for type selection, indexing, and `EXPLAIN`. Note: Anthropic's official repo has no database skill; content is community-sourced plus Postgres best practice.
