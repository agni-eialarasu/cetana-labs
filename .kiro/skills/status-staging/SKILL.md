---
name: status-staging
description: >-
  Reports the health of the Cetana Labs staging environment — the single reference env that a merge to main auto-deploys (Railway backend + Vercel frontend). Probes backend/frontend reachability and deploy freshness vs main. Use when the user runs /status-staging.
---

# Skill: Staging Status (`/status-staging`)

## What "staging" is (Decision Journal Entry 014, RFC-LAB-000-011)

Staging is the **single reference environment** — one env, auto-deployed on every merge to
`main`:
- **Backend:** PocketBase → **Railway** (`.github/workflows/deploy-backend.yml`,
  path-filtered to `app/pocketbase/**`).
- **Frontend:** SvelteKit → **Vercel** (Git integration).

No GCP target, no prod tier, no promotion pipeline (out-of-scope ops, `BK-019`).

## Intended Behavior
`/status-staging` reports the live env health (URLs from `.env.staging`):
1. Probe the **Railway** backend health endpoint (`<PB_URL>/api/health`) — HTTP status + version.
2. Probe the **Vercel** frontend URL — reachability.
3. Report the last deploy SHA/time and whether it matches `main`.

## Trigger Patterns
- `/status-staging`

## Response guidance
Probe the real Railway/Vercel endpoints and report actual status. If `.env.staging` or a URL
is missing, say so (point to `.env.staging.example`) — do not fabricate a status.
