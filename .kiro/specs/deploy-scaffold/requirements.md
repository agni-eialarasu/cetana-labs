# Deploy Scaffold — Requirements

| Property | Value |
| :--- | :--- |
| **Spec ID** | `deploy-scaffold` |
| **Feature** | Implement `RFC-LAB-000-012` — CLI-first deploy scaffold, artifact-verification helper, casual→qualified runbook, + the `status.json` date-drift fix |
| **Backlog** | `TSK-056` (`BK-017`), incl. `BK-020` (SPRINT-10) |
| **Status** | 🟡 Proposed (contract authored on Kiro Web; execution on Kiro IDE) |
| **RFCs** | `RFC-LAB-000-012` (deploy operations — decision of record), `RFC-LAB-000-011` (Vercel + Railway), `RFC-LAB-000-007` (Makefile/env conventions) |
| **Executor role** | Delegated-agent / onboarded-dev |

---

## 1. Introduction

`RFC-LAB-000-012` decided *how we operate deploys* (CLI-first, casual→qualified, verify-the-artifact, gated ops). This Spec **implements the scaffold** so the next deploy — and the deferred BK-018 OAuth fix — are reproducible and low-pain, and **fixes the recurring `status.json` CI drift** (`BK-020`) that has blocked 5 unrelated PRs.

**This is DX plumbing, not a product feature.** It bundles three loosely-coupled deliverables (all "deploy/DX" per RFC-012 §7): (A) the CLI deploy scaffold, (B) the build-artifact verification helper, (C) the status-drift fix. They're independent enough to land/verify separately if needed.

## 0. Preconditions (preflight — verify BEFORE any change; enforced by `tasks.md` T0)

- **P1 — Surface:** Kiro **IDE / local**. `/env-doctor` IDE-ready.
- **P2 — Toolchain:** Python 3.11+ (status fix + validators), Node/pnpm (build). Railway/Vercel **CLIs installed** for the scaffold parts that invoke them; if absent, the scaffold is authored but its live invocation is a [HUMAN] one-time install (STOP, don't fabricate).
- **P3 — Branch:** `feat/deploy-scaffold` off up-to-date `main`; clean tree; not `main`/`master`.
- **P4 — Merge-first:** this Spec merged to `main` before `/spec-run`.
- **P5 — Baseline green:** three validators + `pnpm --dir app/web check && build` pass before changes.

## 2. Current-state facts (of record — verified)

- **Exists (spike down-payment):** `app/web/vercel.json` (framework=null, `outputDirectory: build`), `.env.staging.example`, `.vercel`/`.env.staging` gitignored.
- **Missing:** `railway.json`, any `make` deploy targets, an artifact-assertion helper.
- **`status.json` drift (BK-020):** `generate_status_json.py --check` does a **full-string compare** (line ~68) of the whole file against a freshly-`build()`-ed payload; `build()` **recomputes `days_ago` from today's date** (line ~48) — so the committed file goes stale purely by time passing. `days_ago` is **stored** in `data/status.json` and consumed by the SPA.
- **CLI capability (from BK-017 assessment — re-verify against current docs at build):** Railway CLI `up`/`variables`/`domain`/`logs`/`run` scriptable; volume attach + login are one-time [HUMAN]. Vercel CLI `deploy`/`env add` scriptable.

## 3. Requirements (EARS acceptance criteria = Definition of Done)

### R1 — Railway deploy config (`railway.json`)
- **R1.1** The system SHALL add a `railway.json` pinning the **builder to the `Containerfile`** (`app/pocketbase/Containerfile`) so Railway does not auto-detect/Railpack the build (the papercut the spike hit).
- **R1.2** It SHALL document (comment/README) the persistent-volume mount at `/pb/pb_data` as the one-time [HUMAN] dashboard step (CLI can't attach volumes).

### R2 — CLI deploy wrapper (`make deploy-staging` → `scripts/deploy.sh`)
- **R2.1** The system SHALL add a `make deploy-staging` target delegating to `scripts/deploy.sh` (consistent with the Makefile cheat-sheet, `RFC-LAB-000-007`).
- **R2.2** The script SHALL, via the CLIs, deploy the backend (Railway) and frontend (Vercel), capture the resulting URLs, and print the **irreducibly-manual one-time checklist** (CLI login, volume attach, OAuth app) rather than pretend to automate them.
- **R2.3** It SHALL read config from `.env.staging` (gitignored); it SHALL NOT contain or commit any secret. Missing `.env.staging` ⇒ clear message + the `.env.staging.example` to copy.

### R3 — Build-artifact verification helper (`RFC-LAB-000-012` §5 — the false-negative fix)
- **R3.1** The system SHALL add a helper (script or `make` target, e.g. `make verify-bundle`) that, given an expected backend URL, **asserts the built `app/web/build/` bundle contains that `VITE_PB_URL`** and does **not** contain a specified other-backend URL — failing loudly if the baked-in config is wrong.
- **R3.2** The deploy wrapper (R2) SHALL run this assertion before declaring a frontend deploy trustworthy.

### R4 — Casual→qualified runbook in `developer-guide.md`
- **R4.1** `developer-guide.md` SHALL gain a **Deploy Operations** section documenting: the CLI-first flow (Railway/Vercel), the **casual→qualified environment lifecycle** (`RFC-LAB-000-012` §4), the artifact-verification rule (§5), and the one-time manual steps. Reusable for staging/prod/new environments.

### R5 — Fix `status.json` date-drift (`BK-020`, `RFC-LAB-000-012` §7)
- **R5.1** The system SHALL make the status-sync check **date-tolerant** so `days_ago` advancing over time no longer makes the committed file "stale". *(Leaning per RFC-012 OQ-3: stop storing `days_ago` in `data/status.json` and compute it at read-time in the SPA; alternatively, exclude `days_ago` from the `--check` comparison.)*
- **R5.2** WHEN the fix is in place, `generate_status_json.py --check` SHALL pass on a freshly-checked-out branch **regardless of how many days elapsed** since the file was last written (no manual regenerate needed for time passing alone).
- **R5.3** IF `days_ago` stops being stored, the SPA/data consumers SHALL still render correctly (compute it from `last_updated` at read-time) — no UI regression.

### R6 — No regression / secrets discipline
- **R6.1** No secret (throwaway or real) SHALL be committed; `.env.staging` stays gitignored.
- **R6.2** Local dev + the deployed staging app (M1–M5) SHALL be unaffected by these changes; existing `vercel.json` behavior preserved.

### R7 — Quality gates green
- **R7.1** `pnpm --dir app/web check && build && lint`, `make validate-local`, and — critically — `generate_status_json.py --check` SHALL pass. The status-drift fix SHALL be demonstrated (R5.2).

## 4b. Human Verification Plan (emitted by `/spec-run`; recorded by `/verification-done`)

- **V1 — status-drift fixed (the headline):** simulate time passing (or reason about the compare) → `generate_status_json.py --check` passes without a manual regenerate; confirm the SPA still shows correct "days ago". *(This is the papercut that bit 5×.)*
- **V2 — artifact helper catches a wrong bundle:** build with a deliberately wrong `VITE_PB_URL` → `make verify-bundle` **fails**; build with the right one → passes. (Proves it would've caught the BK-018 false negative.)
- **V3 — `railway.json` pins the builder:** confirm it selects the `Containerfile` (not Railpack auto-detect).
- **V4 — deploy wrapper (dry/where possible):** `make deploy-staging` runs the CLI flow, captures URLs, and prints the manual checklist; with no `.env.staging`, it errors helpfully. *(Full live deploy is [HUMAN]/CLI-login-gated — exercise what's runnable; note the rest.)*
- **V5 — runbook coherent:** `developer-guide.md` Deploy Operations section is followable end-to-end.
- **V6 — no secrets committed; gates green:** `git` diff has no secrets; `check`/`build`/`lint` + `make validate-local` + `--check` all green.

**Verdict rule:** V1–V6 pass before `/verification-done`. V1 (status fix) and V2 (artifact assert) are the two that repay the most pain.

## 5. Out of Scope (deferred)
- The actual **BK-018 OAuth fix** (`fix-bk018-oauth-redirect`) — its own Spec, run *after* this scaffold exists (RFC-012 sequencing).
- Full **production cutover** / real prod instances (`BK-019`).
- CI/CD pipeline beyond the CLI wrappers; multi-tenant env management.
- Automating the irreducibly-manual one-time steps (CLI login, Railway volume attach, OAuth app) — documented, not automated.

## 6. Open Questions (resolve at build start)
1. **status fix approach (R5):** stop storing `days_ago` (compute at read-time) vs. exclude it from the `--check` compare. *(Leaning: compute-at-read — kills the drift class entirely; but check the SPA reads `days_ago` from `status.json` and adjust `data.ts` accordingly.)*
2. **deploy wrapper shape:** one `scripts/deploy.sh` handling both services vs. `deploy-backend`/`deploy-frontend` split. *(Leaning: one script with sub-commands; `make deploy-staging` orchestrates.)*
3. **artifact helper form:** standalone `scripts/verify-bundle.sh` vs. inline in `deploy.sh`. *(Leaning: standalone + called by deploy.sh, so it's reusable/testable.)*
