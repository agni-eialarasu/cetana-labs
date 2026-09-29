# Design — `fix-bk018-oauth-redirect`

## 1. Approach

Replace the SDK's all-in-one popup (`authWithOAuth2`) with PocketBase's **manual redirect
flow** (`listAuthMethods` → provider redirect → `authWithOAuth2Code`), implemented **entirely
client-side** because the app is a static SPA (`ssr=false`, `adapter-static`). The popup flow's
dependency on the realtime SSE channel — which is what breaks through Railway's proxy on 0.40
(confirmed by the spike; corroborated by PocketBase discussion #4514: the all-in-one call needs
a long-lived SSE connection) — is thereby removed entirely.

Reference: PocketBase JS SDK redirect flow — `listAuthMethods()` yields per-provider
`authUrl` / `state` / `codeVerifier`; after the provider redirects back with a `code`, call
`authWithOAuth2Code(provider, code, codeVerifier, redirectURL)`. The `codeVerifier` MUST come
from the *same* `listAuthMethods()` call that produced the `state` (discussion #2476), so it
must survive the full-page redirect. *(Sources: PocketBase GitHub discussions #4990, #3849,
#2476, #4514 — rephrased for compliance.)*

## 2. The redirect round-trip (client-side, static SPA)

```
[anon] click Sign in
   │  listAuthMethods() → { authUrl, state, codeVerifier } for provider "github"
   │  sessionStorage.set(state, codeVerifier, redirectURL)
   ▼  window.location = authUrl + redirectURL      ── full-page redirect ──▶ GitHub consent
                                                                                   │
   ┌───────────────────────────────────────────────────────────────────  redirect back
   ▼  app boots at redirect-return route with ?code=…&state=…
   │  read sessionStorage; assert returned state === persisted state
   │  authWithOAuth2Code("github", code, codeVerifier, redirectURL)
   │  → authStore populated (token persisted to localStorage — R5)
   │  clear sessionStorage
   ▼  resolve identity (github_handle → seeded owner) → reactive UI [signed in]
```

- **Redirect-return route.** The SPA already renders under one shell; the return can be handled
  on the existing entry (`/`) by detecting `?code=&state=` on load, or via a dedicated
  `/auth/callback` route. **Decision:** handle on load in the auth store's constructor path
  (no new route needed for a hash/adapter-static SPA) — simplest, and avoids adapter-static
  fallback routing concerns. Revisit to a dedicated route only if callback detection on `/`
  proves noisy.
- **State/verifier persistence:** `sessionStorage` (cleared after exchange; scoped to the tab;
  not needed after sign-in). Keys namespaced (`cetana-oauth-state`, `cetana-oauth-verifier`).

## 3. Code changes (grounded in current files)

### 3.1 `app/web/src/lib/auth.svelte.ts` — the core change
- **Replace** `signInWithGitHub()`'s body:
  - was: `await pb.collection('users').authWithOAuth2({ provider: 'github' })`
  - now: `listAuthMethods()` → find the `github` provider → persist `state` + `codeVerifier`
    to `sessionStorage` → `window.location.assign(authUrl + redirectURL)`. (Function no longer
    resolves identity itself — it hands off to the redirect; identity resolution happens on
    return.)
- **Add** `completeOAuthRedirect()` — called on app load when `?code=&state=` present:
  read+validate persisted `state`, call
  `pb.collection('users').authWithOAuth2Code('github', code, codeVerifier, redirectURL)`,
  clear `sessionStorage`, then run the existing `#resolve(login, meta)` with the result's
  `meta` (same `loginFromMeta` extraction → same `resolveSeededOwner`). Strip `code`/`state`
  from the URL after (history.replaceState) so a reload doesn't re-exchange.
- **Constructor:** if the URL has an OAuth callback, `void this.completeOAuthRedirect()` before
  the existing rehydrate path; otherwise unchanged.
- **Unchanged:** `mapRecord`, `resolveSeededOwner`, `loginFromMeta`, `#resolve`, `signOut`,
  `#rehydrate`, the `$state` reactivity, and the `authStore.onChange` wiring (R4/R5 preserved).

### 3.2 `app/web/src/lib/components/AuthControl.svelte`
- `signIn()` now triggers a redirect (no `await` resolves to a signed-in state in the same tick).
  Adjust the `busy` handling: set `busy=true` before redirect; the `finally` reset is moot after
  navigation, but keep it for the error path (popup-closed semantics change to redirect-failed).
- Comment update: "all-in-one popup" → "redirect flow". No visual/markup change (R4 UI parity).

### 3.3 `app/pocketbase/Containerfile` — un-pin (R6)
- `ARG PB_VERSION=0.28.4` → **`ARG PB_VERSION=0.40.4`** (or latest verified 0.40.x).
- Replace the multi-line 0.28.4-workaround comment with: a one-line note that 0.40+ is
  supported via the redirect OAuth flow (`fix-bk018-oauth-redirect`), referencing
  `RFC-LAB-000-011` §4.5. Keep the `pb_hooks/` COPY (still required for `github_handle`).

### 3.4 Docs touched (R8, lockstep)
- `docs/guides/developer-guide.md` deployment/OAuth note — if it states "pinned 0.28.4", update
  to "0.40+ via redirect OAuth".
- `app/web/.env.example` — the OAuth note mentions the popup/SDK reading provider config; adjust
  wording only if it implies the popup flow. No new env var is introduced (redirect URL is
  derived from `window.location.origin` + base).

## 4. Why not the alternatives
- **H2 (make SSE survive Railway's proxy):** depends on Railway proxy internals we don't
  control; leaves a fragile SSE dependency on the critical sign-in path. Rejected in the spike.
- **Server-side callback (SvelteKit `+server`):** not available — `adapter-static`, `ssr=false`.
  Client-side persistence of the verifier is the correct pattern for a static SPA.
- **Dedicated `/auth/callback` route:** viable but adds an adapter-static fallback-routing
  concern; on-load detection at `/` is simpler and sufficient. Kept as a fallback option.

## 5. Risks
| Risk | Mitigation |
| :--- | :--- |
| `codeVerifier` lost across redirect (wrong storage / cleared) | `sessionStorage` persists across same-tab navigation; explicit state-match assertion (R2) fails closed → stays anonymous |
| OAuth `meta` shape differs between popup and code flow (breaks handle resolution) | `authWithOAuth2Code` returns the same `RecordAuth` with `meta`; `loginFromMeta` already falls back to the auth record's `github_handle` (populated by the hook) — R4 verified in V3 |
| GitHub callback URL mismatch per surface | Enumerate all redirect-return URLs (local preview, Vercel preview, Vercel prod) in the GitHub OAuth App; captured in V1 |
| Reload re-triggers code exchange | Strip `code`/`state` from URL via `history.replaceState` after exchange |
| Un-pin regresses something else on 0.40 | V2–V5 exercise the full authed path on 0.40 before relying on it for prod (prod cutover is separately gated by BK-019) |

## 6. Verification hooks (map to EARS)
- R1/R2/R3 → V2 (Network shows redirect round-trip, `authWithOAuth2Code`, no `/api/realtime`).
- R4 → V3 (linked identity + owner write succeeds; non-owner denied).
- R5 → V4 (reload persists; sign-out clears).
- R6/R7 → V1 + V2 (0.40 backend live; end-to-end completes behind Railway).
- R8 → `make validate-local` + docs grep.
