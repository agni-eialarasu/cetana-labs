# RFC-LAB-000-002: Relational JSON Data Model (User & Project Masters)

| Property | Value |
| :--- | :--- |
| **RFC ID** | `RFC-LAB-000-002` |
| **Title** | Relational JSON Data Model — User Master, Project Master & Memberships |
| **Author** | Eialarasu (LAB-000 Control Hub) |
| **Status** | ✅ Accepted |
| **Date** | 2026-09-24 |
| **Backlog** | `BK-009` (SPRINT-05 spike) |
| **Related** | `BK-008` (Web App Evolution), `BK-007` (RBAC / role-gated history), `RFC-LAB-000-001` |

---

## 1. Context & Problem Statement

Portfolio metadata is currently **fragmented and denormalized across Markdown**, parsed by regex:

- **Stable project metadata** (archetype, repo URL) lives in each `projects/LAB-XXX/README.md`.
- **Live status** (health, wins, last-updated, lead) lives in each `STATUS.md`.
- The **root `README.md` master registry table** is a *hand-maintained denormalized view* that duplicates all of the above.
- **Owner identity is free text** (`"Eialarasu"`) repeated across every file — there is no user record, so a rename requires editing many files, and there is no way to model a person belonging to multiple projects.

Consequences: registry drift risk, brittle regex parsing (e.g. a prior `.ai` TLD truncation bug), and no relational foundation for the planned PocketBase web app (`BK-008`) or RBAC (`BK-007`).

## 2. Decision

Introduce a **relational JSON data layer** under `data/` as the source of truth for **structural** portfolio metadata, designed to map 1:1 onto future PocketBase collections:

| File | Role | Future PocketBase Collection |
| :--- | :--- | :--- |
| `data/users.json` | **User master** — people who own/participate in initiatives | `users` |
| `data/portfolio.json` | **Project master** — stable project metadata | `projects` |
| `data/memberships.json` | **Join table** — many-to-many user↔project with role | `memberships` |
| `data/*.schema.json` | JSON Schema for each — doubles as the PB collection spec | (schema) |

**Ownership boundaries (what remains canonical where):**
- `data/` owns **structural/relational** data: identity, archetype, repo URL, dev environment, ownership, memberships.
- Each `STATUS.md` remains canonical for **live executive status** (health, wins, focus, blockers, last-updated) — the daily scraper contract (`<= 35 lines`) is untouched.
- The **root `README.md` master table becomes a GENERATED artifact** rendered from `data/`, wrapped in `<!-- BEGIN:registry -->` / `<!-- END:registry -->` markers. It is never hand-edited again.

This is the **Option A** model (JSON = stable index; STATUS.md = live status; README/dashboard generated). Full migration of live status into the datastore is deferred to `BK-008`.

## 3. Relationship Model

Two masters joined by an explicit relationship:

```text
users.json ──1───many── memberships.json ──many───1── portfolio.json ──id/slug──> projects/LAB-XXX/STATUS.md
     ▲                                                        │
     └───────────────── owner_id (1:1 primary owner) ─────────┘
```

- **1:1 primary ownership**: every project has a required `owner_id` referencing a user. Mirrors today's single "Lead" and keeps the dashboard owner-pill trivial.
- **Many-to-many participation**: `memberships.json` records `(user_id, project_id, role)` tuples, allowing a person to belong to multiple projects and a project to have multiple participants. The primary owner is also represented as a membership with `role: "owner"` for a uniform relational view.
- **Roles** (`owner`, `lead`, `contributor`, `stakeholder`, `reviewer`) form the seed of the RBAC model that `BK-007` will enforce.

> **Why both `owner_id` and `memberships`?** `owner_id` is the fast, always-present 1:1 pointer that matches the current UI and avoids a join for the common case. `memberships` is the future-proof M2M layer. In PocketBase, `owner_id` becomes a single `relation` field and `memberships` becomes its own collection — additive, no rewrite.

## 4. Identity & ID Conventions

- **User IDs**: human-readable slugs, `usr-<name-slug>` (e.g. `usr-eialarasu`). Stable and migration-friendly; PocketBase keeps them as a unique `key` field alongside its own record ID.
- **Project IDs**: existing `LAB-XXX` (unchanged). `slug` mirrors the directory slug.
- **Membership IDs**: `mem-<project>-<user>` (e.g. `mem-lab004-abishek-singhavi`).
- **Referential integrity is enforced** by the validator (see §6): no orphan `owner_id`, no dangling membership FK, `data/` records and `projects/` directories in strict lockstep.

## 5. PocketBase Mapping (Forward Compatibility)

| JSON field | PocketBase field type |
| :--- | :--- |
| `users.id` | `text` (unique key) |
| `users.role`, `users.org`, `users.email`, `users.github_handle`, `users.active` | `text` / `email` / `bool` |
| `portfolio.owner_id` | `relation` → `users` (single) |
| `portfolio.archetype` | `select` |
| `portfolio.dev_environment` | `select` (`cloud` / `local`) |
| `memberships.user_id`, `memberships.project_id` | `relation` → `users` / `projects` |
| `memberships.role` | `select` |

When `BK-008` lands, the seed JSON is imported directly as collection records; the generator scripts become PocketBase API reads. No schema redesign required.

## 6. Validation (New Referential-Integrity Pillar)

`validate_portfolio.py` gains relational checks:
1. Every `portfolio[].owner_id` resolves to a `users.json` record.
2. Every `data/portfolio.json` record has a matching `projects/LAB-XXX-<slug>/` directory, and vice-versa (true lockstep — supersedes the old "ID substring present in README" check).
3. Every `memberships[].user_id` / `project_id` resolves (no dangling FKs); each project has at least one `owner` membership matching its `owner_id`.
4. Each `STATUS.md` "Owner / Lead" text matches the resolved owner's `name` (drift detection).
5. All JSON parses and conforms to its `*.schema.json`.

## 7. Migration Plan

1. Ratify this RFC. ✅
2. Author `data/` schemas + seed `users.json`, `portfolio.json`, `memberships.json` from current state.
3. Add `scripts/generate_registry.py` to render the README master table from `data/`.
4. Wire `generate_dashboard.py` / `generate_status.py` to prefer `data/` (regex fallback retained for safety during transition).
5. Add the referential-integrity validator pillar.
6. Wrap the README table in markers; regenerate; lockstep `BACKLOG`/`CHANGELOG`/journal.
7. **(Deferred → `BK-008`)** Import `data/` into PocketBase; migrate live status out of `STATUS.md`; generators become API clients.

## 8. Risks & Mitigations

| Risk | Mitigation |
| :--- | :--- |
| A fourth copy of data increases drift | README table becomes generated; validator enforces `data/`↔`projects/`↔`STATUS.md` lockstep. |
| Consumer scripts break during transition | Scripts prefer `data/` but retain regex fallback; no hard cutover. |
| Schema diverges from eventual PocketBase | Schema authored to PB field types up front (§5). |
| Owner rename drift | Single source (`users.json`); validator flags STATUS name mismatch. |
