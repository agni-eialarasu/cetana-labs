# Spec REPORT — `fix-bk018-oauth-redirect`

> The human **sign-off** artifact of the sprint lifecycle (`RFC-LAB-000-009` §3 Phase 5, §9).
> Complements — does not duplicate — the Decision Journal (*why*) and CHANGELOG (*what*).
> This is a **feature** REPORT: the deliverable is shipped code behind PR #46, verified on a
> throwaway 0.40 Railway instance via the RFC-012 CLI + `verify-bundle` flow.

| Property | Value |
| :--- | :--- |
| **Report for** | Spec `fix-bk018-oauth-redirect` (BK-018 fix) |
| **Executor role** | Delegated-agent (AI) + human (Railway/Vercel/browser sign-in) |
| **Surface(s)** | Kiro IDE (code, build, gates) + throwaway 0.40 Railway (live verification) |
| **Date** | 2026-09-30 |
| **Branch / PR** | `feat/fix-bk018-oauth-redirect` / PR #46 → `main` |
| **Related** | Task: `TSK-055` / `BK-018` (SPRINT-10) · RFC: `RFC-LAB-000-011` §4.5, `RFC-LAB-000-012` · Spike: `spike-bk018-pb040-oauth` (Entry 011) |

---

## 1. Outcome (one paragraph)
Fixed the BK-018 root cause and un-pinned PocketBase to 0.40. GitHub sign-in now uses the
redirect-based manual code-exchange flow (`listAuthMethods` → redirect → `authWithOAuth2Code`)
instead of the all-in-one popup (`authWithOAuth2`), so it **never opens `/api/realtime`** — the
SSE channel Railway's edge proxy breaks on PB 0.40 (spike-confirmed). The `Containerfile` pin
moved `0.28.4 → 0.40.4`. Verified end-to-end on a throwaway 0.40 Railway instance: sign-in
completes with **zero** `/api/realtime` requests, `github_handle` linking + owner-write are
intact, the CSRF `state` guard rejects mismatches, and the bundle was proven wired to the
throwaway (not prod) before any live test. **Live prod stayed 0.28.4 throughout** — the live
version cutover is the separate `BK-019` promotion.

## 2. Definition of Done — met? (requirements.md EARS R1–R6)

| DoD (EARS) | Met? | Evidence |
| :--- | :---: | :--- |
| R1 — redirect OAuth replaces popup (start + callback, no `/api/realtime`) | ✅ | `auth.svelte.ts` `signInWithGitHub()` + `completeOAuthCallback()`; `routes/oauth/callback`; V2 network = 0 realtime |
| R2 — preserve M2→M4 (link, owner-write, RBAC, guard, sign-out, persistence) | ✅ | V3 (owner edit saved) + V4 (guard/sign-out/persistence) |
| R3 — un-pin PocketBase to 0.40+ | ✅ | `Containerfile` `ARG PB_VERSION=0.40.4`; V1 sign-in works on 0.40 |
| R4 — GitHub OAuth app callback includes frontend `/oauth/callback` | ✅ | GitHub app has `.../api/oauth2-redirect` + `localhost:5173/oauth/callback` |
| R5 — verify via RFC-012 CLI + `verify-bundle` (not the UI) | ✅ | V6 verify-bundle: throwaway baked, prod absent, before live test |
| R6 — quality gates green | ✅ | `pnpm check` (0/0), `pnpm build`, status/pb_schema/registry `--check` |

**Verdict:** `DONE` — all EARS criteria met; verified on throwaway 0.40.

## 3. Deferred / carried forward (scope honesty)
- **Live prod cutover to 0.40 is NOT done** — this Spec proves the fix on throwaway 0.40 and
  makes the *codebase* 0.40-ready. Promoting live prod (`cetana-labs-staging`) to 0.40 is the
  separate **`BK-019`** cutover (casual→qualified→prod), gated on its own.
- **Vercel preview deployment is red on PR #46** — the SvelteKit build passes in GitHub Actions;
  the failure is the known Vercel env-scoping / Deployment-Protection issue (spike Log V2/V2'),
  not a code defect. To resolve before `/review-pr` closes: scope the preview `VITE_PB_URL` and
  check Deployment Protection. BK-018 verification runs against the throwaway, not the preview.
- **Throwaway teardown** — the `bk018-throwaway` Railway service + its GitHub OAuth app can be
  torn down after merge.

## 4b. Verification Log — 2026-09-30 (branch `feat/fix-bk018-oauth-redirect`; PR #46)

| Plan step | Result | Finding / correction |
| :--- | :---: | :--- |
| V1 — 0.40 sign-in completes (headline) | ✅ | Signed in as Eialarasu on `localhost:5173` against the throwaway 0.40; no 500. The exact scenario that failed in the spike. |
| V2 — no `/api/realtime` | ✅ | DevTools Network filtered on `/api/realtime` = **0/40 requests** during sign-in — the redirect flow's structural guarantee. |
| V3 — `github_handle` link + owner-write | ✅ | Card showed "YOUR STATUS (OWNER)" + Edit; saved status "At Risk - testing" — linked owner, write succeeded. |
| V4 — RBAC / guard / sign-out / persistence | ✅ | Sign-out reverts to anonymous; `(member)` route redirects; refresh persists session. |
| V5 — CSRF state guard | ✅ | `/oauth/callback?code=x&state=wrong` → "Sign-in didn't complete"; mismatch rejected, no auth granted. |
| V6 — bundle verified first | ✅ | `verify-bundle EXPECTED=<throwaway> FORBIDDEN=<prod>` — throwaway baked ×1, prod ×0, **before** any live test (anti-false-negative). |
| V7 — prod untouched | ✅ | `cetana-labs-staging` health 200 + 6 projects intact; never deployed to from this Spec; still 0.28.4. |
| V8 — gates green | ✅ | `pnpm check` 0/0, `pnpm build` ok, governance validators in sync. |

- **Iterations:** 1 pre-verification correction — the throwaway PB advertised **no** OAuth provider
  (`auth-methods` returned empty) until the GitHub provider config was saved in the PB admin;
  re-checked before the live run (avoids a false V1 failure).
- **Verdict:** `PASS — V1–V8 all green; headline V1/V2/V6/V7 solid.`
- **Verified by:** Agni Eialarasu · **Surface:** Kiro IDE + throwaway 0.40 Railway

## 5. Human gate
- PR #46 is **open**, NOT merged. Two governance CI checks green (Build Sleek UI, Validate
  Portfolio/Pillars/Registry); Vercel preview red (known, non-blocking — §3).
- Lifecycle transition on this record: **`IN_VERIFICATION → IN_REVIEW`**. Next: `/review-pr`.
- **Never merged by the executor** — the merge is the human gate.

## 6. Findings & suggestions
- **The redirect flow is the correct, durable fix** — it removes the sign-in path's dependency
  on realtime SSE entirely, which is also PocketBase's recommended production OAuth flow.
- **Resolve the Vercel preview config** (scope preview `VITE_PB_URL`, Deployment Protection) so
  future PR previews are a trustworthy signal rather than a standing red check.
- **Sequence:** merge this (codebase 0.40-ready) → `BK-019` live prod cutover → optional
  `BK-017` staging automation to auto-assert the baked-in URL.
