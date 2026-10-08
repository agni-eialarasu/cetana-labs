# GitHub-Handle Identity Fix (RFC-016 Phase 1) — Tasks

| Property | Value |
| :--- | :--- |
| **Spec ID** | `github-identity-fix` · **Backlog** `BK-034` (`TSK-074`) · **Branch** `feat/github-identity-fix` |

> Security-sensitive: a live-data migration. Run against a backup/export FIRST; verify before + after; keep it reversible by reseed.

## Tasks

- [x] **T1 — Unique handle** (R1.1): add a case-insensitive unique index on `users.github_handle` (null allowed) in BOTH `pb_provision.py` and `generate_pb_schema.py`; regenerate `pb_schema.json`.
- [x] **T2 — Upsert hook** (R2.1–R2.3): add an `OnRecordAuthWithOAuth2` hook (`pb_hooks/`) that binds the OAuth session to the existing record matching `github_handle` (enriching it) and creates a new record ONLY when no handle matches; populate `github_handle` from the GitHub identity.
- [x] **T3 — Simplify auth store** (R2.4): `auth.svelte.ts` reads the single record; remove `resolveSeededOwner` display-only link.
- [x] **T4 — Migration script** (R3): `scripts/migrate_identity_merge.py` — merge the live dup (`o43801zyav6cwmd` → `usr-eialarasu`), preserve LAB-000..003 ownership, re-point `projects.owner` atomically, delete the orphan; verify row-count + no-orphan + no-admin-gain.
- [x] **T5 — Fail-safe migration run** (R3.3): run against an export/backup first; confirm reversible by `pb_import.py` reseed.
- [x] **T6 — Security checks** (R4): assert no record gains admin it lacked; `RULE_ADMIN`/`OWNER_RULE` unchanged; forced client `isAdmin` still 403s (rule tests still 26/26).
- [x] **T7 — Scope floor** (R5): no `settings`/`projects` rule change; changes limited to the files in design §4.
- [x] **T8 — Self-validate**: `pnpm check`/`build` clean; `just validate-local` green (incl. generator `--check`). Lockstep: CHANGELOG TSK-074; SPRINT_TRACKER coherent.
- [x] **T9 — Open PR** against `main`; STOP-and-hold for `/verification-done` (V1 one-row + V4 no-orphan + V5 no-leak + V6 reversible) → `/review-pr`. Never merge.
