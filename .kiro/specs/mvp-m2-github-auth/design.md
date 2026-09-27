# MVP M2 — GitHub OAuth Sign-In — Design

> Companion to `requirements.md`. Client-side GitHub OAuth via the PocketBase JS SDK, an auth store, account-link by `github_handle`, and a route-guard pattern — confined to auth (no RBAC enforcement, no writes).

---

## 1. Approach: client-side auth on the static SPA

The app is `ssr=false` / `prerender=true`, so auth runs **entirely client-side** via the PocketBase JS SDK's `authStore` (browser-persisted). No server routes, no SSR session. This mirrors how M1's `data.ts` already talks to PocketBase from the browser.

## 2. Shared PocketBase client

Today `data.ts` news up its own `PocketBase(PB_URL)`. To share auth state, extract a **single client module** (`app/web/src/lib/pb.ts`) exporting one `pb` instance; `data.ts` and the new auth store both import it, so `pb.authStore` is consistent app-wide. (Small refactor of `data.ts` to import the shared client — no behavior change to the M1 read path.)

```ts
// lib/pb.ts
import PocketBase from 'pocketbase';
export const pb = new PocketBase(import.meta.env.VITE_PB_URL ?? 'http://127.0.0.1:8090');
```

## 3. Auth store (`lib/auth.svelte.ts`, Svelte-5 runes)

Mirror the `theme.svelte.ts` rune-store pattern. Backed by `pb.authStore`, subscribed via `onChange` so the UI is reactive (R2):

```ts
import { pb } from './pb';
import type { User } from './types';

let user = $state<User | null>(mapRecord(pb.authStore.record));
export const auth = {
  get user() { return user; },
  get isAuthenticated() { return pb.authStore.isValid; },
  async signInWithGitHub() {
    await pb.collection('users').authWithOAuth2({ provider: 'github' }); // R1.1 all-in-one popup
    // onChange updates `user`; link-by-handle resolution in §4
  },
  signOut() { pb.authStore.clear(); }                                     // R1.3
};
pb.authStore.onChange(() => { user = mapRecord(pb.authStore.record); });   // R2.1 reactive
```
- `authStore` persists to `localStorage` by default → returning users stay signed in (R2.2).
- `mapRecord` maps the PB auth record → the UI `User` shape (reusing `types.ts`).

## 4. Account-link by `github_handle` (R3 — link-only)

`authWithOAuth2` returns the auth record + `meta` (incl. the GitHub profile / `rawUser.login`). Linkage strategy:
- The seeded `users` records carry `github_handle`. On sign-in, resolve the app identity by matching the GitHub login to a seeded record's `github_handle` (case-insensitive — OQ-1).
- **Because PocketBase creates/returns an auth record for the OAuth identity**, the "link" for M2 is: treat the signed-in record as the identity, and resolve ownership by `github_handle` against the seeded data (the same key `data.ts` already uses for `owner`).
- **No auto-provision (R3.2):** if the GitHub login matches no seeded `github_handle`, the user is authenticated-but-unlinked — the UI shows a benign "signed in; no owned projects" state. We do **not** pass `createData` to spawn a pending record (that's the deferred OQ-1 path). *(Note: PocketBase's OAuth2 will still create its own auth record for the identity; "unlinked" means it maps to no seeded portfolio owner — M2 does not build onboarding around it.)*

## 5. Auth-reactive header (R4)

In `+layout.svelte`, add an auth control that reads `auth`:
- anon → `Sign in with GitHub` button (calls `auth.signInWithGitHub()`).
- authed → identity (seeded `name`, GitHub avatar if trivially in `meta`) + `Sign out`.
- The public dashboard (`+page.svelte`) is untouched and never gated (R4.1/R4.3) — M1 read parity preserved.

## 6. Route guard (R5 — pattern, public never blocked)

A guard helper usable by future member routes:
```ts
// lib/guard.ts  (or a +layout.ts load in a (member) route group)
import { auth } from './auth.svelte';
export function requireAuth() { if (!auth.isAuthenticated) redirectToSignIn(); }
```
- Applied via a **route group** `src/routes/(member)/+layout.ts` (guarded) while the public dashboard stays outside it — so the guard is real and tested, but no user-facing empty page ships (OQ-2 leaning: a hidden/tested placeholder).
- The guard **never** touches the public route.

## 7. Config & secrets (R7 / `RFC-LAB-000-011` §4.3)

- GitHub OAuth **client id/secret live in the PocketBase admin**, not the frontend. **PocketBase v0.40+ (verified):** OAuth2 is configured **per auth collection**, not in a global Settings menu — go to **Collections → `users` → edit → Options → OAuth2 → enable → Add provider → GitHub**. (The pre-0.23 "Settings → Auth providers" path no longer exists.) Local dev: a dev GitHub OAuth app with callback = the PB OAuth2 redirect. **See the step-by-step in [`docs/guides/developer-guide.md` → GitHub OAuth setup](../../docs/guides/developer-guide.md).**
- Frontend uses only `VITE_PB_URL` (already present).
- `.env.example` documents `GITHUB_OAUTH_CLIENT_ID`/`_SECRET` as **PB-admin-configured** (keys/comment only; already stubbed from RFC-006). No secrets committed.

## 8. Verification (feeds `tasks.md` + `/verification-done`)

Maps to V1–V8: sign-in/out round-trip; linked vs unlinked identity (no row created for unknown); persistence across refresh; public never blocked + guard redirects a member route; superuser intact; gates green. Manual OAuth is inherently human-verified (a popup + GitHub consent) — hence the Human Verification Plan carries the weight here, not automated tests.

## 9. Trade-offs

| Decision | Chosen | Rejected | Why |
| :--- | :--- | :--- | :--- |
| Auth location | client-side (SDK authStore) | server session | App is a static SPA (`ssr=false`); matches M1. |
| Shared client | extract `lib/pb.ts` | two `PocketBase` instances | One `authStore` app-wide; avoids state divergence. |
| First-login | link-by-handle only | auto-provision pending record | M2 is sign-in, not onboarding/RBAC (deferred OQ-1). |
| Guard | route group `(member)` + tested helper | guard the whole app | Public dashboard must never block (R4.1). |
| OAuth flow | `authWithOAuth2` all-in-one popup | manual redirect + code exchange | Simplest; SDK-native; sufficient for local + later Vercel. |
