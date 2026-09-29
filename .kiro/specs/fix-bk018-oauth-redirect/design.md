# Fix BK-018 — Redirect OAuth + Un-pin — Design

> Companion to `requirements.md`. Replace the popup OAuth (`authWithOAuth2`) with the redirect-based **manual code-exchange** flow (`listAuthMethods` → redirect → `authWithOAuth2Code`), preserve the M2→M4 auth loop, and un-pin PocketBase to 0.40+. Verified on a throwaway 0.40 Railway instance via the RFC-012 CLI + `verify-bundle` flow. **Prod stays 0.28.4 until gated + (BK-019) cut over.**

---

## 1. Why a two-part flow (not a one-line swap)

The popup `authWithOAuth2({provider})` is *one call* that opens a popup **and** listens on `/api/realtime` for the result — that realtime channel is what Railway's proxy breaks. `authWithOAuth2Code` is the **manual** flow: no popup, no realtime; instead the app **redirects the whole page** to GitHub and handles the return on a **callback route**. So the call site splits into **start** + **callback**, plus **cross-redirect state** (`codeVerifier`, `state`) that must survive the round-trip.

## 2. The flow (verified against the SDK)

```
signInWithGitHub()  [start]                         /oauth/callback  [return]
──────────────────────────────                      ─────────────────────────
methods = pb.collection('users').listAuthMethods()  const {code, state} = queryParams
gh = methods.oauth2.providers.find(github)          assert state === sessionStorage.state   // CSRF (R1.2)
sessionStorage: codeVerifier=gh.codeVerifier,       await pb.collection('users')
                state=gh.state                        .authWithOAuth2Code(
window.location = gh.authURL + redirectURL              'github', code,
                                                         sessionStorage.codeVerifier,
   ── browser leaves to GitHub ──▶                      redirectURL)
                                                    // authStore now valid → resolve github_handle → land in app
```
- **`redirectURL`** = `${window.location.origin}/oauth/callback` (env-derived — OQ-3; register per-env callbacks in the GitHub app).
- **No `/api/realtime`** anywhere in this path (R1.3) — the structural fix.

## 3. Call-site changes (`app/web/src/lib/auth.svelte.ts`)

- **`signInWithGitHub()`** → the **start** half (§2 left): `listAuthMethods`, stash `codeVerifier`+`state` in `sessionStorage` (OQ-2), `window.location.assign(authURL + redirectURL)`.
- **New `completeOAuthCallback()`** → the **return** half: verify `state`, `authWithOAuth2Code(...)`, then the *existing* post-auth logic (`loginFromMeta` / `github_handle` resolve, `#authed` flip, `LINK_KEY`) — reuse M2's `#resolve(...)` so R2.1 linking is unchanged.
- `res.meta` shape from `authWithOAuth2Code` carries the same `rawUser.login` → `loginFromMeta` works unchanged.

## 4. Callback route (`app/web/src/routes/(auth)/callback/+page.*` — OQ-1)

- A minimal client-side route (`ssr=false` already global): on mount, call `auth.completeOAuthCallback()`, show a "signing you in…" state, then redirect to the dashboard (or the pre-auth destination) on success; on failure (bad `state`, exchange error) show a clear error + a retry link. Not under `(member)` (it must be reachable while still anonymous mid-flow).

## 5. Un-pin the backend (`app/pocketbase/Containerfile`)

- `ARG PB_VERSION=0.28.4` → a current **0.40.x** (e.g. `0.40.x` latest verified). Replace the workaround comment with: *"0.40+ is fine now that sign-in uses the redirect `authWithOAuth2Code` flow (no `/api/realtime`); ref RFC-011 §4.5 / BK-018."*
- The `oauth_github_handle.pb.js` hook stays — it fires on `onRecordAuthWithOAuth2Request`, which the code exchange also triggers (R2.1). Confirm during verification.

## 6. Verify via RFC-012 flow (not the UI — the anti-false-negative discipline)

1. Deploy PB **0.40.x** to a **throwaway** Railway instance (`make deploy-staging` / Railway CLI); seed via `pb_provision.py`/`pb_import.py`.
2. Build the SPA with `VITE_PB_URL=<throwaway>`; **`make verify-bundle EXPECTED=<throwaway> FORBIDDEN=<prod>`** — confirm the *right* backend is baked in **before** any live test (V6). *(This is the exact check that would have caught the spike's false negative.)*
3. Sign in on the deployed throwaway → confirm completion + **no `/api/realtime`** (V1/V2) + owner-write (V3) + RBAC/guard/persistence (V4) + state-mismatch rejected (V5).
4. **Prod stays 0.28.4** throughout (V7).

## 7. Non-destructive & sequencing

- This Spec ships the **fix** (redirect flow + un-pinned Containerfile) and proves it on **throwaway 0.40**. It does **not** cut live prod to 0.40 — that promotion is **`BK-019`** (casual→qualified→prod), gated separately (OQ-4). So merging this makes the *codebase* 0.40-ready and correct; the live prod version bump is a deliberate later step.

## 8. Trade-offs

| Decision | Chosen | Rejected | Why |
| :--- | :--- | :--- | :--- |
| OAuth flow | redirect `authWithOAuth2Code` | popup `authWithOAuth2` | Popup needs `/api/realtime` which Railway's proxy breaks on 0.40 (spike-confirmed); redirect never touches it + is PB's recommended prod flow. |
| Call site | start + callback route | one function | The redirect flow is inherently two-phase; a callback route is required. |
| Cross-redirect state | `sessionStorage` | `localStorage` / cookie | Single-use, short-lived; least residue (OQ-2). |
| `redirectURL` | derive from `window.location.origin` | hardcode per env | Works across local/staging/prod; register callbacks in the GitHub app. |
| Live prod cutover | defer to `BK-019` | do it here | Keep this Spec to fix+un-pin+throwaway-verify; live version bump is a gated promotion. |
