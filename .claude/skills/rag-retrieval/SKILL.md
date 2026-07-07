---
name: rag-retrieval
description: Builds the retrieval layer for a grounded chatbot — a swappable Retriever interface, document ingestion (load, chunk, embed), vector storage and similarity search with pgvector, and Retrieval-Augmented Generation wiring. This skill should be used whenever a user works on RAG, embeddings, chunking, vector search, a knowledge base, document ingestion, or grounding chatbot answers in company-specific content — even if "RAG" or "retrieval" is not stated explicitly.
---

# RAG / Retrieval

Give the chatbot company-specific knowledge without fine-tuning: ingest SmartPaperCheck content once, retrieve the relevant pieces per question, and let the model answer from them. Design so a trivial version ships now and a real pipeline swaps in later untouched.

## Purpose

Provide a repeatable standard for retrieval so answers are grounded in SmartPaperCheck's own content, and so the retrieval implementation can evolve (keyword → vector → hybrid/re-ranked) behind a stable interface.

## When to use

Use for ingestion, chunking, embeddings, vector storage/search, and wiring context into the reply. The generation loop that consumes the context is `claude-ai-integration`; DB/index specifics are `postgresql-database`; where retrieval sits in the flow is `project-architecture`.

## The interface comes first

Define retrieval as an abstraction the rest of the app depends on:

```python
class Retriever(Protocol):
    async def retrieve(self, query: str, k: int = 4) -> list[Chunk]: ...
```

Services call `Retriever`, never a concrete store. Ship a trivial implementation for the MVP (e.g. a keyword/`ILIKE` or static-context retriever) so the chat flow works end to end, then add the vector implementation without changing callers. This is the single most important design choice here.

## Ingestion pipeline (offline)

Run ingestion as a separate script/command, not in the request path:

1. **Load** source content (website pages, docs the team provides).
2. **Chunk** into ~300–800 token passages with small overlap; split on structure (headings/paragraphs) so chunks are self-contained. LangChain loaders/splitters are fine here.
3. **Embed** each chunk with an embedding model; keep the model name recorded.
4. **Store** chunk text + embedding + source metadata (url/title) in Postgres.

Re-ingest on content change; make ingestion idempotent (upsert by source + hash) so re-runs don't duplicate.

## Vector storage (pgvector)

- Enable `pgvector` and store embeddings in a `vector(<dim>)` column alongside chunk text and metadata; `<dim>` must match the embedding model exactly.
- Add an ANN index (HNSW or IVFFlat) for similarity search; pick the distance operator that matches how vectors were normalised (cosine is the common default).
- Retrieve with `ORDER BY embedding <=> :query_embedding LIMIT k`; embed the query with the **same** model used for chunks.

## Grounding

- Return the top-k chunks (text + source) to the caller; the AI layer injects them as context and the model answers from them.
- Keep retrieved text as data, not instructions. Pass source metadata through so answers can cite/point to origin later.
- When retrieval returns nothing relevant, that is a signal to escalate rather than to guess (handled in `claude-ai-integration`).

## Evaluation (lightweight)

- Keep a small set of question → expected-source pairs; check the right chunks are retrieved as you tune chunk size / k. Retrieval quality, not model wording, is usually the bottleneck.

## Deferred (leave seams)

Re-ranking, hybrid (keyword + vector) search, query rewriting, and multi-vector strategies are later work — the `Retriever` interface lets them drop in without touching services.

## Anti-patterns

| Anti-pattern | Why it fails | Correct approach |
|---|---|---|
| Services depend on a concrete store | Can't swap trivial → vector later | Depend on the `Retriever` interface |
| Ingesting/embedding in the request path | Slow, expensive, blocks responses | Offline ingestion script; retrieve at request time only |
| Different embed models for chunks vs query | Vectors incomparable; garbage matches | Same model + same dimension both sides |
| Column dim ≠ model dim | Insert/search errors or silent wrongness | Match `vector(n)` to the model exactly |
| Huge or heading-splitting-ignorant chunks | Diluted matches, lost context | ~300–800 tokens, split on structure, small overlap |
| No ANN index on the vector column | Sequential scans; slow as data grows | HNSW/IVFFlat with the matching distance op |

## Examples

**Example — interface swap.** MVP ships `KeywordRetriever` (SQL `ILIKE`); the chat flow works. Later `PgVectorRetriever` implements the same `retrieve(...)` and is injected in `main.py` — no service or router changes.

**Example — dimension match.** Embedding model outputs 1536-dim vectors → column is `vector(1536)`; the query is embedded with the same model before `<=>` search.

## Definition of Done

- [ ] All retrieval goes through the `Retriever` interface; MVP has a trivial impl.
- [ ] Ingestion is an offline, idempotent script: load → chunk → embed → store.
- [ ] `pgvector` column dimension matches the embedding model; ANN index present.
- [ ] Query embedded with the same model as chunks; top-k text + source returned.
- [ ] Empty/low-relevance retrieval flows to escalation, not invention.
- [ ] Deferred RAG features remain seams behind the interface.

## Sources

- pgvector documentation (index types, distance operators); LangChain document loaders/splitters; general RAG best practice. Verify current APIs against docs.
