# Automate Staging Deploy — Make `done` Observably Live — Requirements

| Property | Value |
| :--- | :--- |
| **Spec ID** | `automate-staging-deploy` |
| **Feature** | Encode `main` = the single reference environment: a merge deploys **both** tiers. Add **backend CI deploy** (GitHub Actions → Railway, path-filtered) to match the frontend's existing Vercel auto-deploy; add a **`/deploy-adhoc`** developer tool for on-demand deploys to throwaway/other instances. |
| **Backlog** | `TSK-059` (`BK-021`, SPRINT-10) |
| **Status** | 🟡 Proposed (contract authored on Kiro Web; execution on Kiro IDE) |
| **RFCs / Journal** | Decision Journal **Entry 014** (D49–D52 — the scope boundary + this work); `RFC-LAB-000-012` (deploy ops — now **reference ops guidance**); `RFC-LAB-000-011` (Vercel + Railway); `RFC-LAB-000-007` (Makefile/env conventions); `RFC-LAB-000-004` (branch → PR → gate) |
| **Executor role** | Delegated-agent / onboarded-dev |

---

## 1. Introduction

The AIDLC lifecycle ends at **`done` = merged to `main` = live** on the project's **single reference environment** (Decision Journal Entry 014, D49). `done` is *pragmatic* (D50): the contract is the **gated merge**; the auto-deploy is a *consequence* that makes `done` observable, and a deploy hiccup is an **ops** alert, never a lifecycle failure. Multi-environment topology / promotion / prod hardening is **out of scope** (DevOps) — no promotion pipeline, no prod tier (D51/D52).

Today the model is only half-true: **merging to `main` auto-deploys the frontend** (Vercel Git integration is connected to `agni-eialarasu/cetana-labs`), but the **backend PocketBase on Railway has no CI-triggered deploy** — it is deployed manually via `scripts/deploy.sh`. This Spec closes that asymmetry (the *minimal bridge*, explicitly the edge of scope) and adds a clearly-separated on-demand developer tool.

**Two deliberately-separated paths (Entry 014, D51):**
1. **Auto-staging (the pipeline):** push to `main` → both tiers deploy to the single reference environment. Gate = PR review + required CI checks (the merge is the deploy gate).
2. **On-demand (`/deploy-adhoc`, a dev tool):** a human deploys to *any* instance (throwaway/other) for ad-hoc testing — **not** a lifecycle stage, not the staging pipeline.

## 0. Preconditions (preflight — verify BEFORE any change; enforced by `tasks.md` T0)

- **P1 — Surface:** Kiro **IDE / local** for the workflow + skill + Makefile edits and quality gates. A live verification of the CI deploy needs a **`RAILWAY_TOKEN`** in **GitHub repo secrets** (one-time [HUMAN] console step) and the Railway service linkable via token.
- **P2 — Toolchain:** Node/pnpm; Railway/Vercel CLIs present (per `RFC-LAB-000-012`); existing `scripts/deploy.sh`, `scripts/verify-bundle.sh`, `railway.json`, `Makefile`.
- **P3 — Branch:** `feat/automate-staging-deploy` off up-to-date `main`; clean tree; not `main`/`master`.
- **P4 — Merge-first:** this Spec merged to `main` before `/spec-run`.
- **P5 — Baseline green:** the three validators + `pnpm --dir app/web check && build`; existing `ci-validate.yml` jobs pass.
- **P6 — Secrets discipline (non-negotiable):** no secret in git at any stage. `RAILWAY_TOKEN` lives ONLY in GitHub Actions secrets; `.env.*` stay gitignored.
- **P7 — Non-destructive:** the new backend-deploy workflow targets the single reference (staging) Railway service already in use; it does NOT create prod infra (that is out-of-scope `BK-019`). The `bk018-throwaway` service is retained for `/deploy-adhoc` testing (user decision).

## 2. Current-state facts (of record — verified)

- **Frontend auto-deploy exists:** Vercel Git integration is connected to the repo (dashboard-confirmed) with `deployment_status` + `repository_dispatch` events on → push to `main` builds/deploys the SPA. `app/web/vercel.json` pins the build (`framework:null`, `outputDirectory: build`).
- **Backend has no CI deploy:** the only workflows are `ci-validate.yml` (validators + web build — the required checks) and two crons (`lead-ping-cron.yml`, `project-status-cron.yml`). None deploy (grep-confirmed: zero `railway`/`deploy`/`vercel` deploy steps).
- **On-demand scaffold exists:** `scripts/deploy.sh` (`deploy-backend` = `railway up` from `app/pocketbase/`; `deploy-frontend` = build → `verify-bundle` → `vercel deploy`; `all`), invoked by `make deploy-staging`. Reads `.env.staging` (gitignored). Contains no secrets (CLI-token auth).
- **`railway.json`** pins `builder: DOCKERFILE` / `dockerfilePath: Containerfile` and `restartPolicyType: ON_FAILURE` — reused by the CI deploy.
- **Stale placeholders:** `make validate-staging` and the `status-staging`/`validate-staging` skills still say "target GCP … pending org transfer" — contradicts the Railway/Vercel reality (RFC-011 amended to Railway/Vercel, Entry 010).
- **Naming conflation:** `make deploy-staging` currently means "deploy to whatever `.env.staging` points at" — which blurs "the staging pipeline" with "on-demand to anywhere." This Spec disambiguates.

## 3. Requirements (EARS acceptance criteria = Definition of Done)

### R1 — Backend CI deploy on merge (the gap; path-filtered)
- **R1.1** The system SHALL add a GitHub Actions workflow (e.g. `.github/workflows/deploy-backend.yml`) that triggers `on: push: branches: [main]` **path-filtered to `app/pocketbase/**`** (and the workflow file itself), so the Railway PocketBase deploys only when the backend actually changes.
- **R1.2** The workflow SHALL deploy via the **Railway CLI** using a **`RAILWAY_TOKEN`** read from **GitHub Actions secrets** (`secrets.RAILWAY_TOKEN`) — never hard-coded, never in the repo. It SHALL target the existing single reference (staging) Railway service.
- **R1.3** The deploy SHALL reuse the repo-committed `app/pocketbase/railway.json` builder pin (no Railpack auto-detect); the deploy context SHALL be `app/pocketbase/` (sidestepping the Root-Directory doubling).
- **R1.4** WHEN the deploy step fails, the workflow SHALL fail loudly (red check + logs) as an **ops alert** — this SHALL NOT retroactively block or revert the already-merged lifecycle work (`done` = the merge, D50). No auto-rollback in scope.

### R2 — Symmetry: a merge deploys both tiers
- **R2.1** The model SHALL be documented such that a merge to `main` deploys **frontend (Vercel, existing) and backend (R1, new)** to the single reference environment — the two tiers are symmetric.
- **R2.2** The Spec SHALL NOT alter or gate the existing Vercel Git integration (it already satisfies the frontend half); it only adds the backend half and documents the whole.

### R3 — `/deploy-adhoc` — on-demand deploy to any instance (a dev tool, not a stage)
- **R3.1** The system SHALL provide an on-demand deploy path that targets an **arbitrary instance** (throwaway/other), parameterized by an env file — e.g. `make deploy-adhoc ENV=<file>` delegating to `scripts/deploy.sh` — so it does not require or touch the staging pipeline.
- **R3.2** A **`.kiro/skills/deploy-adhoc/SKILL.md`** slash skill SHALL wrap this path, clearly framed as a **developer testing tool** (explicitly NOT a lifecycle phase, NOT "release"), including the one-time [HUMAN] checklist reference and the `verify-bundle` guard for any frontend it deploys.
- **R3.3** The on-demand path SHALL retain the existing `verify-bundle` artifact assertion for frontend deploys (the BK-018 false-negative guard) and SHALL read config from a gitignored env file (no secrets committed).

### R4 — Makefile disambiguation (staging pipeline vs. ad-hoc)
- **R4.1** The Makefile SHALL make the distinction explicit: the **auto-staging pipeline** (merge-driven, no manual target needed for the normal path) vs. the **`deploy-adhoc`** target (manual, any instance). The current `deploy-staging` target SHALL be reconciled (renamed/aliased/clarified) so it no longer implies "the staging pipeline is a manual make target."
- **R4.2** `make help` and target comments SHALL reflect the two-path model and reference Journal Entry 014.

### R5 — Refresh stale staging placeholders
- **R5.1** `make validate-staging` and the `status-staging` / `validate-staging` skills SHALL be updated to drop the obsolete "GCP … pending org transfer" text and reflect the **Railway (backend) + Vercel (frontend)** single-reference reality — or be explicitly retired/demoted if redundant, with a note.

### R6 — Docs: the model + the boundary
- **R6.1** `developer-guide.md` §9A SHALL document the **`main` = single reference environment** model: merge deploys both tiers; the PR gate is the deploy gate; `done` = live (pragmatic, D50); the two paths (auto-staging vs `/deploy-adhoc`); and the **explicit scope boundary** (no promotion pipeline / prod tier — ops, out of scope).
- **R6.2** `RFC-LAB-000-012` SHALL be reframed (header note / status) as **optional reference ops guidance**, not part of the lifecycle contract (Entry 014, D52). No deletion — a scoping note.

### R7 — No regression / secrets discipline / gates green
- **R7.1** No secret SHALL appear in the repo or any committed file; `RAILWAY_TOKEN` exists ONLY as a GitHub Actions secret; `.env.*` stay gitignored (verified).
- **R7.2** `pnpm --dir app/web check && build`, `make validate-local`, `generate_status_json.py --check`, and the existing `ci-validate.yml` jobs SHALL remain green. The new workflow SHALL NOT interfere with the required status checks that gate `main`.
- **R7.3** All lifecycle/ops work SHALL land via branch → PR → gate (`RFC-LAB-000-004`); nothing ad-hoc to `main`.

## 4. Out of scope (scope honesty — Entry 014)
- **Dedicated prod infrastructure** (prod Railway/Vercel, prod OAuth app, custom domain, backup/promotion discipline) — that is `BK-019`, reclassified **out-of-scope ops**.
- **Any staging→prod promotion pipeline** — deliberately not built (D51). One automated environment only.
- **Auto-rollback / blue-green / canary** — ops concerns, not in this bridge.
- **Branch-protection configuration itself** is a one-time [HUMAN] GitHub setting (the gate); this Spec assumes/【documents】it, does not script it.

## 4b. Human Verification Plan (emitted by `/spec-run`; recorded by `/verification-done`)
Verified on the IDE + the single reference (staging) Railway/Vercel + a throwaway instance:
- **V1 — backend CI deploy fires on backend change:** a merge to `main` touching `app/pocketbase/**` triggers `deploy-backend.yml` and the Railway service redeploys (deploy log / new deployment id).
- **V2 — path filter works:** a merge touching only docs/frontend does **NOT** trigger the backend deploy (workflow skipped).
- **V3 — token from secrets, no secret in repo:** the workflow authenticates via `secrets.RAILWAY_TOKEN`; `git grep` finds no token/secret anywhere in the tree.
- **V4 — deploy-failure is an ops alert, not a lifecycle failure:** a forced deploy failure yields a red workflow + logs, but the merge/`done` state is unaffected (no revert).
- **V5 — `/deploy-adhoc` hits an arbitrary instance:** `make deploy-adhoc ENV=.env.throwaway` (or the skill) deploys to the throwaway (not staging), with `verify-bundle` asserting the throwaway URL for any frontend.
- **V6 — both-tiers symmetry documented + true:** a backend+frontend change merged to `main` results in both the Vercel deploy and the Railway deploy.
- **V7 — placeholders refreshed:** `make validate-staging` / the staging skills no longer reference GCP; reflect Railway/Vercel.
- **V8 — gates green + docs/RFC reframe present:** `ci-validate.yml` jobs green; `developer-guide` §9A + RFC-012 reframe note landed.
