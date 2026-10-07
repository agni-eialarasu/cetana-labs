# App Branding & White-Labeling — Design

| Property | Value |
| :--- | :--- |
| **Spec ID** | `app-branding` |
| **Builds on** | `BK-012` settings mechanism (`settings` collection + `SettingsAccessor`, PR #64) |

---

## 1. Approach — extend, don't fork

BK-012 already solved the hard parts (collection, RBAC, typed façade, dual load path, defaults). BK-013 is a **thin consumer layer** on top: three more seeded `url` rows, three typed getters on the existing accessor, and logo rendering on the two surfaces that already read `appName()`. No new backend mechanism, no schema/collection change (the logo keys are already reserved + already permitted by `data/settings.schema.json`).

```
data/settings.json        ──(+3 logo rows, empty default)──►  settings collection / snapshot
        │                                                              │
        ▼                                                              ▼
SettingsAccessor.logoSmallUrl()  ◄── typed getter (default '') ◄── existing get<T>()/cast
        │
        ▼
+layout.svelte (header)  &  +page.svelte (masthead)  ── render <img> if URL set, else text-only
```

## 2. Logo delivery — URL references (the decision, recap)
- Logos are **URLs** (`type: "url"`), not uploaded files. A white-label deploy sets the URL to a hosted asset (repo `static/`, CDN, or client URL). Fits the existing `url` type + accessor exactly; needs **no** `file` field, **no** upload flow, **no** admin role (all deferred to `BK-014`/future).
- Empty URL (the seeded default) ⇒ **text branding only** — the current behavior is the fallback, so with no logo set the app is byte-identical to today (R3.2 / R5.2).

## 3. Component changes

### 3.1 Seed — `data/settings.json` (+3 rows)
```json
{ "key": "logo_icon_url",   "value": "", "type": "url", "group": "branding" },
{ "key": "logo_small_url",  "value": "", "type": "url", "group": "branding" },
{ "key": "logo_medium_url", "value": "", "type": "url", "group": "branding" }
```
Additive only. `generate_pb_schema.py --check` stays green (no collection change; schema already reserves these keys).

### 3.2 Accessor — `app/web/src/lib/settings.svelte.ts`
- Extend `SETTINGS_DEFAULTS` with `logo_icon_url: ''`, `logo_small_url: ''`, `logo_medium_url: ''`.
- Add getters mirroring `appName()`:
  ```ts
  logoIconUrl():   string { return this.get<string>('logo_icon_url',   SETTINGS_DEFAULTS.logo_icon_url); }
  logoSmallUrl():  string { return this.get<string>('logo_small_url',  SETTINGS_DEFAULTS.logo_small_url); }
  logoMediumUrl(): string { return this.get<string>('logo_medium_url', SETTINGS_DEFAULTS.logo_medium_url); }
  ```
- No change to load path, casting, or RBAC.

### 3.3 Render — the two branding surfaces
- **`+layout.svelte`** (header): a small logo (`logoSmallUrl()` ‖ `logoIconUrl()`) before `{settings.appName()}`.
- **`+page.svelte`** (masthead): logo beside the `<h1>{settings.appName()}</h1>`.
- Guard pattern (text-only fallback, no broken image, no layout shift):
  ```svelte
  {#if settings.logoSmallUrl()}
    <img src={settings.logoSmallUrl()} alt={settings.appName()} class="h-8 w-auto" />
  {/if}
  <span>{settings.appName()}</span>
  ```
- Theme-safety: size by height, `w-auto`; no forced background. If a logo needs a backdrop it is the asset's concern, not a fixed color (honors the theme-variable rule).

### 3.4 Docs — `developer-guide.md`
A "White-labeling a deploy" subsection: set `app_name`/`app_description`/`logo_*_url` (snapshot `data/settings.json` for the static path, or the `settings` collection for the live path), the `VITE_PB_SOURCE` source toggle, and that it is a **data change, not a code change**.

## 4. Risks & mitigations
| Risk | Mitigation |
| :--- | :--- |
| Broken-image flash when URL is set but unreachable | `{#if url}` guards presence; a bad URL is a data error (document "use a reachable asset") — out of scope to validate liveness. |
| Logo unreadable on one theme | Size-by-height + no forced bg; V5 checks both themes; asset choice is the operator's. |
| Layout shift when logo appears | Fixed height (`h-8`) reserves space; text-only path unchanged. |
| Scope creep into upload/editor UI | R5.3 scope floor + §4 out-of-scope; this Spec only consumes `url` keys. |

## 5. Why not the alternatives
- **PB `file` field + upload:** needs a new field-type helper in `generate_pb_schema.py`, storage wiring, and the missing admin write role (`BK-014`) — disproportionate for white-label-on-deploy, which a URL already serves. Deferred, not rejected forever.
- **Hardcode branding per deploy build:** fights the whole BK-012 "settings, grown over time" premise and makes white-labeling a code change. Rejected.
