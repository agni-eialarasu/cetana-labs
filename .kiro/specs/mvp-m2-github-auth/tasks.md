# MVP M2 — GitHub OAuth Sign-In — Tasks

> Ordered plan for `/spec-run` (Build). Execute on **Kiro IDE**. Do NOT merge; open a PR, emit the Human Verification Plan, STOP in `IN_VERIFICATION`.

## Execution header (self-describing — read by `/spec-run`)

| Field | Value |
| :--- | :--- |
| **Spec id** | `mvp-m2-github-auth` |
| **Kickoff (IDE one-liner)** | `/spec-run mvp-m2-github-auth` |
| **Surface** | Kiro **IDE** (runs the stack + configures GitHub OAuth in PB admin) |
| **Branch to create** | `feat/mvp-m2-github-auth` (off up-to-date `main`, per `RFC-LAB-000-004`) |
| **Base for PR** | `main` |
| **Preflight** | Requirements §0 (P1–P6, incl. a dev GitHub OAuth app) + task **T0** — STOP on any ❌ |
| **Self-validation target** | `requirements.md` EARS R1–R8 |
| **Human Verification Plan** | `requirements.md` §4b (V1–V8) — OAuth is human-verified (popup + consent) |
| **On completion** | Open PR via `gh api`, emit the Verification Plan, STOP → `/verification-done` → `/review-pr` (never merge) |
| **Executor role** | Delegated-agent / onboarded-dev |

---

- [ ] **T0 — Preflight (gate — STOP on any ❌)**
  - Surface=IDE (`/env-doctor`); clean tree; branch `feat/mvp-m2-github-auth` off fresh `main`; this Spec on `main` (merge-first).
  - Baseline green (P5): three validators + `pnpm check`/`build`.
  - **P6:** local stack up (`make setup` + `make start-local`); a **dev GitHub OAuth app** exists and is configured in the PB admin (client id/secret + callback = PB OAuth2 redirect). If absent, STOP with setup instructions (do not fabricate secrets).
  - _Refs: §0._

- [ ] **T1 — Extract the shared PocketBase client (`lib/pb.ts`)**
  - Create `app/web/src/lib/pb.ts` exporting one `pb` instance (reads `VITE_PB_URL`); refactor `data.ts` to import it (no behavior change to the M1 read/fallback path).
  - _Refs: design §2._

- [ ] **T2 — Auth store (`lib/auth.svelte.ts`)**
  - Svelte-5 rune store (mirror `theme.svelte.ts`): reactive `user` / `isAuthenticated`; `signInWithGitHub()` (`pb.collection('users').authWithOAuth2({ provider:'github' })`); `signOut()` (`pb.authStore.clear()`); subscribe `pb.authStore.onChange`; rehydrate on load.
  - _Refs: R1, R2, design §3._

- [ ] **T3 — Account-link by `github_handle` (link-only)**
  - Resolve the signed-in identity to a seeded `users` record by matching GitHub login → `github_handle` (case-insensitive, OQ-1). Unknown login ⇒ authenticated-but-unlinked (benign state); **do NOT auto-create** a record (R3.2).
  - _Refs: R3, design §4._

- [ ] **T4 — Auth-reactive header (`+layout.svelte`)**
  - Anon: "Sign in with GitHub" action + full public dashboard. Authed: identity (seeded `name`, avatar if trivially in `meta`) + "Sign out". Public route never gated; M1 read parity preserved.
  - _Refs: R4, design §5._

- [ ] **T5 — Route-guard pattern (`(member)` group)**
  - Add a `src/routes/(member)/+layout.ts` guard (redirect to sign-in when `!isAuthenticated`) + a hidden/tested placeholder so the pattern is real and adoptable by M3/M4; the public dashboard route stays outside the group (never guarded).
  - _Refs: R5, design §6._

- [ ] **T6 — Config & secrets docs**
  - `.env.example` (root + `app/web`): document `GITHUB_OAUTH_CLIENT_ID`/`_SECRET` as **PB-admin-configured** (keys/comment only; no secrets). Confirm frontend needs only `VITE_PB_URL`.
  - Verify the PB superuser/admin path still works (R6).
  - _Refs: R7, R6, design §7._

- [ ] **T7 — Quality gates green**
  - `pnpm --dir app/web check && build && lint`; `make validate-local`. M1 snapshot fallback intact.
  - _Refs: R8._

- [ ] **T8 — Commit, open PR, emit Human Verification Plan, STOP**
  - Branch `feat/mvp-m2-github-auth`; semantic commit referencing `TSK-049` / `BK-011` M2.
  - Open PR into `main` via `gh api`; CI green; emit §4b plan (V1–V8); STOP in `IN_VERIFICATION`. **Never merge.**
  - Note in the PR: OAuth is human-verified (popup + GitHub consent) — the Verification Log carries the evidence.
  - _Refs: R-all, `RFC-LAB-000-009` §3.2._

- [ ] **T9 — After human verification passes: `/verification-done`**
  - Human runs V1–V8 (sign in/out, linked + unlinked paths, persistence, public-not-blocked, superuser); fixes ride the same PR; on pass, `/verification-done` writes the Verification Log to this Spec's `REPORT.md` → `IN_REVIEW` → `/review-pr`.
  - _Refs: `RFC-LAB-000-009` §3.2._

---

### Governance lockstep reminder (Record, after merge)
Note M2 in CHANGELOG (`TSK-049`); M2 **unblocks M3 (RBAC enforcement), M4 (owner writes), the authenticated M5 deploy, and `BK-014` admin CRUD**. Keep the M2 scope line honest — this is sign-in only, not RBAC/writes.
