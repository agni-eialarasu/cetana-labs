# Auth Live-Refresh — Design

| Property | Value |
| :--- | :--- |
| **Spec ID** | `auth-live-refresh` · **Backlog** `BK-033` (`TSK-073`) · **Branch** `feat/auth-live-refresh` |

## 1. Approach

Reference-impl-first: the exact 22-line `auth.svelte.ts` diff is already built and verified in the Antigravity clone. This Spec re-lands it on-protocol under the **security-sensitive** lane (Kiro IDE executor, fail-closed DoD), carved out of the UI pass so an auth change never rides inside a cosmetics PR.

## 2. The change (single file: `app/web/src/lib/auth.svelte.ts`)

1. **Reactive flag** — add `#admin = $state<boolean>(record?.is_admin === true)`.
2. **Keep it synced** — re-derive `#admin` in `onChange`, after `authWithOAuth2Code`, and reset in `signOut`.
3. **Simplify the getter** — `get isAdmin() { return this.#authed && this.#admin; }` (no per-read record access).
4. **Live refresh** — in `#rehydrate()`, when `pb.authStore.isValid`, `await pb.collection('users').authRefresh()` inside a try/catch, then re-derive `#admin`. On failure: `console.warn` and leave state as-is (fail-closed).

## 3. Why fail-closed matters

`authRefresh()` re-fetches the auth record from the server. If it SUCCEEDS, `#admin` reflects the live tier (the bootstrap fix). If it FAILS, the catch must NOT elevate — the pre-existing `#admin` (false for a fresh/non-elevated session) stands. The server `RULE_ADMIN` is the real gate regardless; this is purely about the *client UI* reflecting truth and never over-reflecting it.

## 4. Risks & mitigations

- **Risk: `authRefresh()` adds a network call on every load** → acceptable (one lightweight call; it's how PocketBase recommends keeping a session fresh). It is awaited before identity resolution so there is no flash of wrong state.
- **Risk: a thrown refresh breaking rehydrate** → wrapped in try/catch; identity resolution continues from persisted state.
- **Risk: perceived as a security feature** → explicitly NOT — R3.1/V4 prove the server gate is unchanged and authoritative.

## 5. Executor

**Kiro IDE** (escalated): auth-path change needing behavioral + fail-closed verification. Not Antigravity's cost-first lane.
