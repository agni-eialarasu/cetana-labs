---
name: deploy-adhoc
description: >-
  On-demand developer deploy to an ARBITRARY instance (throwaway/other), parameterized by an env file — a testing tool, NOT a lifecycle stage and NOT "release." Wraps `just deploy-adhoc ENV=<file>` (delegates to scripts/deploy.sh). Use when the user runs /deploy-adhoc or asks to deploy to a throwaway/scratch instance for testing. The normal staging deploy is automatic on merge to main — this is separate.
---

# Skill: Ad-hoc Deploy (`/deploy-adhoc`) — developer testing tool

## What this IS (and is NOT)

This deploys the backend (PocketBase → Railway) and/or frontend (SvelteKit → Vercel)
to an **arbitrary instance you point it at** via an env file — a **throwaway or other
scratch instance** for hands-on testing.

- ✅ **IS:** a developer testing tool for on-demand deploys to any instance.
- ❌ **IS NOT** a lifecycle phase, NOT "release," NOT "the staging pipeline."

> **The staging pipeline is the *merge*.** Merging to `main` auto-deploys BOTH tiers
> (frontend via Vercel Git integration; backend via `.github/workflows/deploy-backend.yml`)
> to the single reference environment. That is the real staging deploy. This skill is
> **ad-hoc only** — it never touches that pipeline. (Decision Journal **Entry 014**, D51.)

## Trigger Patterns
- `/deploy-adhoc` (defaults to a full `all` deploy of the target env)
- "deploy to the throwaway instance", "push a scratch build to `<env>` for testing"

## Usage

```bash
just deploy-adhoc ENV=<env-file>            # backend + frontend to whatever <env-file> points at
just deploy-adhoc ENV=<env-file> WHAT=deploy-backend    # backend only
just deploy-adhoc ENV=<env-file> WHAT=deploy-frontend   # frontend only (build + verify-bundle first)
```

- `ENV=<file>` — a **gitignored** env file (e.g. `.env.throwaway`) describing the target
  instance: `PB_URL`, `VITE_PB_URL`, optional `FORBIDDEN_PB_URL`. Copy the template:
  `cp .env.staging.example .env.throwaway` then edit (it is gitignored — NEVER commit it).
- `WHAT=` — `all` (default) · `deploy-backend` · `deploy-frontend`.

The recipe sets `ENV_FILE=<ENV>` and calls `scripts/deploy.sh <WHAT>` — the same
script the staging CLI path uses, just aimed at a different env file.

## Guarantees & discipline (carried over from scripts/deploy.sh)

- **`verify-bundle` guard (R3.3 / BK-018):** any frontend deploy first builds and then
  asserts the built bundle bakes in the **expected** backend URL (and, if set, that a
  `FORBIDDEN_PB_URL` is absent) before Vercel sees it. A bundle baked against the wrong
  backend is never deployed.
- **Secrets discipline (P6/R7.1):** no credentials live in this repo. Railway/Vercel auth
  comes from the CLIs' own stored tokens (`railway login` / `vercel login`, one-time per
  machine); the env file holds only URLs and is gitignored. Never commit an `.env.*`.
- **One-time [HUMAN] setup:** run `scripts/deploy.sh checklist` for the irreducibly-manual
  steps (CLI login, Railway volume at `/pb/pb_data`, GitHub OAuth app callback, Vercel env).

## Boundary reminder
If the intent is "make the merged work live," that already happens automatically on merge
to `main` — do NOT use this. Use `/deploy-adhoc` only for throwaway/other instances.
