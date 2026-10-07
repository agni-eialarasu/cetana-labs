# App Branding & White-Labeling — Requirements

| Property | Value |
| :--- | :--- |
| **Spec ID** | `app-branding` |
| **Feature** | Make the app's **name, description, and logo set** branding settings the deployed UI reads at runtime, so a deploy can be re-skinned per client (white-labeling). Consumes the `BK-012` settings mechanism. |
| **Backlog** | `TSK-060` (`BK-013`, SPRINT-12) |
| **Status** | 🟡 Proposed (authored on KiroCrew Operator; execution on an Executor) |
| **RFCs** | `RFC-LAB-000-013` (settings mechanism — decision of record; reserved the logo keys), `RFC-LAB-000-011` (deploy/white-label context), `-002`/`-003` (data → PB schema) |
| **Consumes** | `BK-012` app-level-settings (the `settings` collection + `SettingsAccessor` façade, merged PR #64) |
| **Executor role** | Default **Antigravity** (cost-first per `RFC-LAB-000-014`) — mostly SPA wiring + a reserved-key seed, no new backend mechanism; escalate to Kiro IDE only if the logo-render path proves deeper than expected (record why). |
| **Source** | `BK-013` backlog row; builds directly on the just-merged `BK-012` foundation. |

---

## 1. Introduction

`BK-012` (merged, PR #64) delivered the settings **mechanism**: a key/value `settings` collection, a typed `SettingsAccessor` façade (`appName()`/`appDescription()`/`typed()` with hardcoded defaults + per-`type` casting), public read / superuser write, and the dual load path (PocketBase → `data/settings.json` snapshot fallback). It **reserved** three logo keys (`logo_icon_url`, `logo_small_url`, `logo_medium_url`) but seeded/implemented none.

`BK-013` completes the branding story on top of that mechanism: **seed + read-wire the logo set**, add typed logo getters to the accessor, render the logo (with a graceful text/initial fallback) on the branding surfaces that already consume `appName()`, and document the **white-label deploy** path (how a per-client deploy re-skins name/description/logo without a code change).

### Design decision — logos are URL references, NOT file uploads (this Spec's one real decision)
The `settings` `type` enum is `string|number|boolean|**url**` and the reserved keys are `logo_*_**url**` — there is **no file-upload field type** and **no admin write UI** (the admin role is deferred to `BK-014`). So BK-013 scopes logos as **URL references** (point at a hosted asset — a repo `static/` path, a CDN, or the client's own URL). This fits the existing model with **zero new backend infra**, keeps white-labeling to a data change, and honors RFC-013's "grow over time". **Logo file *upload* + an in-app branding *editor UI* remain explicitly out of scope** (they need the admin write path from `BK-014`); this Spec only consumes the already-reserved `url` keys. *(Rejected alternative: a new PocketBase `file` field + upload flow — richer, but requires a new schema field type, the missing admin role, and storage wiring; disproportionate for white-label-on-deploy, which a URL already serves.)*

## 0. Preconditions (preflight — verify BEFORE any change; enforced by `tasks.md` T0)
- **P1 — Surface:** an Executor clone (default Antigravity `cetana-labs-antigravity/`); local PocketBase (`:8090`) + SvelteKit (`:5173`) for verification (`/start-local`).
- **P2 — Toolchain:** Node/pnpm; the data→schema flow (`generate_pb_schema.py`), seed flow (`pb_provision.py`/`pb_import.py`).
- **P3 — Branch:** `feat/app-branding` off up-to-date `main`; clean tree; not `main`/`master`.
- **P4 — Merge-first:** this Spec merged to `main` before `/spec-run`.
- **P5 — BK-012 present on `main`:** the `settings` collection + `SettingsAccessor` exist (PR #64 merged). This Spec extends them; it does not re-create the mechanism.
- **P6 — Baseline green:** the 5 validators + `generate_pb_schema.py --check` + `pnpm --dir app/web check && build`.

## 2. Current-state facts (of record — verified 2026-10-07 on `main`)
- `settings` collection live (`key` unique, `value`, `type` select `string|number|boolean|url`, `group`); public read, superuser write; unique index `idx_settings_key`.
- `SettingsAccessor` (`app/web/src/lib/settings.svelte.ts`): `appName()`, `appDescription()`, generic `get<T>()`/`typed<T>()`, `castSettingValue()`; `SETTINGS_DEFAULTS` holds `app_name`/`app_description`. Eager-loaded via `loadSettings()`.
- `app_name`/`app_description` already **render** in `+page.svelte` (title, `<h1>`, footer) and `+layout.svelte` — these are the surfaces a logo joins.
- Logo keys `logo_icon_url`/`logo_small_url`/`logo_medium_url` are **reserved in `data/settings.schema.json`** but not seeded.
- No `file`-type field exists in `generate_pb_schema.py`; no admin write UI exists (`BK-014`).

## 3. Requirements (EARS acceptance criteria = Definition of Done)

### R1 — Seed the logo set (reserved keys → real settings)
- **R1.1** The seed SHALL add `logo_icon_url`, `logo_small_url`, `logo_medium_url` to `data/settings.json` as `type: "url"`, `group: "branding"`, with **empty-string defaults** (unset ⇒ the UI falls back to text — R3.2), via the existing `data/` + `pb_provision.py`/`pb_import.py` flow.
- **R1.2** `data/settings.schema.json` SHALL already permit these keys (they are reserved); `generate_pb_schema.py --check` SHALL pass (no collection/schema change needed — additive data rows only).

### R2 — Typed logo accessors (extend the façade, don't fork it)
- **R2.1** `SettingsAccessor` SHALL expose typed getters `logoIconUrl()`, `logoSmallUrl()`, `logoMediumUrl()` returning `string` (default `''`), built on the existing `get<T>()`/casting — callers SHALL NOT touch raw rows.
- **R2.2** `SETTINGS_DEFAULTS` SHALL be extended with the three logo keys (default `''`), consistent with the existing default pattern.

### R3 — Render branding (logo + name) with graceful fallback
- **R3.1** The app header (`+layout.svelte`) and the dashboard masthead (`+page.svelte`) SHALL render the logo (`logo_small_url`/`logo_icon_url` as appropriate) **beside/above** `appName()` when a logo URL is set.
- **R3.2** WHEN a logo URL is empty/absent (the default), the UI SHALL render the existing **text branding only** (name/description) with no broken image, no layout shift, no crash — the current behavior is the fallback.
- **R3.3** The logo `<img>` SHALL have an `alt` of `appName()` (accessibility) and SHALL be theme-safe (render acceptably on light + dark surfaces).

### R4 — White-label deploy path (documentation + proof)
- **R4.1** `developer-guide.md` SHALL document how a per-client deploy re-skins branding **without a code change**: set `app_name`/`app_description`/`logo_*_url` (via the seed `data/settings.json` for the snapshot path, or the `settings` collection for the live path), and the mechanism of the PB→snapshot source toggle (`VITE_PB_SOURCE`).
- **R4.2** The Spec SHALL prove the white-label path end-to-end at least once: set a non-default `app_name` + a `logo_small_url`, and show the deployed/served UI reflects both (V-plan).

### R5 — Quality gates / no regression / no secrets / scope floor
- **R5.1** `pnpm --dir app/web check && build`, `make`/`just validate-local`, and the 5 validators (incl. `generate_pb_schema.py --check`) SHALL pass.
- **R5.2** No secret SHALL be stored in settings. Existing behavior SHALL be unaffected (additive): with no logo set, the app looks exactly as it does today.
- **R5.3** Scope floor: `data/settings.json`, the accessor, the two branding surfaces, and docs ONLY. **No** new PB field type, **no** upload flow, **no** admin editor UI, **no** `data/` schema/collection change (logo keys are already reserved).

## 4. Out of scope (scope honesty)
- Logo **file upload** + storage + an in-app branding **editor UI** → needs the admin write path (`BK-014`); deferred.
- Per-client deploy **automation** / multi-tenant provisioning → `RFC-LAB-000-011` territory; this Spec documents the manual re-skin, not an automated pipeline.
- Favicon / PWA-icon generation from the logo → future polish, not this Spec.

## 4b. Human Verification Plan (emitted by `/spec-run`; recorded by `/verification-done`)
On the local stack (`/start-local`) with the seeded branding settings:
- **V1 — logo keys seeded:** `logo_icon_url`/`logo_small_url`/`logo_medium_url` present in `settings` (empty default); `generate_pb_schema.py --check` green.
- **V2 — default fallback (headline):** with all logo URLs empty, the app renders **text branding only** — no broken image, no layout shift (R3.2). This is the no-regression proof.
- **V3 — logo renders:** set `logo_small_url` to a real asset; the header/masthead shows the logo beside `appName()`, with `alt` = app name (R3.1/R3.3).
- **V4 — white-label proof (headline):** set a non-default `app_name` + `app_description` + `logo_small_url`; the served UI reflects all three — a re-skin with **no code change** (R4.2).
- **V5 — theme-safe:** the logo renders acceptably on both light and dark themes (R3.3).
- **V6 — accessor typing:** logo getters return `string` via the existing façade; callers use getters, not raw rows (R2).
- **V7 — gates green + docs:** validators + `pnpm check && build` green; the white-label deploy path documented in `developer-guide.md` (R4.1).
