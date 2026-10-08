# App Settings UI (admin-gated editor) — Requirements

| Property | Value |
| :--- | :--- |
| **Spec ID** | `app-settings-ui` |
| **Feature** | An in-app **editor** for the `settings` collection (app name, description, branding logo URLs), visible and writable **only to the `is_admin` tier**. The read/display side already exists (BK-012/BK-013); this adds the write UI. |
| **Backlog** | `BK-031` (`TSK-070`, SPRINT-13) |
| **Work class** | **Sprint deliverable** (product UI a user exercises) → **FULL gate**: Spec → `/spec-run` → `/review-pr` scorecard → human merge. |
| **Depends on** | `BK-030` (`is_admin` tier + `settings` write rule — **merged** `d4f9734`), `BK-012` (`SettingsAccessor` + `settings` collection), `RFC-LAB-000-008` A1. |
| **RFCs** | `RFC-LAB-000-013` (settings), `RFC-LAB-000-008` A1 (`is_admin`), `RFC-LAB-000-005` (Sleek UI) |
| **Executor role** | Default **Antigravity** (cost-first per `RFC-LAB-000-014`) — SvelteKit form UI over an existing SDK write path, no new backend/rules (BK-030 landed those); escalate to Kiro IDE only if the auth-gating wiring proves deeper (record why). |
| **Source** | Operator brainstorm 2026-10-08 (item #5 of six); first consumer of the `is_admin` tier. |

---

## 1. Introduction

`settings` holds the app's branding/config (`app_name`, `app_description`, `logo_*_url`). Today it is **read-only in-app** (the `SettingsAccessor` getters render it; writes are superuser-only via the PocketBase admin UI). BK-030 added `is_admin` + the `settings` write rule (`RULE_ADMIN`). This Spec adds the **admin editor**: an authenticated admin edits settings in the app; everyone else sees no editor (the display is unchanged for all).

## 2. Current-state facts (verified 2026-10-08 on `main`)
- **`app/web/src/lib/settings.svelte.ts`** — `SettingsAccessor` is **read-only**: eager `loadSettings()` + typed getters (`appName()`, `appDescription()`, `logoIconUrl/SmallUrl/MediumUrl()`), hardcoded `SETTINGS_DEFAULTS`. **No write method exists.** `loadFromPocketBase()` maps rows to `{key,value,type,group}` — **drops the PocketBase record `id`** (the UI `SettingRecord` type has no `id`). A write path needs the row id → the editor must fetch full records (with ids) for editing.
- **`app/web/src/lib/auth.svelte.ts`** — `auth` exposes `isAuthenticated`, `user` (the *seeded* linked record), `isUnlinked`. **It does NOT yet surface `is_admin`.** `is_admin` lives on the **OAuth auth record** (`pb.authStore.record.is_admin`), not on the seeded `user` map — so the admin gate must read it from the auth record.
- **`app/web/src/lib/pb.ts`** — single shared `pb` client; `pb.collection('settings').update(id, {...})` is the write path, gated server-side by `RULE_ADMIN` (BK-030).
- **Settings keys** (`data/settings.json`): `app_name`, `app_description` (`type:string`), `logo_icon_url`, `logo_small_url`, `logo_medium_url` (`type:url`).

## 3. Requirements (EARS acceptance criteria = Definition of Done)

### R1 — Surface `is_admin` in the auth store
- **R1.1** `auth` SHALL expose a reactive **`isAdmin`** boolean derived from `pb.authStore.record?.is_admin === true` (false when anonymous, unlinked, or non-admin). It updates on sign-in/out like the other auth flags (no reload).
- **R1.2** `isAdmin` SHALL be independent of `isUnlinked`/`user` — an admin need not be a seeded portfolio owner (an admin is defined solely by the `is_admin` flag on their auth record).

### R2 — Admin-gated Settings editor route/view
- **R2.1** A **Settings editor** SHALL exist (a route e.g. `base/admin/settings`, or a gated panel) that renders ONLY when `auth.isAdmin` is true. For a non-admin / anonymous user it SHALL NOT render (redirect to `base/` or render a "not authorized" notice — no editor, no settings-write controls).
- **R2.2** The editor SHALL list the editable settings (`app_name`, `app_description`, `logo_icon_url`, `logo_small_url`, `logo_medium_url`) as typed form fields, pre-filled from the live `settings` records (fetched **with their record ids**, R-note §2).
- **R2.3** On save, the editor SHALL write changed values via `pb.collection('settings').update(id, { value })` (one update per changed row), honoring the row's `type`.
- **R2.4** After a successful save, the in-app branding (header/footer app name, description, logo — BK-013/BK-027) SHALL reflect the new values without a hard reload (re-run `loadSettings()` / repopulate the shared `settings` accessor).

### R3 — Write-path behavior & feedback
- **R3.1** A successful save SHALL show a success affirmation; a failed save (e.g. a non-admin who reached the endpoint, or a network error) SHALL show the error and NOT silently drop the edit. The server rule (`RULE_ADMIN`) is the real gate — the UI gate (R2.1) is UX, not security.
- **R3.2** The editor SHALL validate `url`-typed fields as URLs (empty allowed — empty logo = text-only branding, BK-013 fallback); invalid non-empty URLs are flagged before save.
- **R3.3** Creating NEW settings keys is **out of scope** (R4) — the editor edits the existing seeded keys only (`value` field); key/type/group are fixed.

### R4 — Nav / entry point
- **R4.1** The admin Settings entry point SHALL appear only for admins — e.g. a link in the header **center-nav slot** (the empty slot BK-027 shipped) or a user-menu item, shown `{#if auth.isAdmin}`. For non-admins the slot stays empty (BK-027 behavior unchanged).

### R5 — No regression
- **R5.1** For non-admins and anonymous users, the app renders exactly as today (no editor, no new controls, branding reads unchanged).
- **R5.2** The read-only `SettingsAccessor` getters + `loadSettings()` behavior are unchanged (the editor ADDS a write path; it does not alter the read path's defaults/fallbacks).
- **R5.3** No backend/`data/`/schema/rule change — BK-030 already landed the `settings` write rule. This Spec is **frontend-only**.

### R6 — Quality gates / scope floor
- **R6.1** `pnpm --dir app/web check && build`, `just validate-local`, 5 validators green.
- **R6.2** Scope floor: `app/web/**` only (the auth store `isAdmin` getter + the editor route/component + a nav entry). **NO** backend, `data/`, schema, or rule change. **NO** new settings keys.

## 4. Out of scope
Creating/deleting settings keys (edit existing values only); Projects/Developers CRUD (`BK-014`); any `users`/role management UI; the RGS Stage B UI; new settings beyond the seeded five.

## 4b. Human Verification Plan (emitted by `/spec-run`; recorded by `/verification-done`)
On the local stack (`just setup && just start-local`), with a bootstrapped admin (`is_admin=true`) and a non-admin user:
- **V1 — gate hidden for non-admin:** signed out AND signed in as a non-admin → no Settings editor, no entry-point link; branding renders normally.
- **V2 — gate shown for admin:** signed in as admin → the Settings entry point + editor render.
- **V3 — edit persists:** admin changes `app_name` (or a logo URL) → save succeeds → header/footer branding updates without a hard reload; refresh confirms persistence.
- **V4 — server gate holds:** a non-admin hitting the write path (e.g. via console/SDK) is denied by `RULE_ADMIN` (the UI gate is not the only guard).
- **V5 — URL validation:** an invalid `logo_small_url` is flagged pre-save; an empty one saves and yields text-only branding (BK-013 fallback).
- **V6 — gates:** `pnpm check && build` + validators green.
