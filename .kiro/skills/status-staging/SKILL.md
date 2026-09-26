---
name: status-staging
description: >-
  Reports the health of the Cetana Labs staging environment. PLACEHOLDER — staging is not yet provisioned; target is GCP (backend + frontend) with optional Vercel for the frontend, pending the repo transfer to the org account. Use when the user runs /status-staging.
---

# Skill: Staging Status (`/status-staging`) — PLACEHOLDER

## Status: Not yet provisioned

Staging does **not exist yet**. This skill is a documented placeholder so the command vocabulary is standardized ahead of the environment being built.

## Planned Staging Architecture
- **Primary target: GCP** — both backend (PocketBase, single-binary + persistent volume, e.g. Cloud Run + a mounted disk / GCS-backed SQLite) and the frontend.
- **Optional quick-win: Vercel** — for fast frontend preview deploys.
- **Dependency:** provisioning begins after the repository is **transferred to the org account** (enables org-level Pages/Actions/secrets and branch protection per `RFC-LAB-000-004` §10a).

## Intended Behavior (once staging exists)
When implemented, `/status-staging` will:
1. Probe the staging backend health endpoint (GCP PocketBase URL) and report HTTP status + version.
2. Probe the staging frontend (GCP or Vercel URL) and report reachability.
3. Report the last deploy SHA/time and whether it matches `main`.

## Trigger Patterns
- `/status-staging`

## Current Response
State clearly: "Staging is not provisioned yet — planned on GCP (backend + frontend), optional Vercel for frontend, pending the org-account transfer." Do not fabricate a status.
