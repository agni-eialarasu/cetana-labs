# Projects & Developers CRUD — Tasks (`/spec-run admin-crud`)

> Executor = **Antigravity** (CRUD forms over the SDK, BK-031 pattern; cost-first per RFC-014). Consumes BK-030 (rules) + BK-031 (gate/pattern). STOP-and-hold at the PR; never merge.
> **Phasing (D-CRUD-3):** if one clean build is too large, ship Phase A (project CRUD + reconciliation, T1–T4 + T7–T9) and flag Phase B (user CRUD, T5–T6) as a fast-follow — note the split in the PR.

---

## T0 — Preflight + baseline (STOP on failure)
- [ ] Executor clone; `just setup && just start-local` up; **bootstrap a local admin** (superuser → `/_/` → toggle `is_admin`).
- [ ] This Spec merged to `main` (merge-first).
- [ ] BK-030 (`is_admin` + `projects`/`users` write rules) + BK-031 (`auth.isAdmin`, admin-editor pattern) present on `main`.
- [ ] Create `feat/admin-crud` off up-to-date `main`; clean tree; not `main`.
- [ ] Baseline: `pnpm --dir app/web check && build` + 5 validators green.

## T1 — CRUD surface + gate → R1
- [ ] Add `admin/projects` (and `admin/developers`) routes, `{#if auth.isAdmin}` gated (reuse BK-031); `{:else}` not-authorized notice. *(R1.1)*
- [ ] Admin-only entry points beside the Settings link. *(R1.2)*

## T2 — Project read + create → R2
- [ ] `loadEditableProjects()` (with ids) + a project list. *(R2.1)*
- [ ] Project create form (field-accurate: `lab_id` `^LAB-\d{3}$`+uniqueness msg, `slug`, `name` req, `descriptor`, `archetype`, `owner` picker, urls, `dev_environment`, `status_*`) → `pb.collection('projects').create`. *(R2.2)*

## T3 — Project update + delete → R3
- [ ] Edit any project incl. owner reassign → `projects.update`. *(R3.1)*
- [ ] Delete behind a named confirm → `projects.delete`. *(R3.2)*

## T4 — Developer read + edit → R4
- [ ] User list (name/handle/role/org/active/is_admin). *(R4.1)*
- [ ] Edit `name`/`role`/`org`/`active`/`is_admin` → `users.update` (is_admin grant/revoke, A1 R2.6). *(R4.2)*

## T5 — Developer delete semantics → R5 (D-CRUD-2) *(Phase B)*
- [ ] Hard-delete blocked (rule) → offer `active=false` soft path with explanation. *(R5.1)*
- [ ] Deactivating a project-owning user → warn + list owned projects (reassign first). *(R5.2)*
- [ ] Document user-create path (OAuth sign-in + admin link); build a direct admin-create only if in scope, setting `seed_id`, no password. *(R5.3)*

## T6 — No regression → R6
- [ ] Non-admin/anon: no CRUD surface; portfolio reads unchanged; `data.ts` read path untouched.

## T7 — Reconciliation + divergence banner → R7 (D-CRUD-1, the critical piece)
- [ ] `scripts/export_pb_to_data.py` + `just export-live-data`: live `projects`+`users` → `data/*.json` (reverse of `pb_import.py`, committed shape). *(R7.1)*
- [ ] Divergence banner on the CRUD surface when live DB ≠ committed `data/` snapshot (state, not a fake %). *(R7.2)*
- [ ] developer-guide: document the in-app-edit → export → registry flow + governance implications. *(R7.3)*

## T8 — Gates / scope floor → R8
- [ ] `pnpm --dir app/web check && build`, `just validate-local`, 5 validators green. *(R8.1)*
- [ ] Scope floor: `app/web/**` + the export script/recipe + developer-guide. **NO** schema/rule change; the PR changes no committed `data/` masters (the export is an admin-run tool). *(R8.2)*

## T9 — Lockstep + PR
- [ ] `CHANGELOG.md` `[Unreleased]` → Added (BK-014/TSK-071; note phasing if split); flip `SPRINT_TRACKER.md` TSK-071 at build.
- [ ] Append `REPORT.md` (summary + V1–V8 plan incl. V6 server-gate + V7 reconciliation, left for `/verification-done`).
- [ ] Open PR `feat/admin-crud → main`; self-validate vs EARS DoD; STOP-and-hold (never merge).

## Post-build (back on the Operator)
- `/verification-done` records V1–V8 PASS → IN_REVIEW.
- `/review-pr <PR>` — full scorecard (V6 server gate + V7 reconciliation as evidence) → human merge.
- Post-merge: TSK-071 → Done. Admin-tier trio complete (BK-030 + BK-031 + BK-014).
