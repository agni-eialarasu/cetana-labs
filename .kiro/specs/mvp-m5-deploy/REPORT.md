# Sprint / Spec REPORT — Spec `mvp-m5-deploy`

> Human sign-off artifact for the AIDLC Spec run (`RFC-LAB-000-009` §3 Phase 5).
> Thin and sign-off-only; complements the Decision Journal (*why*) and CHANGELOG (*what*).

| Property | Value |
| :--- | :--- |
| **Report for** | Spec `mvp-m5-deploy` |
| **Executor role** | Delegated-agent (repo/CLI) + **human-in-console** (Railway/Vercel/OAuth) — `RFC-LAB-000-009` §5 |
| **Surface(s)** | Kiro IDE (repo + local verify) + cloud consoles (human) |
| **Date** | 2026-09-28 |
| **Related** | RFC(s): `RFC-LAB-000-011` (deployment, amended: Vercel + Railway), `RFC-LAB-000-008` §6 · Epic/Task: `BK-011` / `TSK-054` · PR(s): #38 |

---

## 1. Outcome (one paragraph)
Deployed the authenticated MVP app end-to-end: SvelteKit SPA → **Vercel** (`https://cetana-labs.vercel.app`), PocketBase → **Railway** (container + persistent volume, `https://cetana-labs-staging.up.railway.app`), production GitHub OAuth wired, RBAC + owner-writes working live, and the GitHub-Pages classic dashboard retired. **This completes the MVP local→deployed loop (`BK-011`).** Per a lead decision (§3), this Railway+Vercel setup is a **staging environment treated as production** (no real users yet); a real production cutover is tracked as `BK-019`.

## 2. Definition of Done — met? (the gate summary)

| DoD item (R#) | Met? | Evidence |
| :--- | :---: | :--- |
| R1 — PocketBase on Railway (container + volume, HTTPS, seeded) | ✅ | Live URL; 6 projects seeded; volume survives redeploys |
| R2 — Frontend on Vercel (`VITE_PB_URL` → Railway) | ✅ | `cetana-labs.vercel.app` reads live Railway data |
| R3 — Production auth wired | ✅ | GitHub sign-in works on the live URL; owner-writes live |
| R4 — Minimum RBAC holds in prod | ✅ | anon write → 404 (live); owner-write → 200; rule identical to verified local |
| R5 — Dual-run then retire Pages | ✅ | Pages stopgap removed after live verify; refs fixed |
| R6 — Config, secrets, docs | ✅ | prod env docs (keys only); `developer-guide.md` §9 runbook; no secret committed |
| R7 — No regression | ✅ | local M1–M4 + snapshot fallback intact; validate-local green |
| R8 — Gates green | ✅ | check/build/lint + validate-local; CI green; no ref to removed workflow |

**Verdict:** `DONE (staging-as-prod; prod cutover deferred → BK-019)`

## 3. Deferred / carried forward (scope honesty)
- **`BK-019` — production cutover:** M5's deploy is a staging env accepted as prod (lead decision, no real users). Real prod (dedicated instances, custom domain `BK-013`, promotion/backup discipline) is deferred.
- **`BK-018` — latest PocketBase on Railway:** server pinned to **0.28.4** (a proven-good workaround, not a root fix — see §4). Running latest PB (0.40+) on Railway is a spike.
- **`BK-017` — staging deploy automation & docs:** `make setup-staging` + `.env.staging` + CLI scripting, to remove the manual console pain felt here.
- Custom domain, backups hardening, 5-role RBAC, audit trail — all still deferred (per M5 scope §5).

## 4. Corrections & scope decisions during verification (append-only)

M5 was **infra + config**, mostly human-in-console — and the live deploy surfaced a chain of real issues (none visible in local dev). All fixed on this PR:

- **`768435d` — Railway build rejected the Dockerfile `VOLUME`.** Removed `VOLUME`; persistence attached via a Railway Volume at `/pb/pb_data` (portable: `-v` for Podman/Docker).
- **Build context** — `COPY pb_schema.json` failed until Railway's Root Directory was set to `app/pocketbase` (human, dashboard).
- **Env vars** — Railway auto-imported the `.env.example` *local placeholders* (`change-me-locally`, `127.0.0.1`); the admin password had to be set to a real value (security).
- **`8f3aa42` / `991cdb3` / `b6f3da4` — the version saga (honest):** owner-write 404'd because the `Containerfile` never `COPY`'d `pb_hooks/` → the `github_handle` hook didn't run on Railway. Fixed by baking `pb_hooks/` into the image. I *also* bumped PB 0.28.4→0.40.4 for "parity with local" — **that was a wrong call**: it broke OAuth on the deploy (`/api/realtime 400 Invalid realtime client`). Reverted to 0.28.4 (proven-good). The real trigger is **0.40's realtime/OAuth handshake through Railway's cross-origin HTTPS proxy** — NOT an SDK↔server version gap (local runs 0.40 fine). Root-cause + latest-PB tracked in `BK-018`; the Containerfile comment was corrected to say so.
- **`5665d83` — T6 Pages retirement** (done after live verify, per lead decision staging=prod): removed `docs/index.html` + `deploy-pages.yml` + `generate_dashboard.py`; fixed all active refs; historical mentions left intact.
- **DX pain acknowledged** → `BK-017` (deploy automation + docs).

## 5. Verification Log — human functional verification

### Verification Log — 2026-09-28 (PR #38, LIVE URLs)
| Plan step | Result | Finding / correction |
| :--- | :---: | :--- |
| V1 — Backend live + seeded | ✅ | Railway PB HTTPS, admin reachable, 6 projects (after the build-context + volume fixes). |
| V2 — Frontend live reads Railway | ✅ | Vercel app loads live data (after Output-Directory=`build` fix). |
| V3 — Sign in (prod) | ✅ | GitHub OAuth on the Vercel URL; linked by `github_handle` (after PB 0.28.4 + pb_hooks). |
| V4 — Owner write (prod) | ✅ | Owner edits own status → persists to Railway (after the pb_hooks-in-image fix). |
| V5 — RBAC (SECURITY) | ✅* | **Anon write → 404 denied** on the live instance; owner-write (V4) is the positive control; public read → 200; no write landed. ***Non-owner-authenticated leg accepted by equivalence*** (see note below), not a distinct 2nd-account live test. |
| V6 — Persistence (volume) | ✅ | Data survived multiple Railway redeploys during the fix cycle (the volume's whole point). |
| V7 — Pages retired cleanly | ✅ | Stopgap removed; no dangling active links; CI has no ref to the removed workflow. |
| V8 — Gates + no regression | ✅ | `check`/`build`/`lint` + `make validate-local` green; local M1–M4 intact; CI green (+ Vercel preview). |

- **Iterations:** 5 fixups on this PR (`768435d`, `8f3aa42`, `991cdb3`, `b6f3da4`, `5665d83`) — the deploy layer was the most iterative of any MVP spec.
- **Verdict:** PASS — human functional verification complete (V1–V8), with the V5 caveat recorded honestly below.
- **Verified by:** Agni Eialarasu · **Surface:** Kiro IDE + live cloud URLs

> **V5 honesty note (accept-by-equivalence, lead-approved):** the *non-owner-authenticated* write-denial was NOT exercised with a distinct second GitHub account on the live app (that needs a second identity the executor doesn't have). It is accepted as verified because: (a) the deployed `updateRule` is byte-identical to the local rule where V3 fully proved non-owner-authed → 404 (M3–M4 `/verification-done`); (b) the **anonymous** write-denial IS confirmed live (404); (c) enforcement is server-side and origin/identity-agnostic. Residual risk: a deploy-specific auth-context quirk that only manifests for an authenticated-but-non-owner session — low, given the anon + owner legs both behave correctly live. A 2nd-account spot-check remains available if desired.

> **Version note:** prod runs PB **0.28.4** (pinned workaround); the local-verified stack is 0.40.4. The behaviors that matter (rules, hook, OAuth) were confirmed working on the deployed 0.28.4. Moving prod to latest is `BK-018`.

## 6. Human gate
- PR: #38 — verification PASS recorded; state **IN_REVIEW**, ready for `/review-pr 38` · CI green (Validate ✅, Build ✅, Vercel preview ✅) · squash-merged: no (awaiting gate).

## 7. Sign-off
- **Signed:** Agni Eialarasu (Lead) — 2026-09-28 — human functional verification PASS (V1–V8; V5 accept-by-equivalence, noted).
- **This completes the MVP (`BK-011`).** `/sprint-done` closes SPRINT-09 and cuts the MVP release (candidate `v0.11.0`).
- Follow-ups: `BK-017` (deploy automation), `BK-018` (latest-PB compat), `BK-019` (prod cutover).
