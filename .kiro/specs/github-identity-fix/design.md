[🏠 Repo](../../../README.md) / [📚 Docs](../../README.md) / Specs / **github-identity-fix**

# GitHub-Handle Identity Fix (RFC-016 Phase 1) — Design

| Property | Value |
| :--- | :--- |
| **Spec ID** | `github-identity-fix` · **Backlog** `BK-034` (`TSK-074`) · **Branch** `feat/github-identity-fix` |

## 1. Approach — invert "link" into "upsert"

Today the OAuth record and the seeded owner are two rows joined only by a display-time `github_handle` lookup. The fix makes the handle the record's identity so sign-in resolves to ONE row.

Two parts: (A) **forward fix** so no new dup is ever created, (B) a **one-off migration** to merge the dup that already exists.

## 2. The one real design fork — where does the upsert happen?

**Approach 1 — Client-side bind (minimal).** After `authWithOAuth2Code`, the client looks up a seeded record by handle; if found, it copies the OAuth auth binding onto that record and deletes the fresh OAuth row. *Rejected:* record delete/merge from the client needs elevated rules (today `deleteRule=None`), and doing identity surgery in the browser is fragile and hard to make atomic.

**Approach 2 — Server-side upsert via a PocketBase hook (RECOMMENDED).** Use an `OnRecordAuthWithOAuth2` hook (PocketBase `pb_hooks/`) so that when GitHub OAuth resolves, the backend binds the session to the EXISTING record matching `github_handle` (enriching it) instead of creating a new one — the create only happens when no handle matches. This is the correct layer: atomic, server-authoritative, no client privilege. The client auth store then simply reads the (single) record; `resolveSeededOwner` is removed.
- *Why this fits:* `OWNER_RULE` already keys on `@request.auth.github_handle`, so once the auth record IS the owner record, write-authority is correct with no rule widening.

**Chosen: Approach 2.** It makes identity a backend invariant, not a client dance.

## 3. The migration (one-off, scripted)

`scripts/migrate_identity_merge.py` (new):
1. Load the live `users`; find (seeded, oauth) pairs that are the same human (same `github_handle`, or the known `o43801zyav6cwmd`↔`usr-eialarasu` pair where the OAuth row's handle was empty/mismatched).
2. For each pair: ensure the surviving (seeded) record carries the OAuth auth binding + `is_admin` (only if either side already had it — R4.1), re-point any `projects.owner` to the survivor **atomically**, then delete the orphan.
3. Verify: row count drops by exactly the number of merges; every `portfolio.json` project has a valid live owner; no record gained admin it lacked.
4. Reversible: `pb_import.py` reseed from `data/` restores the pre-migration state (R3.3).

## 4. Files
| File | Change |
| :--- | :--- |
| `app/pocketbase/pb_hooks/*.js` (or provision) | `OnRecordAuthWithOAuth2` upsert-by-handle hook (R2). |
| `scripts/pb_provision.py` + `scripts/generate_pb_schema.py` | `github_handle` unique (case-insensitive) index, in both rule sources (R1.1). |
| `app/pocketbase/pb_schema.json` | Regenerated (generated artifact). |
| `app/web/src/lib/auth.svelte.ts` | Read the single record; remove `resolveSeededOwner` display-link (R2.4). |
| `scripts/migrate_identity_merge.py` (new) | The one-off merge (R3). |

## 5. Risks
- **Live-data migration** — mitigated by reversible-by-reseed (R3.3), verify-before-after, and running against a backup/export first.
- **Hook behavior differs from client assumptions** — mitigated by V1/V2 behavioral verification on Kiro IDE with a real sign-in.
- **An empty-handle seeded owner (Arun Elambaram)** — stays pending (owns projects, cannot sign in until a handle is set); uniqueness skips null (R1.1). Explicitly in-scope-aware, not broken.

## 6. Executor
**Kiro IDE** (escalated): identity + live migration, needs real sign-in behavioral verification and a careful migration run. Not Antigravity's cost-first lane.
