# Frontend Deploy Signal — Requirements

| Property | Value |
| :--- | :--- |
| **Spec ID** | `fix-bk023-frontend-deploy-signal` |
| **Feature** | Close the `/review-pr` gate's frontend-deploy blind spot — read Vercel's **real deployment status** at the gate (C) + a **post-deploy live-bundle assertion** backstop (B) |
| **Backlog** | `BK-023` part 2, `TSK-063` |
| **Status** | 🟡 Proposed (contract authored on KiroCrew Operator; execution on Kiro IDE Executor) |
| **RFCs** | `RFC-LAB-000-004` (branching / required checks), `RFC-LAB-000-011` (Vercel+Railway deploy), `RFC-LAB-000-012` (deploy ops), `RFC-LAB-000-009` (lifecycle) |
| **Executor role** | Delegated-agent / onboarded-dev |

---

## 1. Introduction

`BK-023` found that **three stacked frontend-deploy failures all passed `/review-pr` + green CI** — because the only Vercel-aware signal the gate trusted was the **"Vercel Preview Comments"** check, which reports *comment posting*, **not build/deploy status**. Our GitHub CI runs `pnpm build` directly and passed on the same commits, so "green CI + merged" said nothing about whether the frontend actually deployed. The human eyeball caught all three; the gate did not.

**Part 1 (shipped, PRs #51/#52)** fixed the immediate breakage. **This Spec (part 2) closes the systemic gap** so a broken Vercel build is caught by the gate, not eyeballed.

**Finding that shaped the design (verified 2026-10-01):** Vercel *does* post a genuine deployment signal — on the **commit-status** API (not the check-runs surface), contexts **`Vercel`** and **`Cetana Lab Staging - cetana-labs`**, independent of the misleading "Vercel Preview Comments" check-run. So the fix is to read Vercel's *real* status (**C**) rather than *simulate* Vercel's build in CI; a **post-deploy live-bundle assertion** (**B**) is the honest backstop that the right thing is actually live.

**This is DX/governance plumbing.** It touches the `/review-pr` skill, a small post-deploy check (script or workflow), docs, and branch-protection *guidance* — no application/`data/`/migration logic.

## 0. Preconditions (preflight — verify BEFORE any change; enforced by `tasks.md` T0)

- **P1 — Surface:** Kiro **IDE / local** (Executor), in the Executor clone (`cetana-labs-kiro-ide/`). `/env-doctor` IDE-ready; `gh` authenticated.
- **P2 — Branch:** `feat/fix-bk023-frontend-deploy-signal` off up-to-date `main`; clean tree; not `main`/`master`.
- **P3 — Merge-first:** this Spec merged to `main` before `/spec-run`.
- **P4 — Baseline green:** `/validate-local` passes before changes.
- **P5 — Re-verify the Vercel status surface:** before building, confirm (via `gh api repos/.../commits/<sha>/status`) that the `Vercel` context still posts per-commit; capture whether a FAILED Vercel build posts a `failure`/`error` state or only success-or-silence (decides R1.4's staleness guard).

## 2. Current-state facts (of record — verified 2026-10-01)

- **The misleading signal:** `/review-pr` step 2 reads **check-runs**; Vercel's entry there is **"Vercel Preview Comments"** (comment posting), not deploy health.
- **The real signal (available):** `gh api repos/agni-eialarasu/cetana-labs/commits/<sha>/status` returns contexts **`Vercel`** = success and **`Cetana Lab Staging - cetana-labs`** = success — Vercel's actual deployment statuses.
- **CI ≠ Vercel build (why green CI isn't proof):** CI's `web-build` job runs repo-root `generate_status_json.py` *before* `pnpm build`; **Vercel** (Root Directory `app/web`, no Python) does not. And CI never validates `vercel.json` schema (the `//`-comment-key break).
- **Deploy model:** merge to `main` → Vercel Git integration auto-deploys the frontend (`RFC-LAB-000-011`); `vercel.json` = `framework:null`, `buildCommand pnpm build`, `outputDirectory build`, SPA `rewrites /(.*)→/index.html`.
- **`/review-pr` is Operator-run, read-only**, STOP-and-holds, never merges (`RFC-LAB-000-009` §4).

## 3. Requirements (EARS acceptance criteria = Definition of Done)

### R1 — `/review-pr` reads Vercel's REAL deployment status (C)
- **R1.1** The `/review-pr` skill SHALL, for the PR head SHA, read the **commit-status** API (`commits/<head-sha>/status`) and evaluate the **`Vercel`** deployment-status context (and `Cetana Lab Staging - cetana-labs` if present) — **not** the "Vercel Preview Comments" check-run.
- **R1.2** WHEN the `Vercel` status for the head SHA is not `success`, the gate SHALL mark the frontend-deploy line **❌ / HOLD** and surface the state + link.
- **R1.3** The skill SHALL **explicitly stop trusting "Vercel Preview Comments" as a deploy signal** — if referenced at all, it is labeled "comment posting, NOT deploy status."
- **R1.4** WHEN no `Vercel` status exists for the head SHA, or the latest `Vercel` status is attached to a **different (older) SHA** than the PR head (the stale-success trap from the incident), the gate SHALL treat it as **⚠️ unverified → HOLD**, not a pass. *(Staleness guard — the exact rule tuned by P5's finding on whether failures post a `failure` state or are silent.)*
- **R1.5** The gate's step-6 checklist SHALL gain a **Frontend deploy (Vercel status)** row with ✅/⚠️/❌ + the evidence (context, state, SHA match).

### R2 — Post-deploy live-bundle assertion (B)
- **R2.1** The system SHALL add a **post-deploy live check** (script, e.g. `scripts/verify-live-frontend.sh`, optionally invoked by a post-merge workflow) that fetches the live Vercel URL and **asserts the served bundle references the expected `VITE_PB_URL`** (the Railway PB) and **does NOT** emit the old realtime-popup path (`/api/realtime` for OAuth) — reusing the `scripts/verify-bundle.sh` pattern (`BK-017`) against the live site rather than the local `build/`.
- **R2.2** The check SHALL run **post-merge** (ops-alert semantics, like the backend `BK-022` deploy — a red check + logs, **never** a lifecycle failure that reverts a merge; `done` = the gated merge, Entry 014 D50).
- **R2.3** It SHALL exit non-zero with a clear message naming the mismatch (expected vs found URL / unexpected realtime path), and be runnable on demand locally (parameterized by URL).

### R3 — Branch-protection guidance (make Vercel status a required check)
- **R3.1** The docs SHALL document making the **`Vercel` deployment status a required status check** on `main` (so a failing Vercel build blocks merge automatically), as the durable enforcement behind R1. Marked **[HUMAN]** (branch protection is a GitHub-settings action, deferred until org transfer per `RFC-LAB-000-004`) — documented now, applied when branch protection lands.

### R4 — Documentation lockstep
- **R4.1** `RFC-LAB-000-012` (deploy ops) SHALL gain an append-only note: the real Vercel signal is the **commit-status `Vercel` context**, "Vercel Preview Comments" is NOT a deploy signal, and the gate + post-deploy check that enforce it.
- **R4.2** `developer-guide.md` §9A (Deploy Operations) SHALL document the live-frontend check and how to read Vercel status.
- **R4.3** The **Runtime Infrastructure** artifact (`cetana-labs-runtime-infrastructure`) Deploy-plane tab SHALL note the real deploy signal. *(Operator follow-up; not a `/spec-run` task — noted for lockstep.)*
- **R4.4** `CHANGELOG.md` entry under `[Unreleased]`; `BACKLOG.md` BK-023 part 2 → done; close `TSK-063` in `SPRINT_TRACKER.md`.

### R5 — No regression
- **R5.1** `/review-pr` SHALL remain read-only, STOP-and-hold, never-merge (`RFC-LAB-000-009` §4) — this adds a signal, not an auto-action.
- **R5.2** `/validate-local` + existing CI SHALL pass unchanged; the new live check does not run in the PR-gating CI job (it is post-merge / on-demand).

## 4. Out of scope
- A promotion pipeline or a prod tier (`BK-019`, out of scope).
- Replacing Vercel's Git integration or running `vercel build` in CI (option D — heavier; forward option only).
- Simulating Vercel's build in CI (option A) — **superseded by reading Vercel's real status (C)**; recorded as a rejected alternative in `design.md`.

## 5. Human Verification Plan
1. On a PR whose head has a `Vercel` status = `success`, run `/review-pr` → the **Frontend deploy** row shows ✅ with context+SHA evidence; "Preview Comments" is not treated as the deploy signal.
2. Simulate/await a PR head with a **failing or missing** `Vercel` status → `/review-pr` marks the row ⚠️/❌ and **HOLDs** (R1.2/R1.4).
3. Run `scripts/verify-live-frontend.sh <staging-url>` against the live site → passes (correct `VITE_PB_URL`, no `/api/realtime`); point it at a deliberately-wrong URL → exits non-zero with the mismatch (R2.1/R2.3).
4. Confirm `/review-pr` still never merges and stays read-only (R5.1).
