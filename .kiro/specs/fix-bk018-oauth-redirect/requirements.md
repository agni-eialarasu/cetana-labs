# Fix BK-018 — Redirect OAuth + Un-pin PocketBase to 0.40+ — Requirements

| Property | Value |
| :--- | :--- |
| **Spec ID** | `fix-bk018-oauth-redirect` |
| **Feature** | Fix the BK-018 root cause: switch GitHub sign-in from the popup flow to the redirect-based `authWithOAuth2Code` flow, so PocketBase can un-pin `0.28.4 → 0.40+` on Railway |
| **Backlog** | `TSK-055` (`BK-018`, SPRINT-10) |
| **Status** | 👀 In Review (implemented + verified V1–V8 on throwaway 0.40; PR #46 open; `IN_VERIFICATION → IN_REVIEW`) |
| **RFCs** | `RFC-LAB-000-011` §4.5 (the fix decision-of-record), `RFC-LAB-000-012` (deploy ops — verify via CLI + `verify-bundle`), `RFC-LAB-000-006`/`-008` (OAuth/RBAC) |
| **Grounded by** | The `spike-bk018-pb040-oauth` finding (Journal Entry 011): root cause **confirmed**, H1 **chosen** |
| **Executor role** | Delegated-agent / onboarded-dev |

---

## 1. Introduction

The BK-018 spike **confirmed** (Entry 011 / RFC-011 §4.5): PocketBase 0.40's all-in-one **popup** OAuth (`authWithOAuth2`) receives its callback over the **realtime SSE channel**, which **Railway's proxy doesn't preserve** → `POST /api/realtime 400` → sign-in fails. Prod is therefore **pinned to 0.28.4** as a workaround. The chosen fix (H1): switch the frontend to the **redirect-based `authWithOAuth2Code`** flow, which **never touches `/api/realtime`** — structurally sidestepping the proxy/SSE issue — and **un-pins the backend to 0.40+**.

This Spec **implements that fix** (the spike only chose the direction). It ships through the normal gate; verification uses the `RFC-LAB-000-012` CLI + `verify-bundle` flow (not the painful UI path that derailed the spike).

**Key technical shape (verified against the SDK):** `authWithOAuth2Code` is the **manual code-exchange / redirect** flow — a *two-part* call site, not a one-line swap:
1. **Start:** `listAuthMethods()` → the GitHub provider's `authURL` + `codeVerifier` + `state`; persist `codeVerifier`/`state`; redirect the browser to `authURL + redirectURL`.
2. **Callback route:** on return from GitHub, read `code`/`state` from the query, verify `state`, and call `authWithOAuth2Code(provider, code, savedCodeVerifier, redirectURL)`.

## 0. Preconditions (preflight — verify BEFORE any change; enforced by `tasks.md` T0)

- **P1 — Surface:** Kiro **IDE / local** for the code; a **live 0.40 Railway instance** (throwaway/staging) for verification — the bug (and thus the fix) only manifests behind Railway's proxy, not locally.
- **P2 — Toolchain:** Node/pnpm; Railway/Vercel CLIs (per `RFC-LAB-000-012`); the `verify-bundle` helper (merged).
- **P3 — Branch:** `feat/fix-bk018-oauth-redirect` off up-to-date `main`; clean tree; not `main`/`master`.
- **P4 — Merge-first:** this Spec merged to `main` before `/spec-run`.
- **P5 — Baseline green:** three validators + `pnpm --dir app/web check && build`.
- **P6 — Non-destructive:** do NOT touch live prod (0.28.4) until this fix is verified + gated; test on a throwaway/staging 0.40 instance (casual→qualified, `RFC-LAB-000-012` §4).

## 2. Current-state facts (of record — verified)

- **Call site:** `app/web/src/lib/auth.svelte.ts:98` — `pb.collection('users').authWithOAuth2({ provider: 'github' })` (popup), with `loginFromMeta(res.meta)` resolving the GitHub login for `github_handle` linking + owner-write (M2/M3–M4).
- **Backend pin:** `app/pocketbase/Containerfile:19` — `ARG PB_VERSION=0.28.4` (the workaround to un-pin).
- **Hook:** `pb_hooks/oauth_github_handle.pb.js` populates `github_handle` on OAuth — **must keep working** through the redirect flow (it fires on `onRecordAuthWithOAuth2Request`, which the code exchange also triggers).
- **Routing:** SvelteKit static SPA (`ssr=false`); a **callback route** is new (`(member)` group exists from M2). The redirect flow needs a client-side callback handler.
- **DX available:** `make verify-bundle` (assert baked-in `VITE_PB_URL`), `make deploy-staging` (CLI deploy) — from `RFC-LAB-000-012`.

## 3. Requirements (EARS acceptance criteria = Definition of Done)

### R1 — Redirect-based OAuth (replaces the popup)
- **R1.1** `signInWithGitHub()` SHALL initiate the **redirect** flow: `listAuthMethods()` → GitHub provider `authURL`/`codeVerifier`/`state`; persist `codeVerifier` + `state` (session/localStorage); redirect the browser to `authURL` + the app'"'"'s `redirectURL`.
- **R1.2** A **callback route** SHALL handle GitHub'"'"'s redirect back: read `code` + `state`, **verify `state`** matches the persisted value (CSRF guard), then call `authWithOAuth2Code(provider, code, codeVerifier, redirectURL)`.
- **R1.3** The flow SHALL **NOT** open `/api/realtime` at any point (structurally avoiding the proxy/SSE failure — the whole point).
- **R1.4** On success, the auth store SHALL reflect signed-in state (as M2 did) and the user SHALL land back in the app signed-in (no popup).

### R2 — Preserve M2/M3–M4 behavior (no regression to the auth loop)
- **R2.1** `github_handle` SHALL still be populated on sign-in (the `pb_hooks` hook fires on the code-exchange auth) and account-link-by-handle SHALL still resolve the seeded owner.
- **R2.2** The owner-write path (M4) SHALL still work — an owner edits their own project status after signing in via the redirect flow.
- **R2.3** Minimum RBAC (M3) SHALL be unchanged (server-side rules; the OAuth flow change is client-side only). Non-owner still denied.
- **R2.4** The `(member)` route guard, sign-out, and persistence (M2) SHALL still work.

### R3 — Un-pin PocketBase to 0.40+
- **R3.1** `app/pocketbase/Containerfile` `ARG PB_VERSION` SHALL be updated from `0.28.4` to a current **0.40.x** release; the workaround comment SHALL be replaced with a note that the redirect flow (R1) removes the realtime dependency (ref RFC-011 §4.5).
- **R3.2** On the 0.40 Railway instance, GitHub sign-in SHALL complete end-to-end (the reproduction that failed on 0.40 now passes).

### R4 — GitHub OAuth app config
- **R4.1** The GitHub OAuth app callback SHALL include the app'"'"'s **redirect route URL** (the redirect flow returns to the *frontend*, not `/api/oauth2-redirect`); documented in `developer-guide.md`. *(Config step — [HUMAN]; the Spec states it, doesn'"'"'t fabricate it.)*

### R5 — Verify via the RFC-012 flow (not the UI)
- **R5.1** Deployment for verification SHALL use `make deploy-staging` / the CLIs; the frontend build SHALL be checked with `make verify-bundle` (assert the throwaway 0.40 `VITE_PB_URL` is baked in) **before** trusting any live test — the exact discipline that caught the spike'"'"'s false negative.
- **R5.2** Prod (0.28.4) SHALL remain untouched until this ships through `/review-pr` + merge (non-destructive; P6).

### R6 — Quality gates green
- **R6.1** `pnpm --dir app/web check && build && lint`, `make validate-local`, and `generate_status_json.py --check` SHALL pass.

## 4b. Human Verification Plan (emitted by `/spec-run`; recorded by `/verification-done`)

On a **throwaway/staging 0.40 Railway** instance (per RFC-012 casual→qualified), verified via CLI + `verify-bundle`:
- **V1 — 0.40 sign-in works (the headline):** with PB **0.40.x** on Railway + the redirect flow, GitHub sign-in **completes** (no `/api/realtime 400`, no 500). This is the exact scenario that failed in the spike.
- **V2 — no realtime call:** confirm (network tab) the sign-in makes **no `/api/realtime`** request — the redirect flow's structural guarantee (R1.3).
- **V3 — `github_handle` + owner-write (R2):** signed-in owner is linked by handle and can edit their own project status (M2→M4 intact through the new flow).
- **V4 — RBAC + guard + sign-out + persistence (R2):** non-owner denied; `(member)` guard redirects; sign-out reverts; refresh persists.
- **V5 — state/CSRF:** a mismatched/absent `state` on callback is rejected (not silently accepted).
- **V6 — bundle verified:** `make verify-bundle` confirmed the throwaway `VITE_PB_URL` (not prod) was baked in **before** V1 (the anti-false-negative discipline).
- **V7 — prod untouched:** live prod is still 0.28.4 and functioning throughout (nothing shipped to it from this verification).
- **V8 — gates green.**

**Verdict rule:** V1–V8 pass before `/verification-done`. V1 (0.40 sign-in works) + V6 (bundle verified first) are the headline; V7 (prod untouched) is the safety guarantee.

## 5. Out of Scope (deferred)
- **Actually cutting live prod over to 0.40** — this Spec proves + ships the fix on staging/throwaway; promoting *live prod* to 0.40 is the **`BK-019`** cutover (casual→qualified→prod), gated separately once this is proven.
- The 5-role `memberships` model, audit trail, custom domain — unchanged / deferred.
- Any RBAC/write logic change — the fix is the OAuth *flow*, client-side; server rules untouched.

## 6. Open Questions (resolve at build start)
1. **Callback route path:** a dedicated `/(auth)/callback` (or `/oauth/callback`) route vs. handling the code on the existing landing route. *(Leaning: a dedicated callback route — clearest, and keeps the public dashboard clean.)*
2. **codeVerifier/state storage:** `sessionStorage` (cleared on tab close) vs. `localStorage`. *(Leaning: `sessionStorage` — the values are single-use + short-lived; less residue.)*
3. **`redirectURL` per environment:** local vs. staging vs. prod differ — env-derive it (from `window.location.origin`) rather than hardcode. *(Leaning: derive from origin; register all needed callbacks in the GitHub app.)*
4. **How far to take live verification:** stop at "verified on throwaway 0.40" (this Spec) and leave the live-prod 0.40 cutover to `BK-019`? *(Leaning: yes — this Spec = fix + un-pin + throwaway-verified; live cutover is BK-019.)*
