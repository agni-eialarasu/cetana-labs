# App-Level Settings — Requirements

| Property | Value |
| :--- | :--- |
| **Spec ID** | `app-level-settings` |
| **Feature** | A key/value `settings` PocketBase collection + a typed TS accessor façade; seed + read-wire the app's own name/description. Foundation for `BK-013` branding. |
| **Backlog** | `TSK-057` (`BK-012`, SPRINT-11) |
| **Status** | 🟡 Proposed (contract authored on Kiro Web; execution on Kiro IDE) |
| **RFCs** | `RFC-LAB-000-013` (decision of record), `-002`/`-003` (data → PB schema), `-006`/`-008` (auth / per-collection API rules) |
| **Enables** | `BK-013` (branding — consumes these settings) |
| **Executor role** | Delegated-agent / onboarded-dev |

---

## 1. Introduction

Implements `RFC-LAB-000-013`: a **key/value `settings` collection** (one row per setting) with a **typed accessor façade** in the SPA (extensibility in the data, type-safety in the accessor). Public read (branding renders pre-auth), superuser-only write (no admin role yet). Seeds + read-wires `app_name`/`app_description`; **reserves** logo keys (upload + branding UI = `BK-013`). Follows the repo's collection pattern (`generate_pb_schema.py → collections()` + `data/*.json` + typed reads).

## 0. Preconditions (preflight — verify BEFORE any change; enforced by `tasks.md` T0)

- **P1 — Surface:** Kiro IDE / local; local PocketBase (`:8090`) + SvelteKit (`:5173`) for verification (`/start-local`).
- **P2 — Toolchain:** Node/pnpm; the data→schema flow (`generate_pb_schema.py`), seed flow (`pb_provision.py`/`pb_import.py`).
- **P3 — Branch:** `feat/app-level-settings` off up-to-date `main`; clean tree; not `main`/`master`.
- **P4 — Merge-first:** this Spec + RFC-013 merged to `main` before `/spec-run`.
- **P5 — Baseline green:** the 5 validators + `pnpm --dir app/web check && build`.
- **P6 — No secrets in settings:** only non-sensitive config (name/description/logo); never a secret.

## 2. Current-state facts (of record — verified)

- Collections declared in `scripts/generate_pb_schema.py → collections()` (`users`, `projects`, `memberships`); `--check` is a CI gate.
- Masters + schemas in `data/*.json` + `data/*.schema.json`; SPA reads via a typed `data.ts` pattern.
- RBAC = PB per-collection API rules (no library); superuser = null rule.
- No `settings` collection exists yet (clean add).

## 3. Requirements (EARS acceptance criteria = Definition of Done)

### R1 — The `settings` collection (key/value)
- **R1.1** The system SHALL add a `settings` collection in `generate_pb_schema.py → collections()` with fields: `key` (text, **unique**, required), `value` (text), `type` (select: `string`|`number`|`boolean`|`url`), `group` (text, optional).
- **R1.2** It SHALL add `data/settings.json` (master) + `data/settings.schema.json` consistent with the collection, and `generate_pb_schema.py --check` SHALL pass (lockstep).
- **R1.3** A **unique index on `key`** SHALL exist (one row per setting).

### R2 — API rules (RBAC)
- **R2.1** `listRule`/`viewRule` SHALL be **public** (readable while anonymous — branding renders pre-auth).
- **R2.2** `createRule`/`updateRule`/`deleteRule` SHALL be **superuser-only** (null → admin-only). Non-superuser write SHALL be denied (verified with a negative control).

### R3 — Typed accessor façade (SPA)
- **R3.1** The SPA SHALL expose a typed `settings` accessor (mirroring the `data.ts` pattern) with **typed getters + hardcoded defaults**, e.g. `appName(): string` (default = repo name), `appDescription(): string`.
- **R3.2** WHEN a key is absent/empty, the accessor SHALL return the default (no crash, no blank). 
- **R3.3** The accessor SHALL cast `value` per the `type` column; callers SHALL NOT touch raw rows.

### R4 — Seed + read-wiring (minimal)
- **R4.1** The seed SHALL create `app_name` (default: repo name) and `app_description` (default: repo description) via the existing `data/` + `pb_provision.py`/`pb_import.py` flow.
- **R4.2** The app SHALL **read** `app_name` (and `app_description` where shown) from settings via the accessor — at least the app header/title/metadata consumes the setting (proving the read-path end-to-end).
- **R4.3** Logo keys (e.g. `logo_icon_url`) SHALL be **reserved/documented** but NOT seeded or implemented (that is `BK-013`).

### R5 — Docs
- **R5.1** `developer-guide.md` (and/or the data/README) SHALL document the settings pattern: the collection, the accessor façade, how to add a new setting (seed row + accessor getter), and the RBAC posture.

### R6 — Quality gates / no regression / no secrets
- **R6.1** `pnpm --dir app/web check && build`, `make validate-local`, and the 5 validators (incl. `generate_pb_schema.py --check`) SHALL pass.
- **R6.2** No secret SHALL be stored in settings or committed. Existing collections/behavior SHALL be unaffected (additive).

## 4. Out of scope (scope honesty)
- Logo **upload**/file handling + branding **editor UI** + white-label deploy wiring → `BK-013`.
- Non-superuser settings write path → needs the admin role (`BK-014`).

## 4b. Human Verification Plan (emitted by `/spec-run`; recorded by `/verification-done`)
On the local stack (`/start-local`) with the seeded `settings`:
- **V1 — collection + seed present:** `settings` exists with `app_name`/`app_description` seeded; `generate_pb_schema.py --check` green.
- **V2 — public read:** the app reads `app_name` from settings and renders it (header/title) **while anonymous** (no sign-in needed).
- **V3 — default fallback:** with `app_name` absent/empty, the app shows the default (repo name) — no crash/blank (R3.2).
- **V4 — superuser-only write:** a non-superuser write to `settings` is denied (negative control); a superuser write succeeds and the app reflects it.
- **V5 — accessor typing:** the accessor casts per `type` (e.g. a `url`/`boolean` setting returns the right TS type); callers use getters, not raw rows.
- **V6 — logo keys reserved, not implemented:** no logo upload/UI shipped; keys documented only.
- **V7 — gates green + docs:** validators + `pnpm check && build` green; settings pattern documented.
