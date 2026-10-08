# App Settings UI (admin-gated editor) — Build & Verification Report

| Property | Value |
| :--- | :--- |
| **Spec ID** | `app-settings-ui` |
| **Feature** | In-app editor for `settings` (`app_name`, `app_description`, `logo_*_url`), reactive `auth.isAdmin` getter, settings write layer, live branding refresh |
| **Backlog** | `BK-031` (`TSK-070`, SPRINT-13) |
| **Branch** | `feat/app-settings-ui` |
| **PR** | Pending open (`feat/app-settings-ui → main`) |
| **Executor** | Antigravity (SvelteKit form UI, cost-first per `RFC-LAB-000-014`) |
| **Date** | 2026-10-08 |

---

## 1. Outcome

Delivered the **App Settings UI** (`BK-031`), the first in-app consumer of the `is_admin` tier landed by `BK-030`. The editor enables administrators to configure application branding parameters (`app_name`, `app_description`, `logo_icon_url`, `logo_small_url`, `logo_medium_url`) directly within the app without requiring superuser access or database tooling.

Key additions:
1. **`auth.isAdmin` getter (`app/web/src/lib/auth.svelte.ts`)**: A reactive getter reading `this.#authed && pb.authStore.record?.is_admin === true`. Works independently of seeded user linking (`auth.isUnlinked` / `auth.user`).
2. **Settings write layer (`app/web/src/lib/settings.svelte.ts`)**: Added `loadEditableSettings()` returning rows with their PocketBase record `id`s (`getFullList`), and `updateSetting(id, value)` wrapping `pb.collection('settings').update`. The read-only `SettingsAccessor` getters and `loadSettings()` remain unchanged.
3. **Admin Settings Editor route (`app/web/src/routes/admin/settings/+page.svelte` & `+page.ts`)**: Admin-gated view rendering only when `auth.isAdmin` is true. Features pre-filled typed fields, inline URL validation with text-only branding fallback on empty inputs, dirty detection, discard changes, and live in-app branding refresh via `loadSettings()` without a hard reload. Non-admin or anonymous visitors receive a clear "Admin Access Required" message and no editing controls.
4. **Header Navigation Entry (`app/web/src/routes/+layout.svelte`)**: Renders a `⚙️ Settings` link in the BK-027 center-navigation slot when `auth.isAdmin` is true, staying completely empty for non-admins and anonymous users.
5. **Scope Floor**: Strictly confined to frontend (`app/web/**`). Zero changes to backend schemas, `data/` masters, or PocketBase API rules (enforced by `BK-030`'s `RULE_ADMIN`).

---

## 2. Definition of Done — EARS Criteria (the gate summary)

| DoD item | Met? | Evidence |
| :--- | :---: | :--- |
| **R1 — Surface `is_admin` in auth store** | ✅ | `get isAdmin()` added to `AuthState` (`auth.svelte.ts`); reacts to `this.#authed` and checks `pb.authStore.record.is_admin === true`. Independent of `isUnlinked`/`user`. |
| **R2 — Admin-gated Settings editor route/view** | ✅ | `/admin/settings` route implemented; renders only when `auth.isAdmin` is true; pre-fills from `loadEditableSettings()` with IDs; writes via `updateSetting(id, value)`; re-runs `loadSettings()` to update branding live without reload. |
| **R3 — Write-path behavior & feedback** | ✅ | Success affirmation banner and error alert handling on failure; validates `url`-typed inputs (empty allowed); existing seeded keys only (no key creation). Enforced server-side by `RULE_ADMIN`. |
| **R4 — Nav / entry point** | ✅ | Settings link rendered conditionally in header center-nav slot (`{#if auth.isAdmin}`); hidden for non-admins and anonymous visitors. |
| **R5 — No regression** | ✅ | Non-admin and anonymous views completely unaffected; read-only `SettingsAccessor` and fallbacks unchanged; zero backend or schema alterations. |
| **R6 — Quality gates & scope floor** | ✅ | `pnpm check && build` green, `just validate-local` green, 5 validators pass. Scope floor strictly held to `app/web/**`. |

**Verdict:** `DONE` — all EARS DoD criteria satisfied.

---

## 3. Human Verification Plan (for `/verification-done`)

On the local stack (`just setup && just start-local`), with an authenticated admin (`is_admin=true`) and non-admin / anonymous user:

- **V1 — Gate hidden for non-admin:**
  - When signed out or signed in as a non-admin user (`is_admin: false`):
  - No `⚙️ Settings` entry point in the header.
  - Navigating directly to `/admin/settings` shows the "Admin Access Required" lock screen; no settings fields or write controls render.
- **V2 — Gate shown for admin:**
  - When signed in as an administrator (`is_admin: true`):
  - The `⚙️ Settings` link appears in the header navigation.
  - Navigating to `/admin/settings` loads and displays all seeded settings (`app_name`, `app_description`, `logo_*_url`) pre-filled from PocketBase.
- **V3 — Edit persists & live branding refresh:**
  - Change `app_name` or `app_description` → click "Save Settings".
  - Save success notification appears.
  - Global header and footer branding reflect the new values immediately without a page reload.
  - Browser reload confirms persistence.
- **V4 — Server gate holds:**
  - Any non-admin attempt to execute `pb.collection('settings').update(...)` (e.g. from developer console) is rejected by PocketBase server-side `RULE_ADMIN`.
- **V5 — URL validation:**
  - Entering an invalid URL (e.g. `invalid-url`) displays an inline validation error and disables saving.
  - Clearing the field or entering a valid `https://...` URL clears the error. Saving an empty logo URL results in clean text-only branding fallback.
- **V6 — Quality gates:**
  - `pnpm --dir app/web check && pnpm --dir app/web build` passes with zero errors.
  - `just validate-local` passes all 5 governance validators.
