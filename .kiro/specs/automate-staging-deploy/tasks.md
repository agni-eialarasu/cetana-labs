# Automate Staging Deploy — Tasks (`/spec-run` build plan)

## Execution header
- **Kickoff:** `/spec-run automate-staging-deploy`
- **Surface:** Kiro IDE (+ single reference Railway/Vercel + a throwaway instance for verification)
- **Branch to create:** `feat/automate-staging-deploy` (off up-to-date `main`)
- **EARS target (DoD):** `requirements.md` §3 R1–R7; verify against §4b V1–V8 (V1/V3/V4 headline)
- **One-time [HUMAN] prereq:** `RAILWAY_TOKEN` in GitHub Actions secrets; branch protection / required checks on `main` (the gate)
- **Merge-first:** this Spec must be on `main` before kickoff (satisfied by `/plan-done`)

> Ordered plan for `/spec-run` (Build) on **Kiro IDE**. Executes `tasks.md`, self-validates against the `requirements.md` EARS DoD, opens a PR into `main`, emits the Human Verification Plan (§4b), and **STOPs in `IN_VERIFICATION`**. **Never merges.**

- [ ] **T0 — Preflight (gate — STOP on any ❌)**
  - Confirm P1–P7: on `feat/automate-staging-deploy` off up-to-date `main`, clean tree; toolchain + existing `deploy.sh`/`railway.json`/Makefile present; baseline green (`ci-validate.yml` jobs, `pnpm check && build`); `RAILWAY_TOKEN` secret exists (or note it as the one blocking [HUMAN] step for V1).

- [ ] **T1 — Backend CI deploy workflow (R1, R2) — the priority**
  - Add `.github/workflows/deploy-backend.yml`: `on: push: branches:[main]`, `paths: ['app/pocketbase/**', '.github/workflows/deploy-backend.yml']`; `concurrency` guard; deploy via Railway CLI using `secrets.RAILWAY_TOKEN`, context `app/pocketbase/` (reuse `railway.json` builder pin).
  - Verify the exact non-interactive `railway up` flags + service selection against current Railway CLI docs (OQ-1). Deploy failure = red check only, no rollback (R1.4).

- [ ] **T2 — `/deploy-adhoc` path (R3)**
  - Add `make deploy-adhoc ENV=<file>` delegating to `scripts/deploy.sh` via `ENV_FILE` (already honored). Add `.kiro/skills/deploy-adhoc/SKILL.md` framing it as a **developer testing tool** (NOT a lifecycle stage / "release"); include the one-time checklist ref, `verify-bundle` guard, secrets-discipline note, and the "staging = the merge; this is ad-hoc only" boundary.

- [ ] **T3 — Makefile disambiguation (R4)**
  - Reconcile `deploy-staging` so it no longer implies "the staging pipeline is a manual target" (lean: keep as documented manual re-deploy/override; add `deploy-adhoc`). Update `make help` + comments to the two-path model, referencing Journal Entry 014.

- [ ] **T4 — Refresh stale staging placeholders (R5)**
  - Update `make validate-staging` + `status-staging`/`validate-staging` skills: drop "GCP … pending org transfer"; reflect Railway (backend) + Vercel (frontend). Demote/retire with a note if redundant.

- [ ] **T5 — Docs + RFC-012 reframe (R6)**
  - `developer-guide.md` §9A: add "The Deployment Model" (`main`=single reference env; merge deploys both tiers; PR gate = deploy gate; `done`=live pragmatic; two paths; explicit ops boundary). Add the RFC-LAB-000-012 header/status note = **reference ops guidance** (append; don't rewrite decisions).

- [ ] **T6 — Governance lockstep (Pillar 2)**
  - Add the `CHANGELOG.md` `[Unreleased]` entry for `TSK-059`/`BK-021`. Confirm `SPRINT_TRACKER.md` `TSK-059` row is coherent (→ `👀 In Review` on the PR; `✅ Done` in the post-merge tidy). Backlog `BK-021`/`BK-019` rows already updated in the plan session.

- [ ] **T7 — Quality gates + no-regression (R7)**
  - `pnpm --dir app/web check && build`; `make validate-local`; `generate_status_json.py --check`; `git grep` clean of any token/secret. Confirm the new workflow is additive and does NOT become/break a required check.

- [ ] **T8 — Commit, open PR, emit Human Verification Plan, STOP**
  - Open PR into `main` via `gh api`; CI green; emit the §4b plan (V1–V8; V1/V3/V4 headline). STOP in `IN_VERIFICATION`. **Never merge.**

- [ ] **T9 — After human verification passes: `/verification-done`**
  - Human runs V1–V8 (esp. V1 backend deploy fires on backend change, V2 path filter skips non-backend, V3 no secret in repo, V4 deploy-failure ≠ lifecycle failure, V5 `/deploy-adhoc` hits throwaway). Fixes ride the same PR (Single-PR rule). On pass → `/verification-done` → `IN_REVIEW` → `/review-pr`.
