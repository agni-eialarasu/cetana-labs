# Tasks — `fix-bk018-oauth-redirect`

> Executed by `/spec-run fix-bk018-oauth-redirect` (Kiro IDE) after this Spec is merged to
> `main` (merge-first → `READY_TO_BUILD`). Each task is self-contained and maps to the EARS
> acceptance criteria in `requirements.md`. Branch: `fix/bk018-oauth-redirect`.

- [ ] **T1 — Redirect initiation in the auth store (R1)**
  - In `app/web/src/lib/auth.svelte.ts`, rewrite `signInWithGitHub()` to: call
    `pb.collection('users').listAuthMethods()`, select the `github` provider, compute
    `redirectURL` from `window.location.origin` + SvelteKit `base`, persist `state` +
    `codeVerifier` to `sessionStorage` (namespaced keys), and `window.location.assign(authUrl + redirectURL)`.
  - _Verify:_ clicking sign-in navigates to GitHub with a `redirect_uri` back to the app.

- [ ] **T2 — Code exchange on return (R2, R3, R4)**
  - Add `completeOAuthRedirect()` that runs on app load when `?code=&state=` are present:
    read persisted `state`/`codeVerifier`, assert `state` matches (else abort → stay anon),
    call `authWithOAuth2Code('github', code, codeVerifier, redirectURL)`, clear
    `sessionStorage`, `history.replaceState` to strip the query, then reuse the existing
    `#resolve(loginFromMeta(res.meta), res.meta)` path.
  - Wire it into the constructor ahead of the rehydrate branch.
  - _Verify:_ return leg completes, identity resolves, no `POST /api/realtime` in Network.

- [ ] **T3 — AuthControl adjustment (R4 UI parity)**
  - Update `AuthControl.svelte` `signIn()` for the redirect (busy state + redirect-failed
    error path); update the "popup" comment to "redirect flow". No markup change.
  - _Verify:_ button shows "Signing in…" then redirects; signed-in and unlinked states render
    identically to before.

- [ ] **T4 — Un-pin the PocketBase container (R6)**
  - In `app/pocketbase/Containerfile`, bump `ARG PB_VERSION` 0.28.4 → 0.40.x; replace the
    workaround comment with a one-line note referencing this fix + `RFC-LAB-000-011` §4.5;
    keep the `pb_hooks/` COPY.
  - _Verify:_ image builds; `pocketbase --version` in the built image reports 0.40.x.

- [ ] **T5 — Docs lockstep (R8)**
  - Grep `docs/` + `app/web/.env.example` for "0.28.4" / "popup" OAuth references; update stale
    statements to "0.40+ via redirect OAuth flow". No new env var.
  - _Verify:_ no doc still describes 0.28.4 as the current/required pin.

- [ ] **T6 — Local validation (R8)**
  - Run `make validate-local` (5-pillar governance + `pnpm check` type-check + `pnpm build`).
    Fix anything red.
  - _Verify:_ validation green; SPA builds.

- [ ] **T7 — Open PR + emit Human Verification Plan (hand-off STOP)**
  - Open a PR (`gh api`, per `RFC-LAB-000-004`) from `fix/bk018-oauth-redirect`; body includes
    the `requirements.md` §6 Human Verification Plan and links the spike finding + RFC-011 §4.5.
  - STOP in `IN_VERIFICATION` — the human runs V1–V5 against a live 0.40 instance; fixes ride
    this same PR; then `/verification-done`.

> **Note (R7 precondition):** V1–V2/V7 require a **live 0.40 instance behind Railway**. The
> spike's throwaway (`truthful-prosperity-staging.up.railway.app`) can be reused (seed it, set
> the GitHub callback + the app's `VITE_PB_URL`). Prod's Containerfile un-pin (T4) is committed
> here, but **relying on it for live prod is gated by `BK-019`** (prod cutover) — this Spec
> proves the fix on 0.40; it does not itself flip live prod.
