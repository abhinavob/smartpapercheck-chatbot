---
name: frontend-development
description: Builds production-grade frontend UI with React, TypeScript, and Tailwind CSS, covering component architecture, server vs. client state, data fetching, accessibility, performance, and distinctive (non-templated) visual design. This skill should be used whenever a user creates or modifies user-facing UI, builds React/TypeScript components, wires client-side state or routing, integrates an API into a frontend, or requests anything visual or interactive — even if "frontend" is not stated explicitly.
---

# Frontend Development

Build interfaces that are correct, accessible, fast, and visually intentional — never templated defaults. Treat every component as something shipping to real users on real devices.

> **Project note (SmartPaperCheck):** the frontend is a chat widget embedded in the site. It calls the backend `POST /api/v1/chat` (stream when possible), renders conversation history, and shows an escalation form collecting name, email, optional phone, and optional preferred demo time. Treat the API request/response shape as the contract owned by `project-architecture`; coordinate changes with the backend rather than inventing fields.

## Purpose

Provide a repeatable standard for implementing frontend features so generated UI is production-ready: typed end to end, accessible, performant, and designed with a deliberate point of view rather than generic scaffolding.

## When to use

Use when building or changing any user-facing interface: new screens, reusable components, forms, dashboards, client-side state, routing, or API integration on the client. For deep visual direction on a greenfield design, also consult the project's `DESIGN.md` if one exists — it overrides the design defaults below. For reviewing existing UI, use the `frontend-review` skill; for verifying behavior in a real browser, use `webapp-testing`.

## Requirements

Assume this stack unless the project specifies otherwise:

- **React 18+** with function components and hooks (no class components).
- **TypeScript** in strict mode — every component, prop, and API response typed; avoid `any`.
- **Tailwind CSS** (core utilities) or the project's existing token system. For rich claude.ai artifacts, the proven stack is React 18 + TypeScript + Vite + Tailwind + shadcn/ui.
- A server-state library (TanStack Query / SWR) — never hand-rolled `useEffect` + `fetch` for shared or cached data.
- Vite + ESLint + Prettier configured.

Before coding, confirm: framework version, styling system, state-management choice, and whether a design system already exists. Match what is there rather than introducing a parallel stack.

## Workflow

1. Clarify the brief: name the one job the screen does and who uses it.
2. Model the data first: define the TypeScript types for props and API responses. The types are the contract.
3. Compose small components: presentational leaves (typed props, no fetching) composed inside containers that own data and state. Keep components under ~150 lines.
4. Wire server state through the query layer with loading, empty, error, and success states — all four, every async surface.
5. Handle unhappy paths: skeletons, empty states with a next action, errors that say what went wrong and how to recover.
6. Make it accessible (see checklist).
7. Verify: render in the browser, check keyboard navigation, run the type-checker and linter, and test at mobile width before declaring done.

## Component and state patterns

- Separate presentational from container components; presentational stays reusable and testable.
- Derive, don't duplicate, state: compute values from existing state/props during render instead of storing and syncing them.
- Lift state only as far as needed; reach for global state (Zustand/Context) only for genuinely app-wide data (auth, theme).
- Distinguish **server state** (owned by the backend → query library, with cache invalidation on mutations) from **client state** (UI-only → local `useState`/`useReducer`). Never mirror server data into client state.
- List keys are stable IDs, never array indices.
- Apply `useMemo`/`useCallback` only where referential equality or cost measurably matters, not reflexively.

## Accessibility checklist (the quality floor)

- Semantic HTML first (`button`, `nav`, `main`) before `div` + ARIA.
- Keyboard-reachable interactions with a **visible focus indicator**.
- Labels on inputs; `aria-label` on icon-only buttons.
- Meaningful `alt` text (or `alt=""` if decorative).
- Color is never the only signal; contrast meets WCAG AA.
- Respect `prefers-reduced-motion`.

## Performance practices

- Route-level code-splitting with `React.lazy` + `Suspense`.
- Lazy-load and size below-the-fold images to prevent layout shift.
- Virtualize long lists; memoize expensive subtrees.
- Import only what is used (per-icon imports, not whole packs).

## Design judgment (avoid "AI slop")

When the design is left open, make deliberate choices rather than defaults. Per Anthropic's frontend-design and web-artifacts-builder guidance, specifically avoid: excessive centered layouts, purple gradients, uniform rounded corners, and the Inter font as a reflex.

Plan a compact token system before building:
- **Color**: 4–6 named hex values.
- **Type**: a characterful display face used with restraint + a complementary body face (not the same families used on every project).
- **Layout**: one concept, sketched as a one-line description or ASCII wireframe.
- **Signature**: the one element this screen is remembered by; keep everything around it quiet.

Then critique the plan against the brief: if any part reads like the generic default you'd produce for any similar page, revise it and say why.

## Writing UI copy

Copy is design material. Write from the user's side of the screen: active voice, plain verbs, "Save changes" not "Submit," and the same action name through a whole flow (a "Publish" button produces a "Published" toast). Empty and error states give direction, not mood — say what happened and how to fix it.

## Anti-patterns

| Anti-pattern | Why it fails | Correct approach |
|---|---|---|
| `key={index}` on a dynamic list | React reuses the wrong DOM/state when items reorder, insert, or delete | `key={item.id}` — a stable identity |
| Mirroring server data into `useState` | Two sources of truth drift; UI shows stale data after refetch | Read from the query cache; keep server state in TanStack Query/SWR |
| `any` or `!` to silence TypeScript | Hides the real shape mismatch; the bug surfaces at runtime | Fix the type; model the actual data shape |
| Only rendering the success state | Loading/empty/error paths show blank or crash for real users | Handle all four async states on every fetch |
| Reflexive `useMemo`/`useCallback` everywhere | Adds cost and noise without measured benefit | Memoize only where referential equality or compute cost matters |
| Secrets/keys in frontend code | The bundle is public; anyone can read it | Keep secrets server-side; the client calls an API |

## Examples

**Example 1 — typed component, all async states handled**
```tsx
type User = { id: string; name: string; email: string };
const useUsers = () => useQuery({ queryKey: ['users'], queryFn: fetchUsers });

function UserList() {
  const { data, isLoading, isError } = useUsers();
  if (isLoading) return <UserListSkeleton />;
  if (isError)   return <ErrorState message="Couldn't load users. Try again." />;
  if (!data?.length) return <EmptyState action="Invite your first user" />;
  return <ul>{data.map((u) => <UserRow key={u.id} user={u} />)}</ul>;
}
```
Rationale: types define the contract, server state goes through the query layer, all four states are handled, key is a stable id.

**Example 2 — derived vs. stored state**
For "show the count of selected items," derive `selected.length` during render. Do not keep a separate `count` state synced with `useEffect` — that is a class of bugs with no benefit.

## Definition of Done

- [ ] Strict TypeScript; no `any`, no `!` to silence the compiler.
- [ ] Loading, empty, error, and success states handled on every async surface.
- [ ] Server state via query layer; no server data mirrored into client state.
- [ ] List keys are stable IDs.
- [ ] Accessibility floor met (semantic HTML, keyboard + visible focus, labels, contrast, reduced motion).
- [ ] Design choices are deliberate, not templated defaults.
- [ ] `tsc` and the linter pass; verified at mobile width in the browser.

## Sources adapted and merged

- Anthropic official `frontend-design` skill — https://github.com/anthropics/skills/tree/main/skills/frontend-design (design philosophy, anti-slop calibration, token-system process).
- Anthropic official `web-artifacts-builder` skill — https://github.com/anthropics/skills/tree/main/skills/web-artifacts-builder (React 18 + Vite + Tailwind + shadcn/ui stack, anti-slop specifics).
- Component/state/accessibility/performance guidance synthesized from mainstream React + a11y (WCAG) practice.
