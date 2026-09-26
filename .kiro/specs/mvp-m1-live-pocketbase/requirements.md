# M1 — Wire Sleek UI to Live PocketBase — Requirements

| Property | Value |
| :--- | :--- |
| **Spec ID** | `mvp-m1-live-pocketbase` |
| **Feature** | MVP Phase M1 (`RFC-LAB-000-008` §6) — flip the data-access layer from the static `data/status.json` snapshot to the live PocketBase JS SDK |
| **Epic / Backlog** | `BK-011` (Control Hub Web App MVP) |
| **Status** | 🟡 Proposed (contract authored on Kiro Web; execution on Kiro IDE) |
| **RFCs** | `RFC-LAB-000-008` (MVP/M1), `RFC-LAB-000-005` (Sleek UI data layer §4), `RFC-LAB-000-003` (PocketBase), `RFC-LAB-000-009` (lifecycle — this is the first AIDLC Spec) |
| **Executor role** | Delegated-agent / onboarded-dev (full Spec — `RFC-LAB-000-009` §5) |

---

## 1. Introduction

The PocketBase backend is live and seeded (3 users, 6 projects, 6 memberships on v0.40) and the Sleek UI is live — **but disconnected**: the UI's data-access layer (`app/web/src/lib/data.ts`) reads bundled static snapshots (`static/data/{users,portfolio,status}.json`), while PocketBase holds the real records. This Spec closes that gap for the **structural** data (users + projects), the highest-leverage first step of the MVP (`RFC-LAB-000-008` §3).

**Scope of M1 (deliberately narrow):**
- Load **structural** data (projects + resolved owner) from PocketBase via the JS SDK.
- Continue to **merge live status** (health/wins/focus/blockers/metrics) from the `status.json` snapshot — status migration into the DB is explicitly deferred to a later MVP phase (`RFC-LAB-000-008` §7).
- **No auth, no writes, no deploy** — those are M2 / M4 / M5. M1 must remain fully testable on the local stack.

**Read-parity is the success bar:** the UI must render the same portfolio (same cards, ordering, severity, tags, owner pills) whether it read from PocketBase or the snapshot, because both derive from the same seeded `data/` masters.

## 2. Glossary / Field Mapping (of record — verified against `scripts/pb_provision.py`)

The PocketBase `projects` collection field names differ from the UI's `ProjectRecord` type. The data layer MUST translate:

| UI `ProjectRecord` field | PocketBase `projects` field | Notes |
| :--- | :--- | :--- |
| `id` | `lab_id` | e.g. `LAB-000`. **Not** the PB record `id`. |
| `slug` | `slug` | |
| `name` | `name` | |
| `descriptor` | `descriptor` | |
| `archetype` | `archetype` | select |
| `owner_id` | `owner` (relation → `users`) | resolve via `expand: 'owner'` |
| `repo_url` | `repo_url` | |
| `reference_url` | `reference_url` | |
| `dev_environment` | `dev_environment` | select |
| `status_source` | `status_source` | select |

`users` (expanded owner) → UI `User`: `seed_id`→`id`, `name`, `github_handle`, `role`, `org`, `active`. (`email` is a native PB auth field.)

**Status join key:** the UI merges status by `ProjectRecord.id` (= `lab_id`). `status.json` records are keyed by `LAB-xxx`, so the join key after mapping is `lab_id`.

## 3. Access-rule constraint (critical — informs the design)

`pb_provision.py` sets `projects.listRule` / `viewRule` = `@request.auth.id != ""` (authenticated-only). M1 has **no auth** (that is M2). Therefore an anonymous SDK read of `projects` will be **empty/forbidden** against the seeded rules. The Spec MUST resolve this without pulling M2/M3 forward. See design §2 for the chosen option; requirements below are written to be satisfiable by whichever option is selected at build start (an OQ in §6).

## 4. Requirements (EARS acceptance criteria = Definition of Done)

### R1 — Load structural data from PocketBase
- **R1.1** WHEN `loadProjects` runs in an environment configured with a reachable PocketBase URL, the system SHALL fetch projects via the PocketBase JS SDK using `getFullList({ expand: 'owner', sort: ... })` rather than fetching `static/data/{users,portfolio}.json`.
- **R1.2** WHEN a project record is loaded from PocketBase, the system SHALL map its fields to the UI `ProjectRecord` shape per §2 (notably `lab_id`→`id`, expanded `owner`→`owner_id`/`owner_name`/`owner_github`).
- **R1.3** WHEN the owner relation is expanded, the system SHALL resolve `owner_name` and `owner_github` from the expanded `users` record, and SHALL fall back to `"— Unassigned"` / `null` when the owner is missing (parity with the current snapshot behavior).

### R2 — Preserve live status merge (status stays snapshot-sourced in M1)
- **R2.1** WHILE M1 is the active phase, the system SHALL continue to merge live status fields (`health`, `pitch`, `wins`, `focus`, `blockers`, `risks`, `metrics`, `last_updated`, `days_ago`, and the `is_*` flags) from the `status.json` snapshot, keyed by `lab_id`.
- **R2.2** WHEN a project has no matching status record, the system SHALL apply the existing `emptyStatus` default (no regression).

### R3 — Derived-view parity (the read-parity bar)
- **R3.1** WHEN projects are loaded from PocketBase, the system SHALL compute `severity`, `priority_score`, `tags`, `has_blocker`, `archetype_label`, and `archetype_icon` using the **same logic already in `data.ts`** (no behavioral change to these helpers).
- **R3.2** WHEN the portfolio is loaded from PocketBase, the resulting rendered dashboard (card set, ordering, owner pills, severity styling, KPI counts) SHALL match the snapshot-sourced render for the same seeded dataset.

### R4 — Environment-configurable PocketBase URL
- **R4.1** The system SHALL read the PocketBase base URL from a client-exposed environment variable (Vite `import.meta.env`, `VITE_`-prefixed — the app is a static SPA with `ssr = false`), defaulting to `http://127.0.0.1:8090` when unset.
- **R4.2** The `.env.example` (repo root and/or `app/web`) SHALL document the new variable.

### R5 — Graceful degradation / no hard regression
- **R5.1** IF the PocketBase URL is unreachable OR returns no readable records, THEN the system SHALL surface a clear, non-crashing state (per the fallback strategy chosen in design §2) rather than throwing an unhandled error that blanks the dashboard.
- **R5.2** The change SHALL be confined to the data-access layer and its config; `+page.svelte`, components, and the `Project` view type SHALL NOT require changes (the `loadProjects(fetch) → Project[]` contract is preserved).

### R6 — Quality gates green (`RFC-LAB-000-009` Phase 3)
- **R6.1** WHEN the change is complete, `pnpm --dir app/web check` (svelte-check + tsc) SHALL pass with no new errors.
- **R6.2** WHEN the change is complete, `pnpm --dir app/web build` SHALL succeed (static adapter).
- **R6.3** WHEN the change is complete, `pnpm --dir app/web lint` (prettier) SHALL pass, and `make validate-local` SHALL remain green.

## 5. Out of Scope (deferred — do NOT implement in M1)
- GitHub OAuth / sign-in (M2), any RBAC rule changes beyond what R-access requires (M3), owner write path (M4), deploy (M5).
- Migrating status fields into PocketBase (`status_snapshots`) — status stays snapshot-sourced (`RFC-LAB-000-008` §7).
- Removing the static-snapshot code path if it is retained as the M5/fallback dual-run mechanism (decide in design §2).

## 6. Open Questions (resolve at build start — the AIDLC spike, `RFC-LAB-000-009` §7)
1. **Anonymous read vs. rule relaxation (§3):** for M1, do we (a) temporarily open `projects` `listRule`/`viewRule` to public (`""`) — which is the eventual public-summary tier anyway (`RFC-LAB-000-008` §4) — via `pb_provision.py`, or (b) keep authenticated-only and defer live read until M2, or (c) read as superuser in dev only? *(Leaning: (a) — it matches the planned public tier and keeps M1 self-contained; document that granularity is refined in M3.)*
2. **Retain the snapshot path?** Keep `fetchJson` as a configurable fallback / dual-run (per `RFC-LAB-000-008` §9.4 "dual-run continues"), or remove it? *(Leaning: retain behind the env flag for graceful degradation, R5.)*
3. **`sort` in the SDK vs. in JS:** replicate the current JS sort (`priority_score`, then `last_updated`) client-side (safest for parity) or push a partial sort to PocketBase? *(Leaning: keep the JS sort for exact parity.)*
