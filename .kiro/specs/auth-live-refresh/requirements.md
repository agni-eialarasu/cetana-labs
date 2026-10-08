# Auth Live-Refresh (reactive is_admin on rehydrate) — Requirements

| Property | Value |
| :--- | :--- |
| **Spec ID** | `auth-live-refresh` |
| **Feature** | Make the client auth store reflect the live `is_admin` tier without a manual sign-out: hold `is_admin` as reactive Svelte 5 state and `authRefresh()` the record on page rehydrate, so a tier change (e.g. a superuser toggling `is_admin`) takes effect on next load. |
| **Backlog** | `BK-033` (`TSK-073`, SPRINT-13) |
| **Work class** | **Sprint deliverable + security-sensitive** (auth path) → **FULL gate**, with explicit fail-closed criteria as the DoD. |
| **Depends on** | `BK-030` (`is_admin` tier + rules — merged `d4f9734`), `BK-031` (`auth.isAdmin` getter — merged `#78`). |
| **RFCs** | `RFC-LAB-000-008` A1 (`is_admin`), `RFC-LAB-000-008` (RBAC/auth). |
| **Executor role** | **Kiro IDE** (escalated per `RFC-LAB-000-014` — auth-path change; needs behavioral verification, not cost-first routing). One-line reason: touches the live auth record read + a network `authRefresh` on every rehydrate. |
| **Source** | Operator session 2026-10-08. **Reference implementation already built & verified in the Antigravity clone** (the 22-line `auth.svelte.ts` diff); carved OUT of the UI pass because it is a different risk class. This Spec re-lands it on-protocol with proper auth DoD. |

---

## 1. Introduction

BK-031 added `get isAdmin()` reading `pb.authStore.record?.is_admin`. Two gaps remain:
1. **`isAdmin` is computed on read, not reactive state** — if the underlying record changes between renders without an `onChange`, the UI can lag.
2. **The persisted record is never re-fetched on page load** — so when an admin is first bootstrapped (superuser toggles `is_admin=true`), an already-signed-in session keeps the *stale* record (no admin UI) until a full sign-out/in. That is the exact friction hit during BK-030/031 bootstrap testing.

The fix: hold `#admin` as `$state`, keep it synced in `onChange` / `signOut` / the OAuth code-exchange, and call `pb.collection('users').authRefresh()` on `#rehydrate()` when a valid token exists, so the record (and `is_admin`) is live on load.

## 2. Current-state facts (verified 2026-10-08 on `main`)
- **`app/web/src/lib/auth.svelte.ts`** — `#authed` is `$state`; `get isAdmin()` computes `this.#authed && pb.authStore.record?.is_admin === true` on each read. `#rehydrate()` rebuilds identity from persisted state but does **NOT** call `authRefresh()` — the record is whatever localStorage held.
- **Server rule** — `RULE_ADMIN` (BK-030, `pb_provision.py`) is the real gate; this change is **client UX only** (it does not grant anything the server wouldn't).

## 3. Requirements (EARS acceptance criteria = Definition of Done)

### R1 — Reactive admin state
- **R1.1** The store SHALL hold `#admin` as `$state<boolean>`, initialized from `pb.authStore.record?.is_admin === true`.
- **R1.2** `#admin` SHALL be re-derived (from the auth record) in `pb.authStore.onChange`, after a successful OAuth code-exchange, and reset to `false` in `signOut()`.
- **R1.3** `get isAdmin()` SHALL return `this.#authed && this.#admin` — reactive, no per-read record access.

### R2 — Live refresh on rehydrate
- **R2.1** `#rehydrate()` SHALL, WHEN `pb.authStore.isValid`, call `pb.collection('users').authRefresh()` and then re-derive `#admin` from the refreshed record — so a tier change made while signed in takes effect on next page load without a manual sign-out.
- **R2.2** WHEN `authRefresh()` fails (network error, revoked token), the store SHALL **fail closed**: it SHALL NOT elevate `#admin`, SHALL log a warning, and SHALL leave the existing (non-elevated or cleared) state intact — a failed refresh never grants admin.

### R3 — Security invariants (the heart of the DoD)
- **R3.1** This change SHALL grant NO client-side authority the server does not already enforce — `RULE_ADMIN` remains the real gate. A user who flips `#admin` in devtools still cannot write server-side.
- **R3.2** A revoked/expired token on rehydrate SHALL result in `isAdmin === false` (fail-closed), never a stale `true`.
- **R3.3** No change to any `data/**`, `app/pocketbase/**`, PocketBase rule, or `pb_schema.json` — client-only.

## 4. Human Verification Plan (the `/review-pr` evidence)
- **V1** — Sign in as a non-admin → no admin UI. A superuser toggles `is_admin=true` on that user → **reload the page** (no sign-out) → admin UI now appears. (R2.1 — the headline fix.)
- **V2** — Toggle `is_admin=false` again → reload → admin UI gone. (R1/R2 symmetry.)
- **V3** — **Fail-closed:** with devtools, block/kill the `authRefresh` request on load (or revoke the token) → the UI does NOT show admin; a warning is logged; the app stays usable as non-admin. (R2.2/R3.2)
- **V4** — **Server gate holds:** a non-admin who forces `isAdmin` true client-side (devtools) and attempts a `settings`/`projects` write is still denied by `RULE_ADMIN`. (R3.1)
- **V5** — `just validate-local` green; `pnpm build`/`check` clean; diff is `auth.svelte.ts` only (no backend/`data/`). (R3.3)
