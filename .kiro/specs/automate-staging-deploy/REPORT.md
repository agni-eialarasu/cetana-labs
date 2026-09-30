# Spec REPORT — `automate-staging-deploy`

> The human **sign-off** artifact of the sprint lifecycle (`RFC-LAB-000-009` §3 Phase 5, §9).
> Complements — does not duplicate — the Decision Journal (*why*) and CHANGELOG (*what*).
> This is a **governance/DX** REPORT: the deliverable is the backend CI-deploy workflow +
> `/deploy-adhoc` tool + the deployment-model docs behind PR #48. The one-time [HUMAN]
> enabler (Railway token/service + volume) is in place; the two live-deploy criteria (V1/V2)
> are **deferred-by-constraint** to immediate post-merge confirmation (see §4b).

| Property | Value |
| :--- | :--- |
| **Report for** | Spec `automate-staging-deploy` (`BK-021` / `TSK-059`) |
| **Executor role** | Delegated-agent (AI) + human (GitHub/Railway console, post-merge Run-workflow) |
| **Surface(s)** | Kiro IDE (code, build, gates) + GitHub/Railway consoles (enabler + live deploy) |
| **Date** | 2026-09-30 |
| **Branch / PR** | `feat/automate-staging-deploy` / PR #48 → `main` |
| **Related** | Task: `TSK-059` / `BK-021` (SPRINT-10) · Decision Journal **Entry 014** (D49–D52) · RFCs: `RFC-LAB-000-012` (reframed as reference ops guidance), `-011` (Vercel + Railway), `-004` (branch → PR → gate) · Scope edge: `BK-019` (prod cutover, out of scope) |

---

## 1. Outcome (one paragraph)
Encoded **`main` = the single reference environment**: a gated merge deploys both tiers.
Added `.github/workflows/deploy-backend.yml` — a **path-filtered** (`app/pocketbase/**`)
push-to-`main` deploy of PocketBase → Railway via the Railway CLI + `secrets.RAILWAY_TOKEN`
(project token, environment-scoped; CLI pinned to `@railway/cli@5.2.0` because v5.3.0 broke
project-token auth in CI), reusing the committed `railway.json` builder pin. A deploy failure
is a loud **ops alert** (red check), never a lifecycle failure (`done` = the gated merge, D50);
the workflow is deliberately **not** a required check. Added a `/deploy-adhoc` developer tool
(`make deploy-adhoc ENV=<file>` + skill) for on-demand deploys to arbitrary instances,
disambiguated the Makefile (the auto-staging pipeline *is the merge*), refreshed the stale
GCP staging placeholders to the Railway/Vercel reality, documented the model in
`developer-guide.md` §9A.0, reframed `RFC-LAB-000-012` as reference ops guidance, and kept
`CHANGELOG`/`SPRINT_TRACKER` in lockstep. Later added `workflow_dispatch` (a manual re-deploy
button + intended pre-merge V1 smoke-test — see the constraint in §3).

## 2. Definition of Done — met? (requirements.md EARS R1–R7)

| DoD (EARS) | Met? | Evidence |
| :--- | :---: | :--- |
| R1 — backend CI deploy on merge; path-filtered; token from secrets; reuses `railway.json`; failure = ops alert | ✅ (code) / ⏸️ (live) | `deploy-backend.yml`: `on: push:[main] paths:[app/pocketbase/**, self]`; `railway up ... --ci --path-as-root .`; `RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}`; no rollback. **Live firing = V1 (deferred, §4b).** |
| R2 — a merge deploys both tiers; Vercel integration untouched | ✅ | §9A.0 documents both-tiers symmetry; no change to `app/web/vercel.json` or the Vercel Git integration. |
| R3 — `/deploy-adhoc` to an arbitrary instance + skill + `verify-bundle` guard | ✅ | `Makefile` `deploy-adhoc` (`ENV_FILE=$(ENV) scripts/deploy.sh`); `.kiro/skills/deploy-adhoc/SKILL.md`; `verify-bundle` retained in `deploy.sh deploy-frontend`. |
| R4 — Makefile disambiguation (pipeline vs ad-hoc) | ✅ | `deploy-staging` reframed as manual override; DEPLOY MODEL comment block (Entry 014); `make help` shows both. |
| R5 — refresh stale staging placeholders | ✅ | `make validate-staging` + `status-staging`/`validate-staging` skills now Railway/Vercel; no "GCP … pending org transfer" remains. |
| R6 — docs: the model + the boundary; RFC-012 reframe | ✅ | `developer-guide.md` §9A.0 "The Deployment Model"; RFC-012 append-only scoping note (Entry 014, D52). |
| R7 — no regression / secrets discipline / gates green | ✅ | `pnpm check` 0/0, `pnpm build` ok, 5 Python validators green; no literal token in repo; new workflow additive (not a required check). |

**Verdict:** `PASS (pre-merge scope) — all buildable DoD met; R1's live-firing = V1/V2 deferred-by-constraint to immediate post-merge confirmation.`

## 3. Deferred / carried forward (scope honesty)
- **V1/V2 are physically unobservable pre-merge — deferred, NOT skipped.** `deploy-backend.yml`
  is a **new** workflow: GitHub only registers a `workflow_dispatch` "Run workflow" button (and
  only accepts a REST dispatch) once the workflow exists on the **default branch** (`main`) — a
  dispatch against the PR branch returns HTTP 404 (observed). And the `on: push` trigger cannot
  fire until the file is on `main`. So neither the manual nor the on-push path can run before
  merge. This is a GitHub platform constraint, not a gap in the work. Confirmation method for each:
  - **V1** (deploy fires + Railway auth works): after merge, Actions tab → *Deploy Backend
    (Railway)* → **Run workflow** (`workflow_dispatch`) → expect a green run + a new Railway
    deployment on the `cetana-labs` service. Re-confirmed naturally by the next real
    `app/pocketbase/**` merge (the on-push path).
  - **V2** (path filter skips non-backend): observed by **PR #48's own merge NOT firing** the
    backend deploy — PR #48 touches no `app/pocketbase/**`, so the workflow must be absent from
    the merge commit's checks.
- **V4/V5/V6 verified by code-review** (live run not required to establish the criterion): V4 —
  the workflow has no rollback and a deploy failure is only a red check; V5 — `deploy-adhoc`
  targets an arbitrary `ENV` file via `scripts/deploy.sh` with the `verify-bundle` guard intact;
  V6 — both-tiers symmetry is documented in §9A.0 and true (Vercel untouched + Railway added). A
  live V5/V6 exercise (actual throwaway deploy) can be run opportunistically post-merge but is
  not required for the criterion.
- **Prod cutover is out of scope** — no promotion pipeline, no prod tier (`BK-019`).
- **One-time [HUMAN] enabler — DONE:** `RAILWAY_TOKEN` secret (scoped to the Railway `staging`
  environment); `RAILWAY_SERVICE` repo variable = `cetana-labs` (the actual service name;
  workflow default was `pocketbase`); Railway volume `cetana-lab-data` mounted at `/pb/pb_data`
  (data persists). `bk018-throwaway` retained for `/deploy-adhoc` testing.

## 4b. Verification Log — 2026-09-30 (branch `feat/automate-staging-deploy`; PR #48)

| Plan step | Result | Finding / evidence |
| :--- | :---: | :--- |
| V1 — backend CI deploy fires on backend change (headline) | ⏸️ DEFERRED (post-merge) | Physically unobservable pre-merge: a new `workflow_dispatch`/on-push workflow must be on the default branch first (REST dispatch on the PR branch → HTTP 404, observed). Confirm post-merge via Actions → Run workflow, then via the first real `app/pocketbase/**` merge. **Not skipped.** |
| V2 — path filter skips non-backend merges | ⏸️ DEFERRED (post-merge) | Confirmed by PR #48's own merge NOT firing the backend deploy (touches no `app/pocketbase/**`). Observable only at merge. **Not skipped.** |
| V3 — token from secrets, no secret in repo (headline) | ✅ PASS (pre-merge) | `git grep` for a literal token = 0 hits; only functional ref is `RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}` (rest are comments); no tracked non-example `.env`. |
| V4 — deploy failure = ops alert, not a lifecycle failure (headline) | ✅ PASS (code-review) | Workflow has no rollback/revert; a failed `railway up` only reds the run; `deploy-backend.yml` is not a required check, so it cannot block/revert the merged commit. |
| V5 — `/deploy-adhoc` hits an arbitrary instance | ✅ PASS (code-review) | `make deploy-adhoc ENV=<file>` → `ENV_FILE="$(ENV)" scripts/deploy.sh` (arbitrary env); usage guard exits 2 without `ENV`; `verify-bundle` guard retained for frontend. Live throwaway run optional post-merge. |
| V6 — both-tiers symmetry documented + true | ✅ PASS (code-review) | §9A.0 documents merge → Vercel (frontend) + Railway (backend); Vercel Git integration untouched; Railway half added by `deploy-backend.yml`. |
| V7 — placeholders refreshed (no GCP) | ✅ PASS (pre-merge) | `make validate-staging` + staging skills now Railway/Vercel single-reference; `git grep` finds no "pending org transfer"/"GCP (backend" in the staging surfaces. |
| V8 — gates green + docs/RFC reframe present | ✅ PASS (pre-merge) | CI 3/3 green (Validate, Build Sleek UI, Vercel Preview Comments); `developer-guide.md` §9A.0 present; RFC-012 reframe note (Entry 014/D52) present. |

- **Iterations:** 1 correction during setup — the workflow's `--service` default was `pocketbase`,
  but the actual Railway service is `cetana-labs`; resolved by adding the `RAILWAY_SERVICE` repo
  variable = `cetana-labs` (no code change needed — the workflow already reads
  `vars.RAILWAY_SERVICE`). Also added `workflow_dispatch` (commit `bc29fc3`) as a manual
  re-deploy button and the intended V1 smoke path — which surfaced the default-branch constraint.
- **Verdict:** `PASS (pre-merge scope) — V3/V7/V8 verified firsthand, V4/V5/V6 by code-review;`
  `V1/V2 deferred-by-constraint to immediate post-merge confirmation (Run workflow for V1; the`
  `non-firing merge for V2). No V1/V2 pass is claimed.`
- **Verified by:** Agni Eialarasu · **Surface:** Kiro IDE + GitHub/Railway consoles

## 5. Human gate
- PR #48 is **open**, NOT merged. CI green (Validate Portfolio/Pillars/Registry, Build Sleek UI,
  Vercel Preview Comments). `deploy-backend.yml` is additive and **not** a required check.
- Lifecycle transition on this record: **`IN_VERIFICATION → IN_REVIEW`**. Next: `/review-pr` on
  Kiro Web (it consumes this honest record, including the explicit V1/V2 deferral).
- **Never merged by the executor** — the merge is the human gate. Immediately after merge, run
  the V1 Run-workflow smoke-test and note the V2 non-firing to close the deferred pair.

## 6. Findings & suggestions
- **The `workflow_dispatch` default-branch constraint is worth remembering** for any future new
  deploy workflow: pre-merge smoke-testing of a brand-new `workflow_dispatch` isn't possible;
  plan V1-type checks as immediate post-merge steps, or land the workflow shell earlier.
- **`workflow_dispatch` is a keeper** beyond the smoke test — a GitHub-native manual re-deploy
  button for the staging backend (apply Railway env changes / restart without a code change).
- **Post-merge close-out:** run V1 (Run workflow → green + new Railway deployment), record V2
  (merge didn't fire the backend deploy), then this Spec's DoD is fully closed on the live path.
