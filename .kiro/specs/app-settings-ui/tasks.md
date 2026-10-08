# App Settings UI — Tasks (`/spec-run app-settings-ui`)

> Executor = **Antigravity** (SvelteKit form UI over an existing SDK write path; cost-first per `RFC-LAB-000-014`). Consumes `BK-030` (`is_admin` + `settings` write rule, merged). STOP-and-hold at the PR; never merge.

---

## T0 — Preflight + baseline (STOP on failure)
- [x] Surface = an Executor clone; `just setup && just start-local` up; Node/pnpm + PocketBase on PATH.
- [x] This Spec merged to `main` (merge-first).
- [x] `BK-030` present on `main`: `users.is_admin` field + `settings` `RULE_ADMIN` write rule (verify `scripts/pb_provision.py`).
- [x] **Bootstrap a local admin:** superuser (admin UI `/_/`) toggles `is_admin=true` on a test user (needed to verify V2/V3).
- [x] Create `feat/app-settings-ui` off up-to-date `main`; clean tree; not `main`.
- [x] Baseline: `pnpm --dir app/web check && build` + 5 validators green.

## T1 — Surface `is_admin` in the auth store → R1
- [x] Add `get isAdmin(): boolean` to `AuthState` (`auth.svelte.ts`) = `this.#authed && pb.authStore.record?.is_admin === true`. *(R1.1)*
- [x] Confirm it's independent of `isUnlinked`/`user` (admin need not be a seeded owner). *(R1.2)*

## T2 — Settings write layer → R2.2/R2.3
- [x] In `settings.svelte.ts`, add `loadEditableSettings()` returning rows **with `id`** (`getFullList`, keep `r.id`). *(R2.2)*
- [x] Add `updateSetting(id, value)` wrapping `pb.collection('settings').update(id, { value })`. *(R2.3)*
- [x] Leave the read-only getters + `loadSettings()` untouched. *(R5.2)*

## T3 — Admin-gated editor route → R2.1/R2.4/R3
- [x] Create `app/web/src/routes/admin/settings/+page.svelte`: `{#if auth.isAdmin}` render the form; `{:else}` "Not authorized" + link to `base/`. *(R2.1)*
- [x] Pre-fill fields from `loadEditableSettings()`: `app_name`/`app_description` (text), `logo_*_url` (url + validation, empty allowed). *(R2.2/R3.2)*
- [x] On save: diff → `updateSetting` per changed row → success/error feedback → re-run `loadSettings()` so branding updates live (no reload). *(R2.3/R2.4/R3.1)*
- [x] Theme-safe styling with existing design tokens (no fixed palette).

## T4 — Entry point → R4
- [x] Add `{#if auth.isAdmin}` Settings link in the BK-027 header center-nav slot (or user menu); non-admins see nothing (slot stays empty). *(R4.1)*

## T5 — Gates, lockstep, PR → R5/R6
- [x] `pnpm --dir app/web check && build`, `just validate-local`, 5 validators green. *(R6.1)*
- [x] Scope floor: `app/web/**` only (auth getter + settings write layer + editor route + nav entry). **NO** backend/`data`/schema/rule change. *(R5.3/R6.2)*
- [x] Lockstep: `CHANGELOG.md` `[Unreleased]` → Added (BK-031/TSK-070); flip `SPRINT_TRACKER.md` TSK-070 at build.
- [x] Append `REPORT.md` (summary + the V1–V6 Human Verification Plan, incl. the V4 server-gate check, left for `/verification-done`).
- [x] Open PR `feat/app-settings-ui → main`; self-validate vs EARS DoD; STOP-and-hold (never merge).

## Post-build (back on the Operator)
- `/verification-done` records V1–V6 PASS → IN_REVIEW.
- `/review-pr <PR>` — full scorecard (incl. V4: server `RULE_ADMIN` denies non-admin, not just the UI gate) → human merge.
- Post-merge: TSK-070 → Done. Next admin-tier feature: `BK-014` (Projects/Developers CRUD).
