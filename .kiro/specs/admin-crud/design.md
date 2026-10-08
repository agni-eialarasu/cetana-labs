# Projects & Developers CRUD (admin UI) — Design

| Property | Value |
| :--- | :--- |
| **Spec ID** | `admin-crud` (`BK-014` / `TSK-071`) |
| **Consumes** | `is_admin` + write rules (BK-030) · `auth.isAdmin` + admin-editor pattern (BK-031) · `data.ts` read path |
| **Executor** | Antigravity (CRUD forms over the SDK; cost-first) — escalate if the reconciliation/owner handling proves deeper |

## 1. Approach

Reuse BK-031's proven admin-editor pattern (gate → id-carrying load → SDK write → live-refresh) and extend it to two collections with richer forms. The genuinely new engineering is **not** the forms — it's **D-CRUD-1 reconciliation**: keeping the README registry honest when the live DB diverges from committed `data/`. Treat that as the core, not an afterthought.

## 2. The source-of-truth model (the heart of this Spec)

```
         in-app CRUD (admin)                     governance flow (committed)
   admin ──────────────▶ PocketBase (live) ──reconcile──▶ data/*.json ──generate_registry──▶ README registry
                              ▲                 (explicit     (committed       (regenerated,
                              │                  export step)  masters)         gated, PR)
   GitHub sign-in ───────────┘
```
- **Live writes** go to PocketBase (the app the user sees).
- **`data/*.json`** stays the committed source-of-truth for the README registry + the snapshot fallback.
- They reconcile via an **explicit export** (R7.1) — never a silent background sync (D-CRUD-1). Between an in-app edit and a reconciliation, the DB and `data/` legitimately diverge; R7.2's banner makes that visible instead of letting the README quietly lie.

> **Why not auto-sync?** Auto-writing `data/` from the app would (a) require the app to commit to git (it can't / shouldn't), and (b) bypass the human gate on registry changes. The explicit export keeps registry changes inside the normal governance+gate flow.

## 3. Components (reusing BK-031)

| Piece | Reuse / new |
| :--- | :--- |
| `auth.isAdmin` gate | **reuse** (BK-031) |
| id-carrying loaders (`loadEditableProjects/Users`) | **new**, same shape as `loadEditableSettings` |
| write wrappers (`createProject`/`updateProject`/`deleteProject`/`updateUser`) | **new**, thin over `pb.collection(x).create/update/delete` |
| `admin/projects/+page.svelte`, `admin/developers/+page.svelte` | **new** routes, `{#if auth.isAdmin}` gated (BK-031 pattern) |
| owner picker | **new** — a select populated from `users` (dedup, show name+handle) |
| divergence banner + reconciliation | **new** — the D-CRUD-1 piece |

## 4. Forms (field-accurate to §2 of requirements)

- **Project form:** `lab_id` (text, `^LAB-\d{3}$` + uniqueness-on-conflict message), `slug`, `name` (required), `descriptor`, `archetype` (select, 5 values), `owner` (user picker → relation id), `repo_url`/`reference_url` (url validation), `dev_environment` (cloud/local), `status_source` (local/remote), `status_health` (HEALTH_VALUES select), `status_note`.
- **User form (edit):** `name`, `role` (5 values), `org`, `active` (toggle), `is_admin` (toggle — grants/revokes admin, A1 R2.6). `github_handle`/`seed_id` shown; create path per R5.3.

## 5. Delete semantics (D-CRUD-2)

- **Project delete:** `pb.collection('projects').delete(id)` behind a typed confirm (name the project). Rule allows it (admin).
- **User delete:** `users.deleteRule = None` → **hard delete impossible in-app**. UI offers `active=false` (soft). If the user owns projects (`owner` relation, required/cascade=False), block/warn with the owned-project list — a hard delete would orphan a required relation. Reassign-first guidance.

## 6. Reconciliation (R7)

- **`scripts/export_pb_to_data.py`** (+ `just export-live-data`): authenticates (admin or superuser), reads `projects`+`users` via the SDK/REST, writes `data/portfolio.json`+`data/users.json` in the committed shape (reverse of `pb_import.py`). An admin runs it after a round of edits; then the normal flow (`generate_registry` + gated PR) updates the README.
- **Divergence banner (R7.2):** the CRUD surface compares a cheap signature of live rows vs the bundled `data/` snapshot (count + a hash of key fields); on mismatch, show "live DB has unsynced changes vs committed `data/` — run `just export-live-data` then commit." State, not a fabricated %.

## 7. Risk / phasing (D-CRUD-3)

This is the **biggest** admin-tier Spec — richer forms + the owner relation + the reconciliation. If one clean build is too large, ship **project CRUD + reconciliation + banner (R1–R3, R6–R8)** first, **user CRUD (R4–R5)** as a fast-follow. The executor flags the split at build start rather than shipping half-verified. Honest phasing beats a rushed monolith.

## 8. Decisions
- **D-CRUD-1** — explicit export reconciliation, never silent sync; divergence banner shows state.
- **D-CRUD-2** — user hard-delete blocked (rule + referential integrity); soft `active=false`; project delete allowed with confirm.
- **D-CRUD-3** — phase project-CRUD before user-CRUD if the single build is too large.
- **D-CRUD-4** — reuse BK-031's gate/pattern verbatim; the new risk is data-sync, not auth.

## 9. Rollback
Frontend + a standalone export script; no schema/rule/`data/` change in the PR itself. Revert returns CRUD to admin-UI-only; the export script is inert if unused.
