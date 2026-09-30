---
name: validate-staging
description: >-
  Validates the Cetana Labs staging environment — the single reference env that a merge to main auto-deploys (Railway backend + Vercel frontend). Smoke-tests backend health, frontend load, and deploy freshness vs main. Use when the user runs /validate-staging.
---

# Skill: Staging Validation (`/validate-staging`)

## What "staging" is (Decision Journal Entry 014, RFC-LAB-000-011)

Staging is the **single reference environment** — there is exactly one, and **a merge to
`main` auto-deploys both tiers to it**:
- **Backend:** PocketBase → **Railway** (via `.github/workflows/deploy-backend.yml`,
  path-filtered to `app/pocketbase/**`).
- **Frontend:** SvelteKit → **Vercel** (via the Vercel Git integration).

There is no separate GCP target and no promotion/prod pipeline — that is out-of-scope ops
(`BK-019`). `done` = the gated merge, made observably live on this env.

## Intended Behavior
`/validate-staging` smoke-tests the live single reference env (reads URLs from `.env.staging`):
1. Probe the **Railway** backend health endpoint (`<PB_URL>/api/health`) — report HTTP status + version.
2. Probe the **Vercel** frontend URL — report reachability and that it loads.
3. Do a data read (e.g. `projects` list) and confirm expected records come back.
4. Report the last deploy SHA/time and whether it matches `main` (no drift).
5. Check API-rule / RBAC behavior (`RFC-LAB-000-006`).

## Trigger Patterns
- `/validate-staging`

## Response guidance
Probe the real Railway/Vercel endpoints from `.env.staging`; report actual results. If the
env file or a URL is missing, say so and point to `.env.staging.example` — do not fabricate
results. For a one-off deploy to a *different* instance (not staging), that is `/deploy-adhoc`.

## Scope boundary (RFC-LAB-000-007 §2.5)
This validates *remote staging health* only. Local environment readiness → `/env-doctor`;
local work correctness → `/validate-local`.
