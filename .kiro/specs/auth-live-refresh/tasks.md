# Auth Live-Refresh — Tasks

| Property | Value |
| :--- | :--- |
| **Spec ID** | `auth-live-refresh` · **Backlog** `BK-033` (`TSK-073`) · **Branch** `feat/auth-live-refresh` |

> Single-file change (`auth.svelte.ts`). Reference diff exists in the Antigravity clone — reproduce it on a clean `feat/` branch off merged-Spec `main`.

## Tasks

- [x] **T1 — Reactive flag** (R1.1): add `#admin = $state<boolean>` initialized from `pb.authStore.record?.is_admin === true`.
- [x] **T2 — Keep synced** (R1.2): re-derive `#admin` in `pb.authStore.onChange`, after `authWithOAuth2Code`, and set `false` in `signOut()`.
- [x] **T3 — Getter** (R1.3): `get isAdmin() { return this.#authed && this.#admin; }`.
- [x] **T4 — Live refresh** (R2): in `#rehydrate()`, when `pb.authStore.isValid`, `await pb.collection('users').authRefresh()` in try/catch, then re-derive `#admin`; on failure `console.warn` and leave state intact (**fail-closed**).
- [x] **T5 — Fail-closed proof** (R2.2/R3.2): verify a failed/blocked refresh never elevates `#admin`.
- [x] **T6 — Scope floor** (R3.3): diff is `auth.svelte.ts` ONLY — no `data/**`, `app/pocketbase/**`, rules, or `pb_schema.json`.
- [x] **T7 — Self-validate**: `pnpm check` + `pnpm build` clean; `just validate-local` green. Lockstep: CHANGELOG entry for TSK-073; SPRINT_TRACKER coherent.
- [x] **T8 — Open PR** against `main`; STOP-and-hold for `/verification-done` (incl. V1 bootstrap-without-signout + V3 fail-closed + V4 server-gate) → `/review-pr`. Never merge.
