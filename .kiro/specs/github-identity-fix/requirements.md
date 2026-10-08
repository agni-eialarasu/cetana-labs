# GitHub-Handle Identity Fix (RFC-016 Phase 1) — Requirements

| Property | Value |
| :--- | :--- |
| **Spec ID** | `github-identity-fix` |
| **Feature** | Make `github_handle` the single authoritative user identity: ONE `users` record per GitHub identity. Eliminate the seed-vs-OAuth duality so project ownership and auth/`is_admin` live on the SAME record. Includes a one-off migration merging the existing duplicate rows. |
| **Backlog** | `BK-034` (`TSK-074`, SPRINT-13) |
| **Work class** | **Sprint deliverable + security-sensitive (identity + LIVE DATA MIGRATION)** → **FULL gate**, with explicit no-orphan + no-privilege-leak criteria. |
| **Depends on** | `RFC-LAB-000-016` D70 (merged `0353bfc`), `BK-030` (`is_admin` + `RULE_ADMIN`), `BK-014` (owner relation + reconciliation). |
| **RFCs** | `RFC-LAB-000-016` (Decision 1), `RFC-LAB-000-008` (RBAC/identity), `RFC-LAB-000-002` (relational data — amended). |
| **Executor role** | **Kiro IDE** (escalated per RFC-014 — identity path + a migration touching live records; needs behavioral verification). |
| **Source** | RFC-016 Phase 1. Triggered by the "two rows of you" bug (`@agni-eialarasu` as both the Unlinked OAuth row and the seeded `usr-eialarasu` owner of LAB-000..003). |

---

## 1. Introduction

**Current design (verified in `auth.svelte.ts` + `pb_provision.py`):** `users` has `createRule=""` so GitHub OAuth creates a NEW auth record on sign-in; ownership is "resolved separately by `github_handle`" into the UI only (`resolveSeededOwner`), never merged into one record. So a seeded owner (`usr-eialarasu`, owns LAB-000..003) and that same human's OAuth record (`o43801zyav6cwmd`, Unlinked, owns nothing) coexist as two rows.

**This Spec inverts that:** the OAuth record IS the owner record, keyed by `github_handle`. One human = one row.

## 2. Current-state facts (verified 2026-10-08 on `main`)
- `pb_provision.py`: `users` is PocketBase's default auth collection, EXTENDED with `github_handle` (plain text, **no unique index today**), `is_admin`, `seed_id`, `role`, `org`, `active`. `createRule=RULE_PUBLIC` (OAuth can create), `updateRule=RULE_ADMIN`, `deleteRule=None`.
- `auth.svelte.ts`: `resolveSeededOwner(login)` filters `github_handle ~ login` and maps to the UI `User` — a **display-only link**, no write. `#resolve()` sets `identity.linkedUser` or leaves unlinked.
- `OWNER_RULE` is `owner.github_handle = @request.auth.github_handle` — so write-authority ALREADY keys on the auth record's `github_handle`. The gap is purely that the auth record and the seeded owner record are two different rows.
- Live dup: seeded `usr-eialarasu` (handle `agni-eialarasu`, owns LAB-000..003) + OAuth `o43801zyav6cwmd` (handle unset/mismatched, `is_admin`).

## 3. Requirements (EARS acceptance criteria = Definition of Done)

### R1 — `github_handle` is unique and authoritative
- **R1.1** `users.github_handle` SHALL have a **unique index** (case-insensitive) so two records cannot share a handle. Empty/null handle is allowed (a pending seeded owner, e.g. Arun Elambaram) and is NOT subject to uniqueness.
- **R1.2** The handle SHALL be the key by which a human is identified across sign-in, ownership, and admin.

### R2 — Upsert-by-handle on sign-in (no second row)
- **R2.1** On GitHub OAuth sign-in, WHEN a `users` record already exists with the OAuth identity's `github_handle` (case-insensitive), the session SHALL bind to THAT record — enriching it with auth/OAuth fields — and SHALL NOT create a second record.
- **R2.2** WHEN no record matches the handle, exactly ONE new record SHALL be created, keyed by that handle (the genuinely-new developer onboarding path).
- **R2.3** The OAuth record's `github_handle` SHALL be populated from the GitHub identity (not left empty), so R2.1 works on the next sign-in. (The root cause of the live dup was an empty/mismatched handle on the OAuth row.)
- **R2.4** `resolveSeededOwner` (display-only link) SHALL be removed/replaced — ownership is now intrinsic to the single record, not a separate UI resolution.

### R3 — One-off migration of existing duplicates
- **R3.1** A **scripted** migration SHALL merge the existing OAuth dup (`o43801zyav6cwmd`) INTO the seeded `usr-eialarasu`: set the surviving record's auth/OAuth binding + `is_admin`, preserve its ownership of LAB-000..003, then delete the orphan OAuth row. Generalize to any (seeded, oauth) pair sharing a human.
- **R3.2** The migration SHALL re-point any `projects.owner` relations atomically — **no project may be left orphaned** (owner relation is required; D-CRUD-2 soft-delete guard applies).
- **R3.3** The migration SHALL be **reversible by reseed** (`pb_import.py` from `data/users.json` + `data/portfolio.json`) and SHALL be verified against the live DB before + after (row counts, ownership intact).

### R4 — Security invariants (no privilege leak)
- **R4.1** The merge SHALL NOT grant `is_admin` to any record that did not already hold it on either side of the merge (no silent escalation).
- **R4.2** `RULE_ADMIN` and `OWNER_RULE` SHALL remain the authoritative server gates — unchanged. A unified identity does not widen write authority.
- **R4.3** No change to `settings`/`projects` rules; the only rule change is the `users.github_handle` unique index (R1.1).

### R5 — Scope floor
- **R5.1** Changes limited to: `pb_provision.py` + `generate_pb_schema.py` (unique index, both sources) + regenerated `pb_schema.json`; `auth.svelte.ts` (upsert-by-handle, remove display-only link); a migration script under `scripts/`. NO `settings`/`projects` rule change, no `app/web` UI route change beyond the auth store.

## 4. Human Verification Plan (the `/review-pr` evidence)
- **V1 — The bug is gone:** sign in as `@agni-eialarasu` → exactly ONE row (owns LAB-000..003 AND is admin); no second Unlinked row. (R2/R3)
- **V2 — New developer:** sign in with a GitHub handle not in `users` → exactly one new record created, keyed by handle; a second sign-in creates no duplicate. (R2.1/R2.2)
- **V3 — Uniqueness enforced:** attempt (via admin/SDK) to create a second record with an existing handle → rejected by the unique index. (R1.1)
- **V4 — No orphans:** after the migration, every project in `data/portfolio.json` still has a valid live `owner`; `just export-live-data` shows no ownership drift. (R3.2)
- **V5 — No privilege leak:** the merge grants admin to no record that lacked it; a non-admin merged identity is still non-admin; forced client `isAdmin` still 403s server-side. (R4)
- **V6 — Reversible + gates:** reseed restores the pre-migration state; `just validate-local` green (incl. generator `--check`); `pnpm build`/`check` clean. (R3.3/R5)
