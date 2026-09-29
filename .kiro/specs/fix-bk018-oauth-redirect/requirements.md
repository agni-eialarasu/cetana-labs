# Requirements — `fix-bk018-oauth-redirect` (BK-018 fix)

| Property | Value |
| :--- | :--- |
| **Spec ID** | `fix-bk018-oauth-redirect` |
| **Backlog / Task** | `BK-018` fix follow-through · `TSK-055` (SPRINT-10) |
| **Type** | Fix Spec (delivers the H1 direction chosen by `spike-bk018-pb040-oauth`) |
| **Lifecycle** | `PLANNING` → (this Spec merged) → `READY_TO_BUILD` → `/spec-run` |
| **Related** | `spike-bk018-pb040-oauth` (finding), `RFC-LAB-000-011` §4.5 (decision), `RFC-LAB-000-008` M2/M3–M4 (OAuth + owner-write), Decision Journal Entry 011 |
| **Surface** | Kiro IDE (build + human verify against a live 0.40 instance) |

---

## 1. Problem (from the spike, confirmed)

The SvelteKit "Sleek UI" signs in with PocketBase's **all-in-one popup** OAuth flow
(`pb.collection('users').authWithOAuth2({ provider: 'github' })`). That flow receives the
OAuth callback over PocketBase's **realtime SSE channel** (`/api/realtime`). On PocketBase
**0.40.x behind Railway's HTTPS proxy**, the realtime subscribe `POST` is rejected
(`400 "Missing or invalid client id"`) — Railway's proxy does not preserve the SSE
connection affinity 0.40 requires — so sign-in fails. Prod is therefore **pinned to
PocketBase 0.28.4** as a workaround (`app/pocketbase/Containerfile`).

**Fix (H1, chosen):** switch to the **redirect-based `authWithOAuth2Code`** flow, which does a
plain OAuth `code` exchange and **never opens `/api/realtime`** — removing the incompatibility
and letting the backend **un-pin to 0.40+**.

## 2. Goal

Replace the popup OAuth flow with the redirect flow in the static SPA, preserve all existing
auth behavior (identity resolution, owner-write path, session persistence), and un-pin the
PocketBase container to 0.40.x — verified end-to-end against a live 0.40 instance behind
Railway before prod un-pins.

## 3. Constraints & context (must respect)

- **Static SPA, `ssr=false`** (`adapter-static`) — there is **no server** to hold the OAuth
  `state`/`codeVerifier`. The redirect flow must run **entirely client-side**: persist the
  `codeVerifier` (and `state`) across the full-page redirect (e.g. `sessionStorage`) and
  complete `authWithOAuth2Code` on return.
- **Preserve the `github_handle` linkage (R3, M3–M4).** Owner writes depend on
  `pb_hooks/oauth_github_handle.pb.js` populating `github_handle` on sign-in and the app
  resolving the seeded owner by handle. The redirect flow must yield the same OAuth `meta`
  (or an equivalent handle source) so `resolveSeededOwner` still works — and the owner status
  write path (M4) must still succeed.
- **Preserve session persistence (R2.2)** — returning users stay signed in via the
  localStorage-persisted `authStore`.
- **SDK:** `pocketbase ^0.26.0` (already supports `authWithOAuth2Code` + `listAuthMethods`).
- **GitHub OAuth App callback** must include the redirect-return route for each surface
  (local `vite preview`, Vercel preview, Vercel prod). This is console config, captured in the
  Human Verification Plan.
- **Single-PR rule** — all corrections found in verification ride the same PR.
- **Non-destructive** — verify on a 0.40 instance (throwaway/staging) BEFORE the prod
  Containerfile un-pin is relied on for live prod (prod cutover discipline is `BK-019`).

## 4. Acceptance criteria (EARS)

- **R1 — Redirect initiation.** WHEN an anonymous user activates "Sign in with GitHub", THE
  system SHALL obtain the GitHub provider's `authUrl`, `state`, and `codeVerifier` via
  `pb.collection('users').listAuthMethods()`, persist the `codeVerifier` and `state`
  client-side across a full-page navigation, and redirect the browser to the provider's
  `authUrl` with a redirect-return URL pointing back to the app.
- **R2 — Code exchange on return.** WHEN GitHub redirects back to the app with a `code` and
  `state`, THE system SHALL verify the returned `state` matches the persisted `state`, then
  call `authWithOAuth2Code(provider, code, persistedCodeVerifier, redirectURL)` to complete
  authentication, and SHALL clear the persisted `state`/`codeVerifier` afterward.
- **R3 — No realtime dependency.** THE sign-in flow SHALL NOT open or depend on the
  `/api/realtime` channel (verified: no `POST /api/realtime` with `subscriptions:["@oauth2"]`
  occurs during sign-in).
- **R4 — Identity + linkage preserved.** WHEN code exchange succeeds, THE system SHALL resolve
  the signed-in user's GitHub login and set the reactive identity exactly as before (linked
  seeded user, or `unlinked`), such that a linked owner can still edit their own project's
  status (M4 owner-write path succeeds) and a non-owner is still denied.
- **R5 — Session persistence preserved.** WHEN a signed-in user reloads, THE system SHALL keep
  them signed in from the persisted `authStore` (no re-auth), and sign-out SHALL clear it.
- **R6 — Backend un-pinned.** THE PocketBase container (`app/pocketbase/Containerfile`) SHALL
  build and run on **0.40.x** (bump `PB_VERSION`), and the workaround comment SHALL be replaced
  with a reference to this fix + `RFC-LAB-000-011` §4.5.
- **R7 — End-to-end on 0.40 behind Railway.** WHEN sign-in is exercised against a live 0.40
  instance behind Railway's proxy, THE full flow SHALL complete (no `/api/realtime` 400, no
  500) and land the user signed-in.
- **R8 — Lockstep + hygiene.** THE change SHALL pass `make validate-local` (5-pillar +
  type-check + build) and update any docs that referenced the 0.28.4 pin as the current state
  (developer-guide deployment note, `.env.example` OAuth note if affected).

## 5. Out of scope

- Production cutover to dedicated prod instances (`BK-019`).
- Staging deploy automation / `make setup-staging` (`BK-017`).
- Any RBAC change (the owner-write rule and 3-tier minimum RBAC are unchanged).
- OAuth providers other than GitHub.
- Terminal-state edit policy (`BK-016`).

## 6. Human Verification Plan (authored here; run at `/verification-done`)

> Experiential, human-executable — distinct from the EARS self-validation. Run against a
> **live 0.40 instance behind Railway** (the spike's throwaway is fine).

- **V1 — Un-pinned backend is live on 0.40.** Confirm the 0.40 PocketBase instance is running
  (health 200) with the `github_handle` hook loaded and GitHub OAuth configured; GitHub OAuth
  App callback includes the app's redirect-return URL.
- **V2 — Sign-in completes with no realtime call.** From the app (pointed at the 0.40 backend),
  click "Sign in with GitHub"; complete the GitHub consent. In DevTools → Network, confirm:
  full-page redirect to GitHub and back, `authWithOAuth2Code` succeeds, and **no
  `POST /api/realtime`** occurs. Land signed-in (no 500).
- **V3 — Identity + linkage.** Signed in as a seeded owner, confirm the header shows the linked
  name (not `unlinked`), and the owner can **edit and save their own project's status** (M4
  path). Confirm a non-owner (or unlinked account) is denied the write.
- **V4 — Session persistence.** Reload the page — still signed in. Sign out — returns to
  anonymous; reload stays anonymous.
- **V5 — Regression: public read.** Anonymous (signed out) still sees the public portfolio
  (M1 read tier unaffected).
