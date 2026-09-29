# Deploy Scaffold — Tasks

> Ordered plan for `/spec-run` (Build). Execute on **Kiro IDE**. Do NOT merge; open a PR, emit the Human Verification Plan, STOP in `IN_VERIFICATION`. Mostly local/scriptable; live CLI deploy is [HUMAN]/login-gated.

## Execution header (self-describing — read by `/spec-run`)

| Field | Value |
| :--- | :--- |
| **Spec id** | `deploy-scaffold` |
| **Kickoff (IDE one-liner)** | `/spec-run deploy-scaffold` |
| **Surface** | Kiro **IDE** (shell/config/Python; CLI deploy parts are [HUMAN]/login-gated) |
| **Branch to create** | `feat/deploy-scaffold` (off up-to-date `main`, per `RFC-LAB-000-004`) |
| **Base for PR** | `main` |
| **Preflight** | Requirements §0 (P1–P5) + task **T0** |
| **Self-validation target** | `requirements.md` EARS R1–R7 |
| **Human Verification Plan** | `requirements.md` §4b (V1–V6; V1 status-fix + V2 artifact-assert are the headline) |
| **On completion** | Open PR via `gh api`, emit the Verification Plan, STOP → `/verification-done` → `/review-pr` (never merge) |
| **Executor role** | Delegated-agent / onboarded-dev |

---

- [ ] **T0 — Preflight (gate — STOP on any ❌)**
  - Surface=IDE; clean tree; branch `feat/deploy-scaffold` off fresh `main`; this Spec on `main` (merge-first). Baseline green (validators + `pnpm check`/`build`).
  - Railway/Vercel CLIs: if installed, great; if not, note it — the scaffold is authored regardless; live invocation is a one-time [HUMAN] install (don't fabricate).
  - _Refs: §0._

- [ ] **T1 — Fix `status.json` date-drift (`BK-020`) — DO FIRST (unblocks all future PRs)**
  - `generate_status_json.py`: drop the stored `days_ago` key from `build()`; regenerate `data/status.json` without it.
  - SPA: `app/web/src/lib/{data.ts,types.ts}` — compute `days_ago` from `last_updated` at read-time; confirm nothing else consumes stored `days_ago` (grep `scripts/` + `app/web/src`).
  - Verify: `generate_status_json.py --check` now stable across elapsed time (R5.2); SPA shows correct days-ago (R5.3).
  - _Refs: R5, design §2._

- [ ] **T2 — Build-artifact assertion helper (`scripts/verify-bundle.sh` + `make verify-bundle`)**
  - Given expected (+ optional forbidden) backend URL, assert `app/web/build/` bakes in the right `VITE_PB_URL`; fail loudly otherwise (the BK-018 false-negative fix).
  - _Refs: R3, design §4._

- [ ] **T3 — `railway.json` (pin the Containerfile builder)**
  - Add `railway.json` pinning builder=DOCKERFILE → `app/pocketbase/Containerfile` (stop Railpack auto-detect); comment the one-time [HUMAN] volume attach at `/pb/pb_data`.
  - _Refs: R1, design §3._

- [ ] **T4 — CLI deploy wrapper (`scripts/deploy.sh` + `make deploy-staging`)**
  - Sub-commands: deploy-backend (Railway CLI, `app/pocketbase/` context), deploy-frontend (Vercel CLI), all. Read `.env.staging` (gitignored; error+point to `.example` if missing). Capture URLs; **call `verify-bundle.sh` before trusting the frontend**; print the irreducibly-manual one-time checklist. **No secrets in the script.**
  - _Refs: R2, R6.1, design §3._

- [ ] **T5 — Runbook: `developer-guide.md` Deploy Operations**
  - Document CLI-first flow + casual→qualified lifecycle + artifact-verification rule + one-time manual steps; cross-link `RFC-LAB-000-012`.
  - _Refs: R4, design §5._

- [ ] **T6 — Regression + gates**
  - No secrets committed; `.env.staging` gitignored; local dev + staging app unaffected; existing `vercel.json` intact.
  - `pnpm --dir app/web check && build && lint`; `make validate-local`; **`generate_status_json.py --check` green** (demonstrate the drift fix).
  - _Refs: R6, R7._

- [ ] **T7 — Commit, open PR, emit Human Verification Plan, STOP**
  - Branch `feat/deploy-scaffold`; semantic commit referencing `TSK-056` / `BK-017` / `BK-020`.
  - Open PR into `main` via `gh api`; CI green (incl. the now-stable status check); emit §4b plan (V1–V6); STOP in `IN_VERIFICATION`. **Never merge.**
  - _Refs: R-all, `RFC-LAB-000-009` §3.2._

- [ ] **T8 — After human verification passes: `/verification-done`**
  - Human runs V1–V6 (esp. V1 status-fix + V2 artifact-assert); fixes ride the same PR; on pass, `/verification-done` writes the Verification Log → `IN_REVIEW` → `/review-pr`.
  - _Refs: `RFC-LAB-000-009` §3.2._

---

### Governance lockstep reminder (Record, after merge)
Note in CHANGELOG (`TSK-056`, `BK-017` decision implemented + `BK-020` fixed). **This unblocks the deferred BK-018 OAuth fix** (`fix-bk018-oauth-redirect`), which now runs + verifies through this clean CLI + artifact-assert flow. The `status.json` drift papercut should be **gone** after T1 — no more per-PR regenerates for time passing.
