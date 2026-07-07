---
name: brevo-email
description: Sends transactional email through the Brevo API from a Python backend for escalation notifications — an internal alert to the support team and a confirmation email to the user — with the integration isolated behind a client, sends run off the request path as background tasks, and failures handled without breaking the user flow. This skill should be used whenever a user integrates Brevo, sends notification or confirmation emails, wires escalation notifications, or works with transactional email or email templates in the backend — even if "Brevo" is not stated explicitly.
---

# Brevo Email Integration

Notify humans reliably without coupling the app to a vendor or blocking user requests. Keep all Brevo specifics behind one client so the rest of the code depends on an intent ("notify support"), not on Brevo.

## Purpose

Provide a repeatable standard for transactional email via Brevo so escalations reliably reach the support team and users get confirmation, while the request stays fast and the vendor stays swappable.

## When to use

Use when integrating Brevo, sending escalation/confirmation emails, or handling notification delivery. What triggers a notification (the escalation) is `escalation_service` in `project-architecture`; running sends off-thread uses FastAPI background tasks per `fastapi-backend`.

## Isolation

- All Brevo code lives in `integrations/brevo/`. Expose a small interface — e.g. `EmailClient.send(to, subject, ...)` or intent methods `notify_support(request)` / `send_confirmation(request)`.
- Services call that interface, never the Brevo SDK/HTTP directly. This keeps the vendor swappable and the services testable with a fake client.
- API key, sender identity, and support recipient come from settings/env — never hardcoded, never in the repo.

## Sending model

- Send **off the request path** using FastAPI `BackgroundTasks`, so the HTTP response returns immediately and isn't blocked on Brevo. (Celery/queue is deferred until volume warrants it.)
- On an escalation, schedule **two** messages: an internal alert to support (with the request details) and a confirmation to the user (acknowledging receipt).
- Prefer Brevo **templates** (template id + params) over HTML built in Python, so copy changes without a deploy; keep template ids in settings.

## Reliability

- Treat email as best-effort but observable: catch and **log** send failures (with a correlation/escalation id); never let a failed email raise out of the request and break the chat response — the `escalation_request` row is already persisted and is the source of truth.
- Add bounded retry/backoff on transient Brevo errors inside the client.
- Make notification idempotent where feasible (guard against double-send on retry) and record send status against the escalation for later admin/analytics.
- Validate the recipient email before scheduling.

## Testing

- Unit-test services against a fake `EmailClient` (assert it was called with the right recipient/params) — do not hit Brevo in tests.
- Keep one manual/integration check against Brevo's sandbox or a test key, run deliberately, not in CI by default.

## Anti-patterns

| Anti-pattern | Why it fails | Correct approach |
|---|---|---|
| Calling Brevo directly from a service/router | Vendor lock-in; untestable; scattered keys | Go through `integrations/brevo/` client |
| Sending inside the request handler | Blocks the response on a third-party call | Schedule via `BackgroundTasks` |
| Email failure bubbles up and 500s the chat | User loses the reply over a side-effect | Catch + log; row is the source of truth |
| Hardcoded key/sender/recipient | Leaks secrets; can't vary by env | Load from settings/env |
| HTML strings built in Python | Copy changes need code deploys | Brevo templates + params |

## Examples

**Example — backgrounded dual send.** `escalation_service` persists the request, then schedules `notify_support(request)` and `send_confirmation(request)` as background tasks; the endpoint returns the assistant's acknowledgement immediately.

**Example — swallow-and-log.** A Brevo 5xx during send is retried with backoff, then logged with the escalation id if still failing. The chat response is unaffected; support can recover from the stored row.

## Definition of Done

- [ ] All Brevo access is behind an `integrations/brevo/` client; services use the interface.
- [ ] Sends run as background tasks; the request path never blocks on email.
- [ ] Escalation triggers both internal alert and user confirmation.
- [ ] Key/sender/recipient/template ids come from settings; nothing hardcoded.
- [ ] Send failures are caught, retried with backoff, and logged; chat never breaks on email.
- [ ] Services tested against a fake client; no live Brevo calls in unit tests.

## Sources

- Brevo transactional email API documentation; FastAPI `BackgroundTasks`. Verify current Brevo SDK/endpoint details against docs.
