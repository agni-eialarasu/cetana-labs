# App Settings UI (admin-gated editor) — Design

| Property | Value |
| :--- | :--- |
| **Spec ID** | `app-settings-ui` (`BK-031` / `TSK-070`) |
| **Consumes** | `is_admin` tier + `settings` write rule (`BK-030`, merged) · `SettingsAccessor` (`BK-012`) · shared `pb` client |
| **Executor** | Antigravity (SvelteKit form UI over an existing SDK write path; cost-first default) |

## 1. Approach

Frontend-only. Three pieces:
1. **`auth.isAdmin`** — a reactive getter reading `pb.authStore.record?.is_admin`.
2. **A write method on the settings layer** — `updateSetting(id, value)` wrapping `pb.collection('settings').update`, plus a loader that fetches rows **with ids** (the current `loadFromPocketBase` drops them).
3. **An admin-gated editor** — a route/panel rendered `{#if auth.isAdmin}`, pre-filled from the live rows, writing changed values and re-populating the shared `settings` accessor so branding updates live.

No backend work — BK-030 already landed the `settings` write rule (`RULE_ADMIN`). The server rule is the real gate; the UI gate is UX.

## 2. `auth.isAdmin` (the gate source)

`is_admin` is on the **OAuth auth record**, not the seeded `user` map. Add to `AuthState`:
```ts
get isAdmin(): boolean {
  return this.#authed && (pb.authStore.record as Record<string, unknown> | null)?.is_admin === true;
}
```
Reactive because `#authed` is `$state` and flips on `authStore.onChange`. An admin need not be a linked seeded owner (R1.2).

> **Note:** `pb.authStore.record.is_admin` is present because BK-030 added `is_admin` to the `users` auth collection, so the auth token/record carries it. Verify on a fresh sign-in after the field exists.

## 3. Settings write layer (extend `settings.svelte.ts`)

- **Loader with ids** — add `loadEditableSettings(): Promise<Array<SettingRecord & {id:string}>>` using `pb.collection('settings').getFullList()` and keeping `r.id`. (The display path's id-less `SettingRecord` is unchanged — this is a separate editor-only fetch.)
- **Write** — `async function updateSetting(id: string, value: string)` → `pb.collection('settings').update(id, { value })`. One call per changed row.
- **Refresh** — after saves, call the existing `loadSettings()` to repopulate the shared `settings` singleton so getters (and thus header/footer) reflect new values (R2.4), no reload.

## 4. The editor (route + component)

- **Route:** `app/web/src/routes/admin/settings/+page.svelte` (SPA, `ssr=false` already global). Guard in the component: `{#if auth.isAdmin}` render the form; `{:else}` show "Not authorized" + a link to `base/`. (A `+layout`/load redirect is optional polish; the `{#if}` is sufficient since the server rule is the real guard.)
- **Form:** one field per seeded key, typed:
  - `app_name`, `app_description` → text inputs.
  - `logo_icon_url`, `logo_small_url`, `logo_medium_url` → url inputs with validation (empty allowed; non-empty must parse as a URL).
- **Save:** diff against loaded values; `updateSetting(id, value)` for each changed row; collect results; show success/error (R3.1); on success re-run `loadSettings()`.
- **Theme-safe** per the widget/UI conventions — use the app's existing design tokens (never fixed palette), consistent with BK-013/BK-027.

## 5. Entry point (R4)

Add, in the BK-027 header center-nav slot (or the auth/user menu), `{#if auth.isAdmin}<a href="{base}/admin/settings">Settings</a>{/if}`. Non-admins never see it; the slot stays empty for them (BK-027 unchanged).

## 6. Verification

The V-plan (requirements §4b) exercises both gates (UI hidden for non-admin; server `RULE_ADMIN` denies a non-admin who reaches the endpoint), persistence + live branding refresh, and URL validation. The server-gate check (V4) is important: it proves the UI gate is not the only guard.

## 7. Decisions

- **D-SET-1 — gate on `pb.authStore.record.is_admin`**, not the seeded `user` (admin ≠ owner).
- **D-SET-2 — edit existing keys' `value` only.** No key create/delete/type change (R3.3/§4) — keeps the editor simple and the schema stable.
- **D-SET-3 — frontend-only.** BK-030 owns the rules; this Spec adds no backend. Scope floor = `app/web/**`.
- **D-SET-4 — live refresh via `loadSettings()`**, not a hard reload — the shared `settings` singleton is reactive, so re-populating it updates header/footer in place.

## 8. Risk / rollback
- **Risk:** UI gate without server gate = security hole. **Mitigation:** server `RULE_ADMIN` (BK-030) is the real gate; V4 verifies it; the UI gate is UX only.
- **Rollback:** revert the PR — frontend-only, no data/schema change; settings return to admin-UI-only editing.
