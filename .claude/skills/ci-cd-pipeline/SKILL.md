---
name: ci-cd-pipeline
description: Builds production CI/CD pipelines with GitHub Actions, covering lint/type/test gating, build-once-and-promote artifacts, container registries, layer and dependency caching, environment-scoped secrets, manual approval for production, branch protection, and post-deploy smoke verification. This skill should be used whenever a user sets up continuous integration or deployment, writes GitHub Actions workflows, automates build/test/deploy, configures release gating, or works on a deployment pipeline — even if "CI/CD" is not stated explicitly.
---

# CI/CD Pipeline

Build once, test hard, and promote the same artifact to every environment. A pipeline's job is to make the path to production fast, repeatable, and impossible to bypass — not to rebuild a different image for prod than the one you tested.

> **Project note (SmartPaperCheck):** deploys are handled by Railway (backend) and Vercel (frontend) on push, so CI here is a **quality gate**, not a deploy pipeline: GitHub Actions running backend lint + type + `pytest`, and frontend build + lint, on PRs to protected branches. Let Railway/Vercel own the actual deploy unless you deliberately move it into Actions.

## Purpose

Provide a repeatable standard for CI/CD so generated pipelines gate quality automatically, ship the exact artifact that passed tests, manage secrets safely, and make deploys traceable and reversible.

## When to use

Use when setting up continuous integration or deployment, authoring GitHub Actions (or comparable) workflows, automating build/test/deploy, gating releases, or wiring a registry. Pairs with `docker-devops` (which defines the image this pipeline builds and ships) and `webapp-testing` / `fastapi-backend` testing (the gates this pipeline runs).

## Requirements

- GitHub Actions (patterns transfer to GitLab CI / CircleCI).
- A container registry (GitHub Container Registry / GHCR, or ECR/GAR).
- A branch strategy: `main` → production, a staging branch/environment, short-lived feature branches.
- Repository and environment **secrets** configured in the platform — never in the repo.

Before writing a workflow, confirm: what "tests pass" means for this repo, where it deploys (host/orchestrator/PaaS), and which environments need manual approval.

## Pipeline stages

Model the pipeline as discrete jobs wired with `needs:`, so a failure stops the line early:

1. **Lint & type-check** — fast static gates; fail in seconds, not minutes.
2. **Test** — unit + integration; the real quality gate.
3. **Build & push** — build the container once, tag it with the immutable git SHA, push to the registry. Runs only after tests pass.
4. **Deploy** — pull that exact SHA-tagged image and release it. Production is gated behind environment protection (manual approval).
5. **Smoke-verify** — after deploy, hit the health endpoint; fail the pipeline (and roll back) if it doesn't return healthy.

## Build once, promote the artifact

The image tested in CI is the image that reaches production. Tag by git SHA, push once, and reference that tag through staging and prod. Never rebuild for production — a rebuild can pull newer base layers or dependencies and ship something you never tested.

## Caching

- Cache language dependencies (`actions/cache` keyed on the lockfile hash) so installs are near-instant on a cache hit.
- Cache Docker layers with Buildx `cache-from`/`cache-to: type=gha` so unchanged layers aren't rebuilt.
- Key caches on content (lockfile, Dockerfile) so they invalidate correctly when inputs change.

## Secrets

- Store secrets as GitHub repository or **environment-scoped** secrets; reference them as `${{ secrets.NAME }}`.
- Pass secrets only through the `env:` of the step that needs them — never `echo` a secret or put it on a command line (it lands in logs).
- Scope prod secrets to the production `environment` so PRs and staging can't read them.
- Rotate secrets and use least-privilege tokens (`GITHUB_TOKEN` with only the permissions the job needs).

## Gating and protection

- Protect `main`: require the CI status checks to pass and at least one review; disallow direct pushes.
- Put production behind a GitHub **Environment** with required reviewers, so deploy waits for a human approval.
- Run a dependency vulnerability check on PRs (`actions/dependency-review-action`) and scan the built image (Trivy) before push.

## Worked example — build-once, gated deploy

```yaml
name: ci-cd
on:
  push: { branches: [main] }
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12", cache: pip }
      - run: pip install -r requirements.txt
      - run: ruff check . && mypy app        # lint + types
      - run: pytest                          # the quality gate

  build-and-push:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    permissions: { contents: read, packages: write }
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    environment: production          # requires manual approval
    steps:
      - name: Release the tested image
        env:
          DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
        run: ./deploy.sh ghcr.io/${{ github.repository }}:${{ github.sha }}
      - name: Smoke test
        run: curl -fsS https://api.example.com/health
```
Rationale: tests gate everything; the image is built once and tagged by SHA; prod waits for approval; the same SHA is deployed and then health-checked.

## Anti-patterns

| Anti-pattern | Why it fails | Correct approach |
|---|---|---|
| Building the image in the deploy job | Prod runs an artifact that was never tested | Build once after tests; deploy that SHA-tagged image |
| `echo ${{ secrets.X }}` / secret on a CLI arg | Secrets leak into build logs | Pass via `env:`; never print them |
| One mega-job doing everything | A late failure wastes the whole run; no caching reuse | Separate jobs wired with `needs:` |
| Tagging only `:latest` | Deploys aren't traceable; rollback is guesswork | Tag by git SHA (and/or semver) |
| No branch protection / required checks | Untested code reaches `main` | Require passing checks + review; block direct push |
| Auto-deploying straight to prod | No human gate on a bad release | Gate prod behind an Environment with required reviewers |

## Definition of Done

- [ ] Separate jobs (lint/type → test → build → deploy) wired with `needs:`.
- [ ] Image built once, tagged by git SHA, pushed to the registry; same tag deployed.
- [ ] Dependency and Docker-layer caching configured and keyed on content.
- [ ] Secrets via environment-scoped GitHub secrets; never echoed or on a command line.
- [ ] `main` protected (required checks + review); production behind manual approval.
- [ ] Dependency review on PRs and image CVE scan before push.
- [ ] Post-deploy smoke check hits the health endpoint and fails the run if unhealthy.

## Sources adapted and merged

- GitHub Actions official documentation — https://docs.github.com/actions (workflow syntax, `needs`, caching, environments, OIDC/secrets).
- `docker/build-push-action` and Buildx GitHub Actions cache (`type=gha`) — https://github.com/docker/build-push-action
- DevOps pipeline patterns from `rohitg00/awesome-claude-code-toolkit` and `Ashfaqbs/software-dev-ai-claude-toolkit`. Note: Anthropic's official repo has no CI/CD skill; content is community-sourced plus GitHub Actions and supply-chain best practice (build-once-promote, least-privilege tokens, image scanning).
