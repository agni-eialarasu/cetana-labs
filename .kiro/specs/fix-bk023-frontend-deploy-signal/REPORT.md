# Frontend Deploy Signal — Execution Report

| Property | Value |
| :--- | :--- |
| **Spec ID** | `fix-bk023-frontend-deploy-signal` |
| **Backlog** | `BK-023` part 2 · `TSK-063` |
| **Branch** | `feat/fix-bk023-frontend-deploy-signal` (off `main` @ `56961e5`) |
| **Executed** | `/spec-run` on the Kiro IDE Executor, 2026-10-01 |
| **State** | IN_VERIFICATION (PR open, awaiting the human verification loop) |

---

## Preflight (T0) — all green

| Check | Result |
| :--- | :--- |
| Surface = Kiro IDE / local | ✅ |
| Spec merged to `main` (merge-first) | ✅ (present at `56961e5`) |
| Branch off up-to-date `main`, clean tree | ✅ |
| Toolchain (python 3.14, node v26, pnpm 12) + deps | ✅ (`pnpm install` restored `node_modules`) |
| Baseline `make validate-local` | ✅ green |

### P5 — Vercel status surface re-verified (the finding that tuned R1.4)
`gh api repos/agni-eialarasu/cetana-labs/commits/<sha>/status` confirmed:
- Two deployment-status contexts post on the **commit-status** API: **`Vercel`** and **`Cetana Lab Staging - cetana-labs`** (both `success` on head `56961e5`).
- Sampling the last 15 `main` commits: **only deploy-triggering commits carry a `Vercel` status** — several commits had **no `Vercel` status at all**. So "missing status for the head SHA" is a *real, common* state, not an edge case → the **⚠️ HOLD on missing-for-head** rule (R1.4) is the correct failure-safe design, not over-strictness.
- A failed Vercel build posts `failure`/`error` per the standard GitHub integration; either way (explicit failure *or* silence) the gate HOLDs — failure-safe.

---

## EARS DoD walk-through (R1–R5)

### R1 — `/review-pr` reads Vercel's REAL deployment status  ✅
- **R1.1** New **step 2b** in `.kiro/skills/review-pr/SKILL.md` reads `commits/<head-sha>/status` and evaluates the **`Vercel`** (and `Cetana Lab Staging - cetana-labs`) context, keyed to the PR head SHA — not the "Vercel Preview Comments" check-run. ✅
- **R1.2** `failure`/`error` for head ⇒ ❌ HOLD, with state + `target_url` surfaced. ✅
- **R1.3** "Vercel Preview Comments" is relabeled in step 2 as **"comment posting, NOT deploy status"** and explicitly not trusted as the deploy signal. ✅
- **R1.4** No `Vercel` status for head, or a success only on an **older SHA** (the stale-success trap), ⇒ ⚠️ HOLD. Encoded as a 4-row state table; the guard is failure-safe (query is keyed to head). Tuned by the P5 finding (missing-for-head is common). ✅
- **R1.5** Step-6 checklist gains a **Frontend deploy (Vercel status)** row requiring evidence (context, state, SHA match). ✅

### R2 — Post-deploy live-bundle assertion  ✅
- **R2.1** `scripts/verify-live-frontend.sh <url> [expected_pb_url]` fetches the live shell + all `/_app/immutable/*.js` and asserts the expected `VITE_PB_URL` is present. ✅
  - **Honest deviation (documented):** the design's "assert the realtime-popup OAuth path absent" is implemented as an **opt-in** check (`FORBID_OAUTH_PATTERN`, off by default), **not** a default. Reason, verified against the live bundle: the PocketBase SDK **always** ships `/api/realtime` *and* `authWithOAuth2(` regardless of which auth flow the app calls, so asserting their absence is a guaranteed false positive. The authoritative live signal is therefore the expected-URL assertion (same basis as `verify-bundle.sh` / `BK-017`). This preserves R2.1's *intent* (catch a frontend that regressed/mis-deployed) without a broken assertion.
- **R2.2** Wired as `verify-live-frontend.yml` — a **post-merge ops-alert** (`push` to `main` on `app/web/**` + `workflow_dispatch`), never a PR-gating/merge-reverting check; no-ops (never fails the run) if `STAGING_WEB_URL` is unset. ✅
- **R2.3** Exits non-zero with a clear message naming the mismatch; runnable on demand (`make verify-live-frontend URL=… EXPECTED=…`). Verified live: positive=0, wrong-URL=1, usage=2. ✅

### R3 — Branch-protection guidance  ✅
- **R3.1** `developer-guide.md` §9A.6 documents making the **`Vercel` deployment status a required status check** on `main`, marked **[HUMAN]** and deferred until branch protection lands post-org-transfer (`RFC-LAB-000-004`); `/review-pr` step 2b is the interim enforcement. ✅

### R4 — Documentation lockstep  ✅ (R4.3 noted as Operator follow-up)
- **R4.1** `RFC-LAB-000-012` §11 append-only note added (real signal = commit-status `Vercel` context; "Preview Comments" ≠ deploy signal). ✅
- **R4.2** `developer-guide.md` §9A.6 documents the live-frontend check + reading Vercel status; command-table row added. ✅
- **R4.3** Runtime Infrastructure artifact Deploy-plane note — **Operator follow-up, not executed here** (spec explicitly tracks, does not execute, this in `/spec-run`). ⏳ handed off.
- **R4.4** `CHANGELOG.md` `[Unreleased]` entry added; `BACKLOG.md` BK-023 part 2 → Done (`TSK-063`); `SPRINT_TRACKER.md` `TSK-063` updated (→ 👀 In Review on PR open). ✅

### R5 — No regression  ✅
- **R5.1** `/review-pr` remains read-only / STOP-and-hold / never-merge — step 2b adds a *signal*, not an auto-action; the Rules section reaffirms it. ✅
- **R5.2** `make validate-local` green after changes; `ci-validate.yml` (the PR-gating required check) does **not** reference the live script; `verify-live-frontend.yml` triggers only on `push`/`workflow_dispatch`, never `pull_request`. ✅

---

## Scope & hygiene
- DX/governance plumbing only — **no** application / `data/` / migration logic touched (9 files: the skill, a script, a workflow, the Makefile, 2 docs, 3 lockstep files).
- `scripts/verify-live-frontend.sh` is bash-3.2 portable (macOS default shell): `mapfile` replaced with a `while read` loop.

## Verification Log

### Verification Log — 2026-10-01 (PR #54)
| Plan step | Result | Finding / correction |
| :--- | :---: | :--- |
| V1 — `/review-pr` step 2b shows the **Frontend deploy** ✅ row (context + head-SHA evidence) when the `Vercel` status = `success`; "Preview Comments" not treated as the deploy signal | ✅ | Passed as implemented. No correction needed. |
| V2 — a failing / missing `Vercel` status on the head SHA ⇒ the row is ⚠️/❌ and the gate HOLDs (R1.2 / R1.4) | ✅ | Passed — failure-safe HOLD confirmed (missing-for-head and failure/error both HOLD). |
| V3 — `scripts/verify-live-frontend.sh` passes against the live site; a deliberately-wrong URL exits non-zero with the mismatch (R2.1 / R2.3) | ✅ | Passed — positive exit 0, wrong-URL exit 1, usage exit 2 against `https://cetana-labs.vercel.app`. |
| V4 — `/review-pr` remains read-only and never merges (R5.1) | ✅ | Passed — the skill adds a signal only; still STOP-and-hold / never-merge. |

- **Iterations:** 0 (no fixups required — all plan steps passed as implemented in commits `b3628c9` / `4df99ae`).
- **Verdict:** PASS — human functional verification complete.
- **Verified by:** Agni Eialarasu (git config) · **Surface:** Kiro IDE
