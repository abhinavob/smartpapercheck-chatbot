---
name: webapp-testing
description: Tests local web applications with Playwright — verifying frontend functionality, debugging UI behavior, capturing screenshots, and reading browser/console logs. This skill should be used whenever a user wants to test, verify, or debug a running web app's UI, write end-to-end or browser tests, automate clicking through a frontend, or check that a frontend and backend work together — even if "Playwright" or "testing" is not stated explicitly.
---

# Web Application Testing

Test local web applications by writing native Playwright scripts. Favor a reconnaissance-then-action approach: observe the rendered page before acting on it.

> **Project note (SmartPaperCheck):** the two flows worth covering end to end are (1) sending a chat message and receiving a grounded reply, and (2) triggering escalation and submitting the contact form (name/email/optional phone/optional demo time). Assert the escalation request is acknowledged in the UI; the backend persists it and sends Brevo email out of band, so don't assert on email delivery here.

## Purpose

Provide a repeatable standard for browser-based testing and debugging so frontend behavior is verified against a real rendered DOM, not assumptions about it.

## When to use

Use to verify a feature works end to end, reproduce a UI bug, capture screenshots/logs for debugging, or confirm a frontend integrates correctly with its backend. For lower-level component logic, prefer unit tests (Vitest/Jest); for backend endpoint tests, see `fastapi-backend`; use this skill for behavior in a real browser.

## Decision tree: choosing the approach

```
Task → Is it static HTML?
  ├─ Yes → Read the HTML file directly to identify selectors
  │         ├─ Works → write a Playwright script using those selectors
  │         └─ Incomplete → treat as dynamic (below)
  └─ No (dynamic webapp) → Is the server already running?
        ├─ No → start the server, then write a simplified Playwright script
        └─ Yes → Reconnaissance-then-action:
              1. Navigate and wait for networkidle
              2. Screenshot or inspect the DOM
              3. Identify selectors from the rendered state
              4. Execute actions with the discovered selectors
```

## Reconnaissance-then-action pattern

1. Inspect the rendered DOM after it settles:
```python
page.screenshot(path='/tmp/inspect.png', full_page=True)
content = page.content()
page.locator('button').all()
```
2. Identify selectors from what actually rendered.
3. Execute actions using the discovered selectors.

The critical rule: on dynamic apps, wait for the page to finish loading before inspecting, or selectors won't exist yet.

## Minimal Playwright script

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)   # always headless
    page = browser.new_page()
    page.goto('http://localhost:5173')
    page.wait_for_load_state('networkidle')       # CRITICAL: wait for JS to execute
    # ... assertions / actions ...
    browser.close()
```

## What to test (priority order)

1. **Critical user flows** end to end (sign-up, the core action, checkout) — these protect revenue and trust.
2. **Form validation and error states** — both the happy path and the rejected input.
3. **Auth-gated behavior** — protected routes redirect when unauthenticated.
4. **Integration points** — the frontend renders what the backend actually returns.

Keep most logic in fast unit tests; reserve browser tests for behavior that only emerges in a real browser. This is the testing-pyramid discipline: many unit tests, fewer integration tests, a small set of end-to-end browser tests.

## Common pitfalls

- Inspecting the DOM before `networkidle` on dynamic apps — selectors will be missing.
- Brittle selectors tied to styling. Prefer role/text/test-id selectors (`get_by_role`, `text=`, `data-testid`) over deep CSS chains.
- Forgetting to close the browser, leaking processes.
- Fixed `sleep()` waits instead of `wait_for_selector()` / `wait_for_load_state()`.

## Best practices

- Launch chromium headless for automation.
- Use descriptive, resilient selectors: `role=`, `text=`, `data-testid`, or stable IDs.
- Add explicit waits (`wait_for_selector`, `wait_for_load_state`) rather than arbitrary timeouts.
- Capture a screenshot and console logs on failure to make debugging fast.
- Keep each test independent and idempotent; reset state between tests.

## Anti-patterns

| Anti-pattern | Why it fails | Correct approach |
|---|---|---|
| Inspecting the DOM before `networkidle` | On dynamic apps the elements aren't rendered yet; selectors miss | `wait_for_load_state('networkidle')` before inspecting |
| `time.sleep(3)` to wait for the UI | Flaky — too short fails, too long is slow | `wait_for_selector` / `wait_for_load_state` |
| Deep CSS-chain selectors (`div > div > .btn`) | Break on any styling change | Role/text/test-id selectors |
| End-to-end testing everything | Slow, flaky, expensive to maintain | Pyramid: most logic in unit tests, few E2E flows |
| Tests sharing mutable state | One test's data breaks the next; order-dependent | Independent, idempotent tests; reset state between |

## Examples

**Example — reconnaissance before action**
For "verify the login form rejects a bad password": navigate, `wait_for_load_state('networkidle')`, screenshot to confirm the form rendered, locate the email/password fields and submit button by role/test-id, submit invalid input, then assert the error message is visible — rather than assuming selector names up front.

## Definition of Done

- [ ] Dynamic pages wait for `networkidle` before inspection/action.
- [ ] Selectors are role/text/test-id based, not styling-coupled CSS chains.
- [ ] Explicit waits used; no fixed `sleep()`.
- [ ] Critical flows, validation/error states, and auth-gating are covered.
- [ ] Each test is independent and idempotent; state reset between tests.
- [ ] Browser is closed; screenshot + console logs captured on failure.

## Sources adapted and merged

- Anthropic official `webapp-testing` skill — https://github.com/anthropics/skills/tree/main/skills/webapp-testing (decision tree, reconnaissance-then-action, networkidle rule, headless Playwright pattern). The official skill ships helper scripts (e.g. `scripts/with_server.py` to manage server lifecycle) and `examples/` — install it directly to get those black-box scripts; this file captures the patterns in self-contained form.
- Testing-pyramid guidance from mainstream test strategy.
