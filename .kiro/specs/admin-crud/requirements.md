# Projects & Developers CRUD (admin UI) — Requirements

| Property | Value |
| :--- | :--- |
| **Spec ID** | `admin-crud` |
| **Feature** | Admin-gated in-app CRUD for **projects** and **developers (users)** — create / edit / delete, visible and writable only to the `is_admin` tier. Last of the admin-tier trio (after BK-030 auth + BK-031 settings UI). |
| **Backlog** | `BK-014` (`TSK-071`, SPRINT-13) |
| **Work class** | **Sprint deliverable** → **FULL gate**. |
| **Depends on** | `BK-030` (`is_admin` + `projects`/`users` write rules — **merged**), `BK-031` (`auth.isAdmin` + the admin-editor pattern — **merged**). |
| **RFCs** | `RFC-LAB-000-008` A1 (`is_admin`), `RFC-LAB-000-002` (relational data model), `RFC-LAB-000-005` (Sleek UI). |
| **Executor role** | Default **Antigravity** (SvelteKit CRUD forms over the existing SDK write path, pattern established by BK-031); escalate to Kiro IDE only if the owner-relation / data-sync handling proves deeper (record why). |
| **Source** | Operator brainstorm 2026-10-08 (item #4 of six). |

---

## 1. Introduction & the central design decision (READ FIRST)

BK-030 opened the write rules; BK-031 proved the admin-editor pattern on `settings`. BK-014 extends it to **projects** and **users**. But projects/users carry a tension `settings` did not:

> **`data/portfolio.json` + `data/users.json` are the committed source-of-truth.** They feed BOTH (a) `scripts/generate_registry.py` → the **README master registry**, AND (b) the UI's snapshot fallback (`VITE_PB_SOURCE=snapshot`). In-app CRUD writes to **PocketBase** — which **desyncs** the live DB from `data/` and the generated README. Editing a project in-app would make the app and the README disagree, and a later `generate_registry --check` would still pass (it reads `data/`, not the DB) while the DB has drifted.

**This Spec resolves that explicitly** (not silently): see **D-CRUD-1** below. The chosen scope avoids shipping a desync footgun.

**Decisions (recorded):**
- **D-CRUD-1 — PocketBase is the live write target; `data/` stays the committed seed/source-of-truth, and the two are reconciled by an explicit EXPORT step, not auto-magic.** In-app CRUD writes to PocketBase (the live app). To keep the README registry + snapshot truthful, this Spec adds a **documented reconciliation**: an admin action / script to **export the live `projects`+`users` back to `data/*.json`** (then the normal governance flow regenerates the registry + commits via the gate). The app shows a **"live DB has unsynced changes vs committed `data/`"** honesty banner when they diverge (reusing the metric-honesty principle — show state, not a fake number). *Rationale:* a master control plane must not let its own registry silently lie; the reconciliation is a deliberate, auditable step, not a background sync.
- **D-CRUD-2 — delete is soft where it has referents.** A `user` that owns projects SHALL NOT be hard-deleted (the `projects.owner` relation is `required`, `cascade=False` — a hard delete would orphan projects). Deleting such a user is blocked with a clear message ("reassign their N projects first"); `active=false` is the soft path. Projects may be hard-deleted by an admin (rule allows it), with a confirm.
- **D-CRUD-3 — scope split (phase honesty).** This Spec delivers **project CRUD + user CRUD + the reconciliation/export + the divergence banner**. If that proves too large for one clean build, **project CRUD + reconciliation** ships first (R1–R4, R7) and **user CRUD** (R5) is a fast-follow — the executor flags the split at build start rather than shipping half-tested.

## 2. Current-state facts (verified 2026-10-08 on `main`)
- **Projects** (`projects` collection / `data/portfolio.json`): `lab_id` (req, `^LAB-\d{3}$`), `slug` (req), `name` (req), `descriptor`, `archetype` (select: control-plane/mini-app/research/data-collection/verification), `owner` (relation→users, **required, cascade=False**), `repo_url`, `reference_url` (url), `dev_environment` (cloud/local), `status_source` (local/remote), `status_health` (select, HEALTH_VALUES), `status_note`, `status_updated_at`.
- **Users** (`users` collection / `data/users.json`): `seed_id` (`^usr-[a-z0-9-]+$`), `name`, `github_handle`, `role` (owner/lead/contributor/stakeholder/reviewer), `org`, `active` (bool), **`is_admin` (bool, BK-030)**.
- **Rules (BK-030):** admin can create/update/delete `projects`; admin can update `users` (`users.updateRule = RULE_ADMIN`); `users.createRule = RULE_PUBLIC` (OAuth sign-in) — so **admin-created users** via the API need care (see R5.3). `users.deleteRule` is `None` (superuser-only) → **in-app user hard-delete is NOT possible by rule**; soft-delete (`active=false`) is the path (ties D-CRUD-2).
- **The admin pattern (BK-031):** `auth.isAdmin`, the `{#if auth.isAdmin}` gate, the id-carrying loader + `pb.collection(x).update/create/delete`, live-refresh via re-load — all established and reusable.

## 3. Requirements (EARS acceptance criteria = Definition of Done)

### R1 — Admin-gated CRUD surface
- **R1.1** A CRUD surface (route e.g. `base/admin/projects`, `base/admin/developers`) SHALL render ONLY when `auth.isAdmin` (reuse BK-031's gate); non-admin/anon → not-authorized notice, no controls.
- **R1.2** Entry points SHALL appear only for admins (header center-nav / admin menu, `{#if auth.isAdmin}`), beside BK-031's Settings link.

### R2 — Project: Read + Create
- **R2.1** The surface SHALL list live projects (from PocketBase, with record ids) with their key fields.
- **R2.2** An admin SHALL create a project via a typed form: `lab_id` (validated `^LAB-\d{3}$`, uniqueness surfaced on conflict), `slug`, `name` (required), `descriptor`, `archetype` (select), `owner` (picker from users), urls, `dev_environment`, `status_*`. Writes via `pb.collection('projects').create(...)` (gated by `RULE_ADMIN`).

### R3 — Project: Update + Delete
- **R3.1** An admin SHALL edit any project's fields (incl. reassigning `owner`), via `pb.collection('projects').update(id, ...)`.
- **R3.2** An admin SHALL delete a project via `pb.collection('projects').delete(id)` behind a confirm dialog (irreversible — name the project in the confirm).

### R4 — Developer (user): Read + soft state
- **R4.1** The surface SHALL list users (name, github_handle, role, org, active, is_admin).
- **R4.2** An admin SHALL edit a user's `name`/`role`/`org`/`active`/`is_admin` via `pb.collection('users').update(id, ...)` (gated). Granting/revoking `is_admin` is here (A1 R2.6).

### R5 — Developer (user): Create + delete (D-CRUD-2/3)
- **R5.1** User **hard-delete** SHALL be blocked in-app (rule: `users.deleteRule = None`); the UI offers **`active=false`** (soft) instead, with a clear explanation.
- **R5.2** A user who **owns projects** SHALL NOT be soft-deactivated without a warning naming the owned projects (reassign first).
- **R5.3** User **create**: because `users.createRule = RULE_PUBLIC`, document that in-app admin "create user" is possible but the clean path for a NEW developer is GitHub sign-in (self-creates the auth record) + an admin linking `github_handle`/`seed_id`. If a direct admin-create form is built, it SHALL set `seed_id` (pattern-valid) and NOT set a password (OAuth identities). *(May be deferred per D-CRUD-3.)*

### R6 — No regression / read path
- **R6.1** Non-admin/anon: the app renders as today (no CRUD surface, portfolio reads unchanged).
- **R6.2** The existing `data.ts` read path (snapshot/PB auto) is unchanged; CRUD ADDS write surfaces.

### R7 — Data reconciliation + honesty banner (D-CRUD-1 — the critical one)
- **R7.1** The Spec SHALL provide a **reconciliation path**: a documented script/recipe (e.g. `just export-live-data` or `scripts/export_pb_to_data.py`) that reads live `projects`+`users` from PocketBase and writes `data/portfolio.json`+`data/users.json`, so the normal governance flow (`generate_registry --check` → commit via gate) brings the README registry back in sync.
- **R7.2** The admin CRUD surface SHALL show a **divergence indicator** when the live DB differs from the committed `data/` snapshot (state, not a fabricated metric — "live DB has unsynced changes; run reconciliation") so an admin never forgets the README is now behind.
- **R7.3** The reconciliation + its governance implications SHALL be documented in the developer-guide (how in-app edits flow back to `data/` + the registry).

### R8 — Quality gates / scope floor
- **R8.1** `pnpm --dir app/web check && build`, `just validate-local`, 5 validators green.
- **R8.2** Scope floor: `app/web/**` (CRUD surfaces + nav) + the reconciliation script/recipe + developer-guide doc. **NO** schema/rule change (BK-030 owns rules). If the export script touches `data/` only via the admin-run tool (not committed by the build), the PR itself changes no `data/` masters.

## 4. Out of scope
Schema/rule changes (BK-030 owns them); the 5-role `memberships` model; bulk import; an audit log of admin edits (A1 deferred); automatic/background `data/`↔DB sync (reconciliation is an explicit step, D-CRUD-1); status-field migration into the DB (still dual-track per RFC-008 §7).

## 4b. Human Verification Plan (emitted by `/spec-run`; recorded by `/verification-done`)
On the local stack with a bootstrapped admin + a non-admin:
- **V1 — gate:** non-admin/anon see no CRUD surface; admin sees Projects + Developers admin links.
- **V2 — project create:** admin creates a project (valid `lab_id`, owner picked) → appears in the portfolio; invalid `lab_id` rejected.
- **V3 — project edit/delete:** admin edits a project (incl. owner reassign) → persists; delete behind confirm removes it.
- **V4 — user edit:** admin toggles another user's `role`/`active`/`is_admin` → persists; granting `is_admin` makes that user an admin (re-login).
- **V5 — soft-delete guard:** attempting to hard-delete / deactivate a user who owns projects → blocked/warned with the owned-project list.
- **V6 — server gate:** a non-admin hitting any write path → denied by `RULE_ADMIN` (not just UI-hidden).
- **V7 — reconciliation + divergence:** after an in-app edit, the divergence banner shows; running the reconciliation exports to `data/`, `generate_registry --check` then reflects the change.
- **V8 — gates:** `pnpm check && build` + validators green.
