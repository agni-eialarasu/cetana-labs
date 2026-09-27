# MVP M2 — GitHub OAuth Sign-In — Requirements

| Property | Value |
| :--- | :--- |
| **Spec ID** | `mvp-m2-github-auth` |
| **Feature** | MVP Phase M2 (`RFC-LAB-000-008` §6) — GitHub OAuth sign-in, auth store, account-link by `github_handle`, route guard |
| **Backlog** | `TSK-049` (SPRINT-09), epic `BK-011` |
| **Status** | 🟡 Proposed (contract authored on Kiro Web; execution on Kiro IDE) |
| **RFCs** | `RFC-LAB-000-006` (auth/RBAC — §2 identity/linking, §5 UI flow), `RFC-LAB-000-008` (MVP §5 minimum auth, §6 M2), `RFC-LAB-000-005` (Sleek UI) |
| **Executor role** | Delegated-agent / onboarded-dev (full Spec) |

---

## 1. Introduction

M1 wired the UI to live PocketBase (read). **M2 adds identity:** a user can **sign in with GitHub**, the UI **reflects auth state**, and the authenticated user is **linked to their seeded `users` record by `github_handle`** so ownership resolves later. Member-only views are **guarded** (redirect to sign-in), while the public dashboard never blocks.

**M2 is deliberately narrow (scope boundary, `RFC-LAB-000-008` §6):**
- **In:** sign-in/sign-out flow (PocketBase OAuth2 via the JS SDK), an auth store, account-link by `github_handle`, a route guard for member views, and auth-reactive UI (header shows signed-in identity / sign-in button).
- **Out (explicitly deferred):** RBAC *rule enforcement* (M3), owner *write* path (M4), deploy (M5). M2 may *reveal* member-scoped detail in the UI, but enforcement of who-can-do-what is M3.

## 0. Preconditions (preflight — verify BEFORE any change; enforced by `tasks.md` T0)

- **P1 — Surface:** Kiro **IDE / local** (runs the stack + configures OAuth). `/env-doctor` IDE-ready.
- **P2 — Toolchain:** Node 22 + pnpm ~10.27; the `pocketbase` binary + JS SDK (`pocketbase@^0.26`, already a dep from M1).
- **P3 — Branch:** feature branch `feat/mvp-m2-github-auth` off up-to-date `main`; clean tree; not `main`/`master`.
- **P4 — Merge-first:** this Spec merged to `main` before `/spec-run`.
- **P5 — Baseline green:** `validate_portfolio.py`, `generate_status_json.py --check`, `project_validate.py --allow-dirty`, and `pnpm --dir app/web check && build` all pass before changes.
- **P6 — Local stack + GitHub OAuth app:** `make setup` + `make start-local` (PocketBase `:8090`, SvelteKit `:5173`); a **GitHub OAuth app** (dev) exists with client id/secret and callback set to the PocketBase redirect — configured in the PB admin UI. *(Secrets stay local/uncommitted — `RFC-LAB-000-011` §4.3.)*

## 2. Current-state facts (of record — verified against the repo)

- **No auth code exists today** — M2 is greenfield auth. The app is a static SPA (`ssr=false`, `prerender=true`), so auth is **client-side** via the PocketBase JS SDK.
- **Data layer:** `app/web/src/lib/data.ts` holds the `PocketBase` client pattern (`VITE_PB_URL`); M2 adds an **auth store** alongside it (mirror the existing lib module style; `theme.svelte.ts` shows the Svelte-5 rune store pattern).
- **Users collection:** the PB `users` auth collection has the custom `github_handle` field (from `pb_provision.py`); seeded users all carry a `github_handle`.
- **SDK surface (verified):** `pb.collection('users').authWithOAuth2({ provider: 'github' })` (all-in-one popup flow); `pb.authStore` (`.token`, `.record`, `.isValid`, `.onChange(cb)`, `.clear()`).
- **Routes:** `+layout.svelte` (header/nav), `+page.*` (dashboard). No member-only route exists yet — M2 introduces the guard pattern for when member views land.

## 3. Requirements (EARS acceptance criteria = Definition of Done)

### R1 — GitHub OAuth sign-in flow
- **R1.1** WHEN a user clicks "Sign in with GitHub", the system SHALL start the PocketBase OAuth2 flow via `pb.collection('users').authWithOAuth2({ provider: 'github' })`.
- **R1.2** WHEN OAuth succeeds, the SDK SHALL persist the auth token/record in `pb.authStore`, and the system SHALL reflect signed-in state without a full reload.
- **R1.3** WHEN a user clicks "Sign out", the system SHALL clear `pb.authStore` and revert to the anonymous state.

### R2 — Auth store (client-side, reactive)
- **R2.1** The system SHALL provide an **auth store** (`app/web/src/lib/auth.svelte.ts` or similar) exposing reactive `user`, `isAuthenticated`, `signInWithGitHub()`, `signOut()`, backed by `pb.authStore` and subscribed via `onChange` so the UI reacts to token changes.
- **R2.2** The store SHALL rehydrate from a persisted `authStore` on load (a returning user stays signed in until token expiry/sign-out).

### R3 — Account-link by `github_handle` (link-only; no auto-provision — decision-of-record)
- **R3.1** WHEN a user authenticates via GitHub, the system SHALL resolve their app identity by matching the GitHub login to the seeded `users` record's `github_handle`.
- **R3.2** IF no seeded record matches, the system SHALL treat the user as **authenticated-but-unlinked** (signed in, but owns no projects) and surface a clear, non-error state — it SHALL NOT auto-create a `users` record. *(Auto-provisioning a pending record is explicitly deferred — `RFC-LAB-000-006` OQ-1; noted for a later phase.)*

### R4 — Auth-reactive UI
- **R4.1** WHILE anonymous, the header SHALL show a "Sign in with GitHub" action; the public dashboard SHALL remain fully visible (never blocked).
- **R4.2** WHILE authenticated, the header SHALL show the signed-in identity (name/handle/avatar) and a "Sign out" action.
- **R4.3** The public/summary portfolio view SHALL render identically for anon and authed users in M2 (detail-tiering/enforcement is M3) — no regression to the M1 read path.

### R5 — Route guard (pattern established; public never blocked)
- **R5.1** The system SHALL provide a **route-guard mechanism** for member-only views (redirect to sign-in when `!isAuthenticated`), applied to any member route.
- **R5.2** Since M2 ships no member-only *page* yet, the guard SHALL be implemented and unit-exercised (e.g. a guarded placeholder or a documented helper) so M3/M4 can adopt it without rework; the **public dashboard route SHALL NOT be guarded**.

### R6 — Superuser escape hatch preserved
- **R6.1** The PocketBase superuser/admin path SHALL remain available (OAuth misconfig must not lock out the control-hub owner) — `RFC-LAB-000-006` §5.

### R7 — Config & secrets
- **R7.1** The GitHub OAuth client id/secret SHALL be configured in the PocketBase admin (not the frontend); the frontend needs only `VITE_PB_URL` (already present).
- **R7.2** `.env.example` (root + `app/web`) SHALL document the GitHub OAuth vars as PB-admin-configured (keys only, no secrets), consistent with `RFC-LAB-000-011` §4.3.

### R8 — Quality gates green
- **R8.1** `pnpm --dir app/web check` (svelte-check + tsc), `pnpm --dir app/web build`, `pnpm --dir app/web lint`, and `make validate-local` SHALL pass. The M1 snapshot-fallback read path SHALL remain intact.

## 4b. Human Verification Plan (emitted by `/spec-run`; recorded by `/verification-done`)

Run against the local stack with the dev GitHub OAuth app configured:
- **V1 — Sign in:** click "Sign in with GitHub" → GitHub OAuth → returns signed-in; header shows your identity.
- **V2 — Linked identity:** signed-in user is linked to the seeded `users` record by `github_handle` (e.g. your `arasu`/handle resolves to your LAB-000 owner record).
- **V3 — Unlinked path:** sign in with a GitHub account NOT in `data/users.json` → authenticated-but-unlinked, clear non-error state, **no** new `users` row created.
- **V4 — Sign out:** click "Sign out" → reverts to anonymous; header shows the sign-in action.
- **V5 — Persistence:** refresh while signed in → stays signed in (authStore rehydrates).
- **V6 — Public never blocked:** anonymous dashboard renders fully (M1 read parity); route guard redirects only a member-only view.
- **V7 — Superuser intact:** PB admin UI login still works.
- **V8 — Gates:** `pnpm check`/`build`/`lint` + `make validate-local` green.

**Verdict rule:** V1–V8 pass (fixes on the same PR, re-verified) before `/verification-done`.

## 5. Out of Scope (deferred)
- RBAC rule enforcement / per-collection API-rule matrix beyond what exists (M3).
- Owner write path for project status (M4).
- Deploy / OAuth on the Vercel+GCP domain (M5 / `RFC-LAB-000-011`) — M2 is local; redirect URLs for prod are an M5 concern.
- Auto-provisioning pending `users` records for unknown GitHub logins (`RFC-LAB-000-006` OQ-1 — deferred).
- Email/password auth (fallback only; not required — `RFC-LAB-000-008` §5).
- The full 5-role `memberships` model / audit trail (deferred by `RFC-LAB-000-008`).

## 6. Open Questions (resolve at build start)
1. **`github_handle` matching key:** match on the OAuth `meta.rawUser` login vs. a stored provider id. *(Leaning: match by GitHub `login` → `github_handle`, case-insensitive; note the record is the seed source of truth.)*
2. **Guard demonstration:** ship a minimal guarded placeholder route vs. a documented+tested guard helper with no page yet. *(Leaning: a tested helper + a hidden placeholder, so M3 adopts it directly without shipping a user-facing empty page.)*
3. **Avatar/display:** use GitHub avatar from OAuth meta vs. seeded name only. *(Leaning: prefer seeded `name`; show GitHub avatar if trivially available.)*
