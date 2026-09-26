---
name: validate-staging
description: >-
  Validates a Cetana Labs staging deployment (smoke tests + parity checks). PLACEHOLDER — staging is not yet provisioned; target is GCP (backend + frontend) with optional Vercel for the frontend, pending the repo transfer to the org account. Use when the user runs /validate-staging.
---

# Skill: Staging Validation (`/validate-staging`) — PLACEHOLDER

## Status: Not yet provisioned

Staging does **not exist yet**. This is a documented placeholder standardizing the command ahead of the environment.

## Planned Staging Architecture
- **Primary: GCP** for backend (PocketBase) and frontend.
- **Optional: Vercel** for frontend preview deploys.
- **Dependency:** begins after the repo transfers to the **org account**.

## Intended Behavior (once staging exists)
When implemented, `/validate-staging` will:
1. Run `/validate-local` equivalents against the staging build artifact.
2. Smoke-test staging endpoints: backend health, frontend load, and a data read (e.g. `projects` list) returns expected records.
3. Verify staging is deployed from the current `main` SHA (no drift).
4. Check API-rule / RBAC behavior once Phase 3 (`RFC-LAB-000-006`) lands.

## Trigger Patterns
- `/validate-staging`

## Current Response
State clearly that staging validation is unavailable until the GCP (and/or Vercel) staging environment is provisioned post org-transfer. Do not fabricate results.
