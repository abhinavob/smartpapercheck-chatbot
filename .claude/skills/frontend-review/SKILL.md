---
name: frontend-review
description: Reviews and critiques existing frontend code for correctness, type safety, accessibility, performance, security, and design quality, then returns a prioritized, fix-oriented report. This skill should be used whenever a user asks to review, audit, refactor, or improve frontend/UI/React/TypeScript code, requests a code review of a component or pull request, or wants feedback on a frontend implementation before merging.
---

# Frontend Review

Audit frontend code the way a senior engineer reviews a pull request: find real problems, prioritize them by impact, and give specific, actionable fixes — not vague praise.

## Purpose

Provide a consistent, thorough review pass over frontend code so issues are caught before they ship. This skill pairs with `frontend-development`: that one builds, this one verifies. For verifying behavior in a real browser rather than reading code, use `webapp-testing`.

## When to use

Use for any request to review, audit, critique, or refactor frontend code, or to evaluate a component or PR before merge.

## Workflow

1. Understand intent first: state in one sentence what the code is supposed to do, and review against that intent — not a preferred rewrite.
2. Pass through each review dimension below in order, noting findings.
3. Prioritize findings into Blocking (must fix), Should-fix, and Nitpick (optional). Lead with Blocking.
4. Give concrete fixes: show the problem and the corrected code or a precise change. Never stop at "this could be better."
5. Briefly acknowledge what is done well, so the author knows what to keep.

## Review dimensions

**Correctness** — Are loading/empty/error/success states all handled? Are list keys stable IDs, not indices? Any state that should be derived but is stored (and synced with effects)? Race conditions where stale responses overwrite newer ones? Unhandled `null`/`undefined`?

**Types** — Strict typing throughout? Any `any`, unsafe casts, or `!` assertions hiding real gaps? Do prop and API types match the actual data shape?

**Accessibility** — Semantic elements (`button` vs clickable `div`)? Keyboard-navigable with visible focus? Labels on inputs, `aria-label` on icon buttons? Sufficient contrast; color not the sole signal; `alt` present?

**Performance** — Unnecessary re-renders from unstable callbacks/objects passed to memoized children? Unvirtualized large lists? Heavy work on the render path? Missing code-splitting; oversized imports?

**Security** — `dangerouslySetInnerHTML` without sanitization (XSS)? Secrets/tokens/keys in client code? User input rendered or placed in URLs without escaping?

**State & architecture** — Server state through a query layer vs. hand-rolled caching? Business logic leaking into JSX? Components too large or doing too much?

**Design & copy** — Does it read as a deliberate design or a generic default (centered layout, purple gradient, uniform radii, reflexive Inter)? Is microcopy user-facing, active-voice, and consistent across the flow? Do empty/error states give direction rather than dead ends?

## Output format

ALWAYS structure the review like this:

```
## Summary
[1–2 sentences: what the code does and overall assessment]

## Blocking
- [Issue] — [why it matters] — [fix]

## Should-fix
- [Issue] — [fix]

## Nitpicks
- [Issue]

## What's good
- [Brief positives worth keeping]
```

## Reviewer best practices

- Be specific and kind: critique the code, not the author, and explain why each issue matters so it teaches.
- Don't rewrite everything in a personal style; respect the existing approach unless it is actually wrong.
- Distinguish objective bugs from preferences, and label preferences as such.
- Ask when intent is ambiguous rather than assuming.
- Prefer the smallest change that fixes the problem.

## Anti-patterns (of reviewing)

| Anti-pattern | Why it fails | Correct approach |
|---|---|---|
| "This could be better" with no fix | Gives the author nothing to act on | Show the problem and the corrected code or precise change |
| Rewriting working code to personal taste | Wastes effort, breeds churn, erodes trust | Respect the existing approach unless it is actually wrong |
| Labeling a preference as a bug | Effort goes to the wrong place; author tunes out | Separate objective bugs from preferences and label them |
| Burying a Blocking issue under nitpicks | The critical fix gets lost in noise | Lead with Blocking; order by impact |
| Reviewing against a rewrite you'd prefer | Misses whether the code meets its own intent | State the code's intent first; review against that |

## Examples

**Example — flag a real bug with a fix**
Found: `{items.map((item, i) => <Row key={i} item={item} />)}`
Finding (Blocking): array-index keys break rendering when the list reorders or items are deleted — React reuses the wrong DOM nodes and state. Fix: `key={item.id}`.

**Example — severity calibration**
A missing `aria-label` on an icon-only delete button is **Blocking** (invisible to screen readers); choosing `gap-3` over `gap-4` is a **Nitpick** (preference). Label accordingly so effort goes where it matters.

## Definition of Done

- [ ] The code's intent is stated in one sentence and used as the review baseline.
- [ ] All seven dimensions were passed through.
- [ ] Every finding has a concrete fix, not just a complaint.
- [ ] Findings are prioritized Blocking / Should-fix / Nitpick, Blocking first.
- [ ] Preferences are labeled as preferences, separate from objective bugs.
- [ ] Output follows the standard format, including a short "What's good."

## Sources adapted and merged

- Review dimensions derived from `frontend-development` standards and Anthropic's `frontend-design` anti-slop heuristics — https://github.com/anthropics/skills/tree/main/skills/frontend-design
- Accessibility checks aligned to WCAG; security checks aligned to common frontend XSS guidance (OWASP).
