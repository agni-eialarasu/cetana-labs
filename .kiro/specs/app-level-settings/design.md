# App-Level Settings — Design

| Property | Value |
| :--- | :--- |
| **Spec ID** | `app-level-settings` (`TSK-057` / `BK-012`) |
| **Decision of record** | `RFC-LAB-000-013` |
| **Surface** | Kiro IDE (build) — schema, data, accessor, docs; local verify |

---

## 1. Approach
Follow the existing collection pattern exactly (no new machinery): declare the collection in `generate_pb_schema.py`, add `data/settings.*`, seed via `pb_provision.py`/`pb_import.py`, read via a typed accessor mirroring `data.ts`. The only *new idea* is the **typed façade over a key/value store** (RFC-013 §3/§6).

## 2. Collection (`generate_pb_schema.py → collections()`)
```
settings:
  fields:  key(text, required, unique) · value(text) · type(select: string|number|boolean|url) · group(text, optional)
  index:   CREATE UNIQUE INDEX idx_settings_key ON settings (key)
  rules:   list/view = ""(public) ; create/update/delete = null (superuser-only)
```
Add `data/settings.json` (seed rows) + `data/settings.schema.json` (draft-07, matching the field set). `generate_pb_schema.py --check` then covers it automatically (CI gate).

## 3. Seed (`data/settings.json`)
```json
[
  { "key": "app_name",        "value": "Cetana Labs Control Hub", "type": "string", "group": "branding" },
  { "key": "app_description", "value": "Protocol Engine",          "type": "string", "group": "branding" }
]
```
- Logo keys (`logo_icon_url`, `logo_small_url`, `logo_medium_url`) are documented in the schema/RFC as **reserved**, NOT seeded (BK-013).
- Defaults for `app_name`/`app_description` mirror the repo name/description (the accessor also hardcodes these as fallbacks).

## 4. Typed accessor façade (SPA, `app/web/src/lib/…`)
- Mirror the existing typed-read (`data.ts`) approach: load the `settings` collection once (eager — the set is tiny, OQ-2), expose typed getters:
  ```ts
  settings.appName(): string          // default: 'Cetana Labs Control Hub' (repo name)
  settings.appDescription(): string   // default: 'Protocol Engine'
  ```
- The façade is the single place that knows each key's name, `type` cast, and default. Absent/empty ⇒ default (R3.2). Callers never see raw rows.

## 5. Read-wiring (prove the path)
- The app header/title (and page `<title>`/metadata where applicable) reads `settings.appName()` instead of a hardcoded string — demonstrating a public, pre-auth read end-to-end (V2). Keep it minimal: one real consumer is enough to prove R4.2.

## 6. RBAC (API rules)
- Public read; superuser-only write (RFC-013 §5). Verify with a positive (superuser write) + negative (non-superuser denied) control (V4) — the enforcement is the server-side rule, not the UI.

## 7. Docs
- `developer-guide.md` (+ `data/README.md` if that's where collection docs live): the settings pattern, "how to add a setting" (seed row + accessor getter + optional `type`), and the RBAC posture. Note the reserved logo keys point at BK-013.

## 8. Open questions (resolve during build — from RFC §9)
- **OQ-1 `group` column now?** Lean **yes** (cheap; avoids a later migration when the branding UI groups settings).
- **OQ-2 load strategy?** Lean **eager** (tiny set).
- **OQ-3 seed via data/ flow?** Lean **yes** (consistency with existing collections).
