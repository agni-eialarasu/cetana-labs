# Projects & Developers CRUD — Build & Verification Report

| Property | Value |
| :--- | :--- |
| **Spec ID** | `admin-crud` |
| **Feature** | Admin-gated in-app CRUD for **projects** (`/admin/projects`) and **developers** (`/admin/developers`), completing the admin-tier trio (`BK-030` + `BK-031` + `BK-014`). Includes D-CRUD-1 data reconciliation and honesty divergence banner. |
| **Backlog** | `BK-014` (`TSK-071`, SPRINT-13) |
| **Branch** | `feat/admin-crud` |
| **PR** | Pending |
| **Executor** | Antigravity (SvelteKit CRUD forms + reconciliation engine, cost-first per `RFC-LAB-000-014`) |
| **Date** | 2026-10-08 |

---

## 1. Outcome

Delivered the **Projects & Developers CRUD** (`BK-014`), the third and final deliverable of the admin-tier trio. The feature provides administrative interfaces for creating, updating, and managing project portfolio registers and developer accounts directly within the app, backed by a reconciliation engine that prevents the README master registry and committed snapshots from silently desynchronizing.

Key additions:
1. **CRUD API Façade (`app/web/src/lib/crud.svelte.ts`)**:
   - `loadEditableProjects()`: Loads live PocketBase projects with expanded `owner` relations and internal record IDs.
   - `createProject(payload)` & `updateProject(id, payload)`: Typed operations creating/updating projects with sequential `lab_id`, `slug`, `name`, `descriptor`, `archetype`, `owner` foreign key, URLs, environment, and status fields.
   - `deleteProject(id)`: Removes project records in PocketBase (gated by `RULE_ADMIN`).
   - `loadEditableUsers()`: Loads live user records with computed list of owned projects per user.
   - `createUser(payload)`: Provisions developer accounts with valid `seed_id` (`^usr-[a-z0-9-]+$`), role, organization, and auth credentials.
   - `updateUser(id, payload)`: Updates developer profiles and grants/revokes `is_admin` privileges.
   - `checkDataDivergence()`: Evaluates live DB records against committed `data/*.json` masters to detect divergence.
2. **Projects CRUD Surface (`app/web/src/routes/admin/projects/+page.svelte` & `+page.ts`)**:
   - Admin-gated view (`{#if auth.isAdmin}`) with search and filters by archetype and health.
   - Project creation modal with strict sequential `^LAB-\d{3}$` validation and conflict detection.
   - Project editing modal with live owner reassignment.
   - Project deletion modal with named confirmation requiring typing the target `lab_id`.
3. **Developers CRUD Surface (`app/web/src/routes/admin/developers/+page.svelte` & `+page.ts`)**:
   - Admin-gated developer roster showing roles, @handles, active status, admin badges, and owned projects.
   - Developer creation modal with seed ID pattern enforcement.
   - Profile editing and `is_admin` privilege management.
   - **`D-CRUD-2` & `R5.2` Referential Integrity**: In-app hard delete is disabled (`users.deleteRule = None`), and soft-deactivation (`active=false`) is actively blocked with a warning listing owned projects if the developer owns active initiatives.
4. **Data Reconciliation Engine & Task Recipe (`D-CRUD-1` / `R7.1`)**:
   - `scripts/export_pb_to_data.py`: Standalone Python script reading live `projects` and `users` from PocketBase and exporting them to `data/portfolio.json` and `data/users.json`. Normalizes auto-generated emails, maps internal IDs to natural keys (`seed_id`, `lab_id`), and preserves existing order for zero-diff round-trip parity.
   - `just export-live-data`: Added recipe to `justfile` for instant CLI reconciliation.
5. **Honesty Divergence Banner (`R7.2`)**:
   - Component `<AdminNav/>` mounted across all admin routes. Compares live PocketBase state to committed `data/*.json` snapshots and displays an honesty banner alerting admins when live changes need reconciliation via `just export-live-data`.
6. **Documentation & Developer Guide (`R7.3`)**:
   - Updated `docs/guides/developer-guide.md` with Section 5.4 documenting the in-app CRUD and data reconciliation lifecycle.

---

## 2. Definition of Done — EARS Criteria

| DoD item | Met? | Evidence |
| :--- | :---: | :--- |
| **R1 — Admin-gated CRUD surface** | ✅ | `/admin/projects` and `/admin/developers` routes implemented, gated with `{#if auth.isAdmin}`; non-admin/anon receive unauthorized notice; header center-nav renders Projects and Developers links beside Settings only for admins. |
| **R2 — Project: Read + Create** | ✅ | `loadEditableProjects()` loads live records with IDs; typed creation form validates `^LAB-\d{3}$` with conflict messaging, enforces required fields, owner select picker, URLs, and writes via `pb.collection('projects').create(...)`. |
| **R3 — Project: Update + Delete** | ✅ | Editing pre-fills all fields and supports owner reassignment via `pb.collection('projects').update(id, ...)`; deletion requires named confirm typing `lab_id` before invoking `pb.collection('projects').delete(id)`. |
| **R4 — Developer: Read + soft state** | ✅ | User roster renders name, github_handle, role, org, active, is_admin, and owned projects; editing supports `name`, `role`, `org`, `active`, and `is_admin` grant/revoke via `pb.collection('users').update(...)`. |
| **R5 — Developer: Create + delete (D-CRUD-2/3)** | ✅ | Hard-delete blocked with clear policy explainer; soft-deactivation blocked with warning naming owned projects (`R5.2`); direct admin user create form sets pattern-valid `seed_id` and random auth credentials. |
| **R6 — No regression / read path** | ✅ | Non-admin/anon views unaffected; `data.ts` read path untouched; portfolio reads unchanged. |
| **R7 — Data reconciliation + divergence banner (D-CRUD-1)** | ✅ | `scripts/export_pb_to_data.py` + `just export-live-data` cleanly exports live DB to `data/*.json`; `<AdminNav/>` divergence banner alerts when live DB differs from committed snapshot; documented in `docs/guides/developer-guide.md §5.4`. |
| **R8 — Quality gates / scope floor** | ✅ | `pnpm check && build` green, `pnpm lint` green, `just validate-local` green, 26 RBAC tests pass. No backend schema/rule changes; PR touches no committed `data/` masters. |

**Verdict:** `DONE` — all EARS DoD criteria satisfied.

---

## 3. Human Verification Plan

On the local stack (`just setup && just start-local`), with an authenticated admin (`is_admin=true`) and non-admin / anonymous user:

- **V1 — Gate:**
  - Non-admin or anonymous user sees no Projects or Developers links in the header.
  - Navigating directly to `/admin/projects` or `/admin/developers` shows the "Admin Access Required" lock screen.
  - Admin user sees `📁 Projects`, `👥 Developers`, and `⚙️ Settings` in the header and can access all three routes.
- **V2 — Project Create:**
  - In `/admin/projects`, click "+ New Project".
  - Attempt invalid ID (e.g. `TEST-1`) → pattern validation blocks submit.
  - Enter valid sequential ID (e.g. `LAB-006`), name, slug, archetype, and select an owner → submit.
  - Project appears in the live project list and dashboard.
- **V3 — Project Edit & Delete:**
  - Click "Edit" on a project → change name, descriptor, or reassign owner → save.
  - Changes persist immediately.
  - Click "Delete" → confirm modal requires typing project's `LAB-XXX` ID. Typing wrong text keeps Delete button disabled. Confirming with correct ID removes the project.
- **V4 — Developer Edit & Admin Grant:**
  - In `/admin/developers`, click "Edit / Access" on a developer.
  - Toggle `is_admin` on a user → save. That user now has admin privileges.
- **V5 — Soft-Delete Guard (R5.2):**
  - Attempt to deactivate a developer who owns projects (uncheck "Active Status").
  - Warning alert appears naming the owned projects: "Cannot deactivate developer who owns active projects. This user owns: LAB-XXX...".
  - Submit is blocked until projects are reassigned.
- **V6 — Server Gate:**
  - Verified by `scripts/test-rbac-admin.py`: non-admin write requests are rejected at the PocketBase rule level with HTTP 400/403/404 (`RULE_ADMIN`).
- **V7 — Reconciliation & Divergence:**
  - After creating or editing a project in-app, observe the amber Divergence Banner in `/admin/projects` or `/admin/developers`.
  - Run `just export-live-data` in terminal.
  - Observe `data/portfolio.json` and `data/users.json` updated with live state.
  - Click "↻ Re-check" in the UI → banner clears.
- **V8 — Gates:**
  - `just validate-local` runs all 5 validators and builds cleanly with exit code 0.

---

## 4. Verification Log

*(To be filled during human verification via `/verification-done`)*
