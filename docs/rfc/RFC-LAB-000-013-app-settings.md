# RFC-LAB-000-013: App-Level Settings

| Property | Value |
| :--- | :--- |
| **RFC ID** | `RFC-LAB-000-013` |
| **Title** | App-Level Settings — a key/value settings collection + typed accessor façade |
| **Author** | Eialarasu (LAB-000 Control Hub) |
| **Status** | 🟡 Proposed |
| **Date** | 2026-09-30 |
| **Backlog** | `BK-012` / `TSK-057` (SPRINT-11) |
| **Builds On** | `RFC-LAB-000-002` (relational data layer), `RFC-LAB-000-003` (data → PB schema), `RFC-LAB-000-006`/`-008` (auth / per-collection API rules) |
| **Enables** | `BK-013` (branding & white-labeling — consumes these settings) |
| **Decision Journal** | (to be Entry 015 if this session records one) |

---

## 1. Context & Problem Statement

The MVP is deployed and hardened. The next product capability is **app-level settings** — configurable values the app reads at runtime (starting with the app's own name/description, growing over time). The explicit design brief (`BK-012`) is **"initialized minimal, grown over time"**, and it is the **foundation for `BK-013`** branding/white-labeling (app name, description, logo set all become settings so a deploy can be re-skinned per client).

The repo already has a clear collection pattern (`RFC-LAB-000-002`/`-003`): collections are declared in `scripts/generate_pb_schema.py → collections()`, backed by `data/<name>.json` masters + JSON schemas (kept in lockstep by `generate_pb_schema.py --check`), enforced by **PocketBase per-collection API rules** (no RBAC library), and read in the SPA via typed accessors. Existing collections (`users`, `projects`/portfolio, `memberships`) are **arrays of records**. App settings is *configuration*, not a record set — so the shape needs a deliberate decision.

## 2. Decision (summary)

1. **Shape = key/value collection + a typed accessor façade.** A `settings` PocketBase collection with one **row per setting** (`key`, `value`, `type`, optional `group`), and a **typed TypeScript accessor** layer in the SPA that presents settings as typed, validated getters with sensible defaults. Extensibility (add a setting = a data row, no schema migration) lives in the collection; type-safety lives in the accessor.
2. **RBAC:** **public read** (branding must render on the public dashboard), **superuser-only write** for now (settings are rare, high-trust; no admin role exists yet — `RFC-LAB-000-008` deferred the 5-role model). Revisit the write path when `BK-014` (admin CRUD) lands.
3. **Defaults & resilience:** the accessor returns a **hardcoded sensible default** when a key is absent (e.g. `appName` → repo name), so a missing/empty setting never breaks the app.
4. **Scope = the mechanism.** `BK-012` delivers the collection, schema, seed, typed accessors, API rules, and **read-wiring** (the app reads `app_name`/`app_description` from settings). **Logo *upload* and the branding *editor UI* are `BK-013`** — this RFC only *reserves* the logo keys.

## 3. Why key/value (D1) — options weighed

| Option | Shape | Verdict |
| :--- | :--- | :--- |
| **A — Key/value rows** (chosen) | `{key, value, type, group}`, one row per setting | ✅ Best fit for "minimal now, grow over time" — a new setting is a data row, not a migration. Typing concern solved in the accessor façade. |
| B — Single typed record | one row, typed columns (`app_name`, `logo_icon_url`, …) | Strong PB-level typing, but every new setting is a schema migration — fights "grow freely". Rejected as the base (its type-safety is recovered via A's accessor). |
| C — Single JSON blob | one row, one `config` JSON field | Max flexibility, but no PB validation, no per-field rules, corruption-prone. Rejected. |

**A + typed façade** takes the extensibility of key/value and the safety of typed access — the accessor is the single place that knows each key's name, type, and default. Adding `app_description` later is a seed row + one accessor getter, no migration.

## 4. Data model (the `settings` collection)

`data/settings.json` (master) + `data/settings.schema.json`, declared in `generate_pb_schema.py`:

| Field | Type | Notes |
| :--- | :--- | :--- |
| `key` | text, unique, required | e.g. `app_name`, `app_description`, `logo_icon_url` (reserved) |
| `value` | text | the stored value (string form; the accessor casts per `type`) |
| `type` | select: `string`\|`number`\|`boolean`\|`url` | drives accessor casting + light validation |
| `group` | text (optional) | grouping for future UI, e.g. `branding` |

- **Unique index on `key`** (one row per setting).
- **Seed (minimal):** `app_name` (default: repo name), `app_description` (default: repo description). Logo keys are **reserved/documented but not seeded** until `BK-013`.

## 5. API rules (RBAC — D2)

- `listRule` / `viewRule`: **public** (`""` / open) — branding renders pre-auth.
- `createRule` / `updateRule` / `deleteRule`: **superuser-only** (null → admin-only in PocketBase).
- Rationale: settings are low-frequency, high-trust; opening writes needs the admin role that `BK-014` will introduce. Documented as a deliberate deferral, not an oversight.

## 6. Typed accessor façade (the safety layer)

In the SPA (`app/web/src/lib/…`, mirroring the existing `data.ts` typed-read pattern):
- A `settings` accessor that loads the collection once and exposes **typed getters** with defaults, e.g. `settings.appName(): string` (default = repo name), `settings.appDescription(): string`.
- The façade is the single source of key names, casting (`type`), and defaults — callers never touch raw rows.
- Missing/empty key ⇒ the default (resilience, D3).

## 7. Scope & Non-Goals

- **In scope (`BK-012`):** `settings` collection + schema + seed + API rules + typed accessor + read-wiring (`app_name`/`app_description` consumed by the app header/metadata).
- **Out of scope (→ `BK-013`):** logo **upload**/file handling, the branding **editor UI**, white-label per-client deploy wiring. This RFC only *reserves* logo keys.
- **Out of scope (→ `BK-014`):** a non-superuser settings write path (needs the admin role).

## 8. Traceability
`BK-012` → `TSK-057` → this RFC → Spec `app-level-settings` → PR → CHANGELOG → tag. Enables `BK-013`.

## 9. Open Questions
- **OQ-1:** does `group` earn its place now, or add it when the branding UI (BK-013) needs grouping? (Lean: include the column now — cheap, avoids a later migration.)
- **OQ-2:** accessor load strategy — eager (load all settings once at app init) vs. lazy per-key? (Lean: eager; the set is tiny.)
- **OQ-3:** should the seed live in `data/settings.json` and flow through `pb_provision.py`/`pb_import.py` like other collections? (Lean: yes — consistency with the existing seed flow.)

## 10. Risks & Mitigations
- **Stringly-typed values** (key/value trade-off) → mitigated by the typed accessor + the `type` column driving casting/validation.
- **Public read exposes settings** → only non-sensitive config lives here (name/description/logo); no secrets in settings, ever.
- **Schema/data drift** → the existing `generate_pb_schema.py --check` CI gate covers the new collection automatically.
