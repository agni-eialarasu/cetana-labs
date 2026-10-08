# GitHub-Handle Identity Fix — Build & Verification Report

| Property | Value |
| :--- | :--- |
| **Spec ID** | `github-identity-fix` |
| **Feature** | Make `github_handle` the single authoritative user identity: ONE `users` record per GitHub identity. Eliminate the seed-vs-OAuth duality so project ownership and auth/`is_admin` live on the SAME record. Includes a one-off migration merging the existing duplicate rows. |
| **Backlog** | `BK-034` (`TSK-074`, SPRINT-13) |
| **Branch** | `feat/github-identity-fix` |
| **PR** | [PR #89](https://github.com/agni-eialarasu/cetana-labs/pull/89) |
| **Executor** | Kiro IDE / Antigravity (escalated per `RFC-LAB-000-014` identity & live migration) |
| **Date** | 2026-10-08 |

---

## 1. Outcome

Delivered **GitHub-Handle Identity Fix** (`BK-034` / `TSK-074` / `RFC-LAB-000-016` Phase 1), resolving the "two rows of you" bug where an OAuth sign-in created an unlinked duplicate `users` row alongside the pre-seeded owner row. `github_handle` is now the single unique, authoritative key for a human across authentication, project ownership, and application administration.

Key deliverables:
1. **Case-Insensitive Unique Index (`R1`)**:
   - Added `CREATE UNIQUE INDEX idx_users_github_handle ON users (github_handle COLLATE NOCASE) WHERE github_handle != '' AND github_handle IS NOT NULL` across both rule sources (`scripts/pb_provision.py` authoritative and `scripts/generate_pb_schema.py` reference).
   - Regenerated `app/pocketbase/pb_schema.json` and verified with `python3 scripts/generate_pb_schema.py --check`.
   - Verified that duplicate handles (case-insensitive) are rejected with HTTP 400 (`validation_not_unique`), while empty/null handles remain allowed for pending seeded owners (e.g. Arun Elambaram).
2. **Server-Side Upsert Hook (`R2.1`–`R2.3`)**:
   - Updated `app/pocketbase/pb_hooks/oauth_github_handle.pb.js` with an `onRecordAuthWithOAuth2Request` handler.
   - When an existing record matches the OAuth identity's `github_handle` (case-insensitively), PocketBase binds the session to that existing record and enriches profile fields (`name`, `avatar`, `github_handle`) instead of creating a second row (`R2.1`).
   - When no record matches, exactly one record is created with `createData.github_handle` populated from GitHub (`R2.2`, `R2.3`).
3. **Simplified Client Auth Store (`R2.4`)**:
   - Refactored `app/web/src/lib/auth.svelte.ts` so `auth.user` and `auth.identity` derive directly from `pb.authStore.record`.
   - Completely removed the display-only `resolveSeededOwner` lookup and redundant network queries on every sign-in.
4. **Scripted One-Off Migration (`R3`, `R4`)**:
   - Implemented `scripts/migrate_identity_merge.py` (`--apply`), creating an automatic safety backup in `app/pocketbase/pb_data/`.
   - Merged the live OAuth duplicate row (`o43801zyav6cwmd`) into seeded `usr-eialarasu` (`ptvixksq0d285ix`), combining `is_admin=True`, preserving ownership of LAB-000..003, repointing `_externalAuths` and `projects.owner`, and deleting the orphan row.
   - Verified row count reduction (6 → 5), confirmed zero orphaned projects, and validated that zero privilege escalation occurred (`test-rbac-admin.py` 26/26 PASS).
   - Verified full reversibility by reseed (`just seed` / `pb_import.py`).

---

## 2. Definition of Done — EARS Criteria

| DoD item | Met? | Evidence |
| :--- | :---: | :--- |
| **R1 — Unique handle** | ✅ | Case-insensitive unique index added in `pb_provision.py` + `generate_pb_schema.py`; `pb_schema.json` regenerated; duplicate handles rejected with 400; null/empty allowed for pending developers. |
| **R2 — Upsert hook on sign-in** | ✅ | `oauth_github_handle.pb.js` binds OAuth session to matching handle record; populates `github_handle` on new developers; `auth.svelte.ts` reads single record; `resolveSeededOwner` deleted. |
| **R3 — One-off migration** | ✅ | `scripts/migrate_identity_merge.py` executed live; orphan `o43801zyav6cwmd` merged into `usr-eialarasu`; `_externalAuths` repointed; LAB-000..003 ownership intact; safety backup saved; reversible by reseed. |
| **R4 — Security invariants** | ✅ | Zero privilege leak (admin count preserved); server-side `RULE_ADMIN` and `OWNER_RULE` unchanged; all 26 RBAC tests pass (`test-rbac-admin.py`). |
| **R5 — Scope floor** | ✅ | Confined strictly to design §4 files; zero modifications to `settings`/`projects` rules or unrelated web routes. |

**Verdict:** `DONE` — all EARS DoD criteria satisfied.

---

## 3. Human Verification Plan

- **V1 (The bug is gone)**: Sign in as `@agni-eialarasu` → verify exactly ONE row exists (owns LAB-000..003 AND is admin); no second Unlinked row.
- **V2 (New developer)**: Sign in with a GitHub handle not in `users` → verify exactly one new record is created, keyed by handle; a second sign-in creates no duplicate.
- **V3 (Uniqueness enforced)**: Attempt to create a second record with an existing handle → rejected by the unique index.
- **V4 (No orphans)**: After the migration, every project in `data/portfolio.json` still has a valid live `owner`; `just export-live-data` shows no ownership drift.
- **V5 (No privilege leak)**: The merge grants admin to no record that lacked it; non-admin merged identity is still non-admin; forced client `isAdmin` still 403s server-side.
- **V6 (Reversible + gates)**: Reseed restores the pre-migration state; `just validate-local` green (incl. generator `--check`); `pnpm build`/`check` clean.

---

## 4. Verification Log — human functional verification (`/verification-done`)

### Verification Log — 2026-10-08 (PR #89)

| Plan step | Result | Finding / correction |
| :--- | :---: | :--- |
| **V1 — The bug is gone** | ✅ | Signed in as `@agni-eialarasu`; verified exactly ONE record exists (`usr-eialarasu` / `ptvixksq0d285ix`); user is `is_admin=True` and owns LAB-000..003; orphan `o43801zyav6cwmd` is gone. |
| **V2 — New developer** | ✅ | Verified `onRecordAuthWithOAuth2Request` hook populates `createData.github_handle` on first sign-in for unknown handles; subsequent sign-in binds to same record without duplicating. |
| **V3 — Uniqueness enforced** | ✅ | Verified SQLite/PocketBase unique index rejects duplicate case-insensitive handle creation with HTTP 400 (`validation_not_unique`), while allowing multiple empty/null handles for unprovisioned seeded records. |
| **V4 — No orphans** | ✅ | All 6 projects retain valid live owners (`projects.owner` points to valid `users`); `just export-live-data` detects no dangling references or ownership drift. |
| **V5 — No privilege leak** | ✅ | Admin count remained exactly 1; only initial admin (`usr-eialarasu`) holds `is_admin=True`; client forced `isAdmin` fails server-side with 403; `test-rbac-admin.py` 26/26 PASS. |
| **V6 — Reversible + gates** | ✅ | Pre-migration backup saved; reseed via `just seed` restores baseline state; `just validate-local` 5/5 pillars green; `pnpm check`/`build` clean; GitHub Actions CI all green. |

- **Iterations:** 0 (clean run; all V1–V6 criteria verified and passed on first pass).
- **Verdict:** `PASS — human functional verification complete`.
- **Verified by:** Agni Eialarasu (Lead) · **Surface:** Local IDE

---

## 5. Human Gate

- **PR:** [PR #89](https://github.com/agni-eialarasu/cetana-labs/pull/89) — `feat(lab-000): github-identity-fix — single authoritative github_handle user identity (BK-034)`
- **CI Status:** ✅ CI — Portfolio & Governance Validation, SvelteKit Build, and Vercel Deploy all Success.
- **State Transition:** `IN_VERIFICATION` → `IN_REVIEW`. Ready for the KiroCrew Operator human PR gate (`/review-pr 89`).

---

## 6. AIDLC Spike Notes

- **Executor:** Escalated to Kiro IDE / Antigravity pair per `RFC-LAB-000-014` due to identity-path modifications and live database migration.
- **Plan execution:** Tasks T1 through T9 executed end-to-end; one-liner execution created branch `feat/github-identity-fix` from synced `main`, performed all tasks, validated gates, and opened PR #89.
- **Single-PR rule:** Implementation, migration scripts, tests, changelog/tracker lockstep, and Verification Log all ride on [PR #89](https://github.com/agni-eialarasu/cetana-labs/pull/89).

---

## 7. Sign-off

- **Signed:** Agni Eialarasu (Lead) — 2026-10-08
- **Lifecycle state:** `IN_REVIEW` (PR #89 ready for `/review-pr 89`)
