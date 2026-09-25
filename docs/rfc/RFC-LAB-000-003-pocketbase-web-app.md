# RFC-LAB-000-003: PocketBase Control Hub Web App — Scoping (`BK-008`)

| Property | Value |
| :--- | :--- |
| **RFC ID** | `RFC-LAB-000-003` |
| **Title** | Control Hub Web App Evolution — PocketBase Backend & Sleek UI |
| **Author** | Eialarasu (LAB-000 Control Hub) |
| **Status** | 🟡 Proposed (Scoping Spike — `TSK-031`) |
| **Date** | 2026-09-24 |
| **Backlog** | `BK-008` (SPRINT-06 scoping) |
| **Builds On** | `RFC-LAB-000-002` (relational data layer), `RFC-LAB-000-001` (cloud dev) |
| **Enables** | `BK-007` (RBAC / role-gated audit trail), `BK-006` (health trend telemetry) |

---

## 1. Purpose & Scope

This is a **scoping RFC**, not an implementation mandate. It defines *how* Cetana Labs (`LAB-000`) evolves from a static, file-based control plane into a **full web application (database + server)** using **PocketBase**, and lays out the architecture, data mapping, access model, migration path, and a phased delivery plan for review before any build begins.

**In scope:** backend choice, collection schema derived from `data/`, auth & RBAC model, migration/import strategy, dev/deploy environment, UI approach, phased plan, risks.
**Out of scope (this RFC):** writing application code, final UI visual design, production hosting contracts.

## 2. Why PocketBase

PocketBase is an open-source backend distributed as a **single Go binary** bundling an embedded **SQLite** datastore, **built-in authentication**, **realtime subscriptions**, an **admin dashboard**, and a **REST-ish API**; it runs standalone or as a Go framework/library. ([pocketbase.io/docs](https://pocketbase.io/docs/))

Fit for `LAB-000`:
- **Single-binary, embedded DB** → minimal ops; deploys inside the existing `.devcontainer/` / Codespaces model from `RFC-LAB-000-001` §5 with no separate DB server to run.
- **Collections map 1:1 to our `data/` masters** — `users`, `projects`, `memberships` already exist as JSON with PocketBase-shaped schemas (`RFC-LAB-000-002` §5). The migration is largely a data import, not a redesign.
- **Built-in auth + per-collection API rules** → the substrate for `BK-007` RBAC without bolting on a separate auth service.
- **Extensible in Go** → custom endpoints (e.g. WhatsApp digest generation, `/ping-leads`) can run as hooks in the same binary.

> _Content was rephrased for compliance with licensing restrictions._

**Alternatives considered (briefly):** Supabase/Firebase (heavier, external managed services — over-provisioned for a control hub of this size); a bespoke FastAPI/Express + Postgres stack (more control, materially more ops and code than the problem warrants). PocketBase wins on ops-simplicity-per-feature for this scale.

## 3. Target Architecture

```text
                 ┌────────────────────────────────────────────┐
                 │            PocketBase (single Go binary)      │
  Sleek UI  ◀──▶ │  REST/Realtime API  •  Auth  •  Admin UI      │ ◀──▶  SQLite (embedded)
 (SPA/SSR)       │  Collections: users, projects, memberships,   │
                 │               status_snapshots, sprints, ...   │
                 │  Go hooks: WhatsApp digest, ping-leads, export │
                 └────────────────────────────────────────────┘
                              ▲                     ▲
                              │                     │
             Git (data/ seed import)      GitHub Actions (CI import + deploy)
```

- **Backend:** PocketBase, run via the `.devcontainer/` (Codespaces primary once services exist, per `RFC-LAB-000-001` §5).
- **Frontend ("Sleek UI"):** a lightweight SPA (framework TBD in the design phase — candidate: a small Svelte/SvelteKit or plain-Vite app) consuming the PocketBase JS SDK. The existing static dashboard (`docs/index.html`) remains the read-only public snapshot until the app reaches parity.
- **Data flow:** `data/*.json` remains the versioned seed source of truth in Git; a migration importer loads it into PocketBase collections. Longer term, PocketBase becomes the write source and `data/` is exported from it for Git-tracked auditability.

## 4. Collection Schema (derived from `data/`)

| Collection | Type | Source | Key fields |
| :--- | :--- | :--- | :--- |
| `users` | auth | `data/users.json` | `name`, `email`, `github_handle`, `role`, `org`, `active` |
| `projects` | base | `data/portfolio.json` | `lab_id`, `slug`, `name`, `archetype`, `owner` (relation→users), `repo_url`, `dev_environment`, `status_source` |
| `memberships` | base | `data/memberships.json` | `user` (relation→users), `project` (relation→projects), `role` |
| `status_snapshots` | base | `STATUS.md` (migrated) | `project` (relation), `health`, `wins`, `focus`, `blockers`, `metrics`, `updated_at` |
| `sprints` | base | `BACKLOG.md` (migrated) | `sprint_id`, `goal`, `status`, `start`, `end`, `tasks[]` |

PocketBase **auth collections** extend base collections with auth-specific fields ([pocketbase.io/docs/collections](https://pocketbase.io/docs/collections)); `users` therefore becomes the login identity as well as the ownership target. `owner_id`/membership FKs from `RFC-LAB-000-002` become native PocketBase **relation** fields.

> **Note:** `status_snapshots` and `sprints` are the *deferred* migration — live status leaves `STATUS.md` only in a later phase (see §7). The scraper contract (`<= 35 lines`) stays intact until then.

## 5. Auth & RBAC Model (seeds `BK-007`)

- **Identity:** PocketBase `users` auth collection (email/OAuth; GitHub OAuth aligns with the existing `github_handle`).
- **Roles:** reuse the `RFC-LAB-000-002` role enum (`owner`, `lead`, `contributor`, `stakeholder`, `reviewer`), resolved via the `memberships` join.
- **Access enforcement:** PocketBase per-collection **API rules** (filter expressions) gate reads/writes — e.g. a user sees full detail for projects they are a member of, and read-only summaries otherwise. This directly implements the `BK-007` goal of role-gated history *without* creating a developer-surveillance perception (rules are explicit and auditable).
- **Admin:** PocketBase superuser (admin UI) reserved for the control-hub owner.

## 6. Dev & Deploy Environment

- **Development:** per `RFC-LAB-000-001`, `LAB-000` stays cloud-based; introducing a persistent server + DB shifts the primary env from Kiro Web → **Codespaces**, with PocketBase declared as a service in `.devcontainer/`.
- **Deploy:** single binary + SQLite volume → simple container host (Railway/Fly/Render-class) or self-host; static public dashboard continues on GitHub Pages until app parity.
- **CI:** a GitHub Action imports `data/` on deploy and runs schema/RBAC-rule checks (extends the `validate_portfolio.py` referential-integrity pillar into the app layer).

## 7. Phased Delivery Plan

| Phase | Scope | Exit Criteria |
| :--- | :--- | :--- |
| **P0 — Spike (this RFC, `TSK-031`)** | Ratify architecture, schema, RBAC, plan | RFC accepted |
| **P1 — Backend Stand-up** | PocketBase in `.devcontainer/`; `users`/`projects`/`memberships` collections; import `data/` | Collections live; seed imported; API rules drafted |
| **P2 — Read UI Parity** | Sleek SPA replicating the current dashboard (read-only) against PocketBase | Feature parity with `docs/index.html` |
| **P3 — Auth & RBAC (`BK-007`)** | GitHub OAuth login; role-gated views via API rules; audit trail | Role-scoped access enforced & audited |
| **P4 — Write Path & Status Migration** | Edit projects/status in-app; migrate `STATUS.md` → `status_snapshots`; `data/` becomes an export | App is write source of truth; Git export retained |
| **P5 — Telemetry (`BK-006`)** | Health-trend history & charts on `status_snapshots` | Trend dashboards live |

Each phase is a candidate sprint theme; P1–P2 are the near-term focus after scoping.

## 8. Migration Strategy (file → DB)

1. **Seed import**: a script maps `data/*.json` → PocketBase collections (owner/membership FKs → relations). Idempotent; re-runnable.
2. **Dual-run**: during P2–P3, `data/` (Git) and PocketBase coexist; `data/` remains authoritative and is imported on deploy.
3. **Cutover (P4)**: PocketBase becomes the write source; a scheduled export writes `data/*.json` back to Git for versioned auditability, preserving the trunk-based history guarantee.
4. **STATUS.md**: migrated last (P4) into `status_snapshots`; the 35-line scraper contract is retired only once the app emits the executive digest.

## 9. Risks & Mitigations

| Risk | Mitigation |
| :--- | :--- |
| Scope creep (full rewrite at once) | Strict phasing (§7); each phase independently shippable. |
| SQLite write-concurrency limits | Control-hub scale is tiny (single-digit concurrent writers); Litestream-style backups for durability. |
| Losing Git-tracked auditability | `data/` export-on-write (§8.3) keeps the versioned trail. |
| Divergence from `data/` schema | Collections generated from the existing JSON Schemas; CI validates parity. |
| RBAC perceived as surveillance (`BK-007` concern) | Explicit, auditable API rules; role model is transparent and member-scoped. |
| Vendor/tool lock-in | PocketBase is open-source, single-binary, SQLite-backed — data is a plain file; low exit cost. |

## 10. Open Questions (for design phase)

1. Frontend framework for the "Sleek UI" (SvelteKit vs. Vite+React vs. plain) — decide in P2 design.
2. Hosting target for the binary + volume.
3. Whether the public GitHub Pages snapshot persists long-term or is replaced by a public read-only app route.
4. Auth providers beyond GitHub OAuth (email/password fallback?).
