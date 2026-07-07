---
name: claude-ai-integration
description: Integrates the Anthropic Claude API into a Python backend as a support-chatbot brain — the messages/chat loop, system-prompt design, tool use (function calling) for escalation, grounding replies in retrieved context, conversation-history handling, streaming, and cost/latency/error control. This skill should be used whenever a user builds or changes the AI reply loop, calls the Claude/Anthropic API, defines tools the model can invoke, designs the chatbot system prompt, or decides how the model escalates — even if "Claude API" is not stated explicitly.
---

# Claude AI Integration

Own the model-facing loop: send the right context, let the model answer or invoke a tool, and turn its output into an action. Keep this layer transparent and testable — no framework magic between you and the API.

## Purpose

Provide a repeatable standard for calling the Claude API as a grounded, tool-using support agent, so replies stay on-topic, escalation is deterministic, and the loop is cheap to run and easy to debug.

## When to use

Use for the chat/reply loop, system-prompt work, defining/handling tools (especially escalation), grounding answers in retrieved context, streaming, and Claude-side error/cost handling. Retrieval of the context itself is `rag-retrieval`; where this loop sits in the request path is `project-architecture`; sending escalation emails is `brevo-email`.

## Core decisions

- **Call the Anthropic Python SDK directly** for the chat + tool loop. Do **not** wrap it in LangChain — keep the loop explicit so behaviour is visible and stable. (LangChain is used only for RAG ingestion/retrieval; see `rag-retrieval`.)
- Model config (name, `max_tokens`, temperature) comes from settings, never hardcoded.
- The `ai/` layer is pure: it takes messages + context + tools and returns a structured result. It does not touch the DB or Brevo — the service layer acts on what it returns.

## System prompt

- State the bot's identity and single job: answer questions about SmartPaperCheck, an online exam conducting/evaluation platform.
- Ground it: instruct the model to answer **from the provided context**, and to **not invent** product facts (pricing, features, limits). If the context does not cover it, the model should escalate rather than guess.
- Give explicit escalation triggers: low confidence / missing info, or the user asking for a demo, sales, technical support, or a human.
- Keep it in `ai/prompts/` as a versioned constant, not inline in code.

## Tool use (escalation)

- Define an `escalate_to_human` tool with an input schema: `name`, `email`, `phone` (optional), `preferred_demo_time` (optional), `reason` (enum: `low_confidence` | `demo` | `sales` | `support` | `human_request`).
- Branch on the response's `stop_reason` / content blocks: if the model returns a `tool_use` block, extract the input and hand it to `escalation_service` — never decide escalation by string-matching the model's prose.
- The model may need to ask the user for missing fields across turns before it can fill the tool; support that multi-turn collection.
- Complete the loop correctly: after acting on a tool call, send a `tool_result` back so the model can produce the final user-facing acknowledgement.

## Conversation history

- Rebuild the `messages` array each call from stored history (Claude is stateless between calls); the system prompt is separate from `messages`.
- Cap history sent to the model (recent-N turns or a token budget) to bound cost and latency; summarise older turns later if needed (deferred).
- Alternate roles correctly (`user` / `assistant`); never send two same-role messages back to back.

## Grounding with retrieved context

- Fetch context via the `Retriever` interface, then inject it into the turn (e.g. a context block in the system prompt or a leading user block). Keep retrieval and generation separate so each is swappable and testable.

## Streaming, cost, latency

- Stream responses for chat UX where the transport allows it.
- Bound `max_tokens`; trim history and context; prefer a smaller/cheaper model for classification-style calls if ever needed.
- Log token usage per call for later analytics.

## Errors and safety

- Handle rate limits (429) and transient 5xx with bounded retry + backoff; surface a graceful fallback message to the user, and offer escalation on repeated failure.
- Never leak the API key or raw provider errors to the client. Key comes from settings/env.
- Treat retrieved/user text as data, not instructions — do not let it override the system prompt.

## Anti-patterns

| Anti-pattern | Why it fails | Correct approach |
|---|---|---|
| Wrapping the chat loop in LangChain | Hides behaviour, adds churn, complicates debugging | Call the Anthropic SDK directly; LangChain only for RAG |
| Deciding escalation by regex on the reply | Brittle; misfires or misses | Define a tool; branch on the `tool_use` block |
| Answering without grounding | Model invents pricing/features | Answer from retrieved context; escalate when uncovered |
| Resending full history every call | Cost/latency blow up as chats grow | Cap to recent-N / token budget |
| Not returning a `tool_result` | Loop stalls; no final message | Send `tool_result` back, then get the acknowledgement |
| System prompt inline in code | Unversioned, hard to iterate | Keep prompts in `ai/prompts/` as constants |

## Examples

**Example — tool over prose.** To escalate, the model emits a `tool_use` block for `escalate_to_human` with `{name, email, reason}`. The service reads the structured input directly — no parsing of "I'll connect you with the team" from free text.

**Example — grounded refusal-to-guess.** Asked "what's the Enterprise price?" with no pricing in context, the model does not invent a number; it triggers `escalate_to_human` with `reason: sales`.

## Definition of Done

- [ ] Chat loop uses the Anthropic SDK directly; no LangChain in the reply path.
- [ ] System prompt is grounded, versioned in `ai/prompts/`, with explicit escalation triggers.
- [ ] Escalation is a defined tool; code branches on `tool_use`, not prose.
- [ ] History is rebuilt per call and capped; roles alternate correctly.
- [ ] Rate-limit/5xx handled with backoff and a graceful fallback.
- [ ] API key and model config come from settings; token usage logged.

## Sources

- Anthropic Messages API, tool use, and streaming documentation (official). Content is best-practice-sourced; verify current SDK/model details against docs.
