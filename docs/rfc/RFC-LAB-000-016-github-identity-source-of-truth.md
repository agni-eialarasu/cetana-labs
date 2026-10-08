[🏠 Repo](../../README.md) / [📚 Docs](../README.md) / RFC / **RFC-LAB-000-016**

# RFC-LAB-000-016: GitHub-Handle Identity & PocketBase as Source of Truth — Retiring the Dual-Source Model

| Property | Value |
| :--- | :--- |
| **Status** | Proposed |
| **Date** | 2026-10-08 |
| **Decision Journal** | D70 (Entry 025) |
| **Supersedes/Amends** | `RFC-LAB-000-002` (relational `data/` masters as source of truth), `RFC-LAB-000-008` (RBAC/identity), partially `RFC-LAB-000-010` (tracking funnel's project registry) |
| **Related** | `BK-014` (admin CRUD + `export_pb_to_data.py` reconciliation), `BK-030/031` (`is_admin` tier) |
| **Author** | KiroCrew Operator (Agni Eialarasu, Lead) |

---

## 1. Problem (the bug, made visible)

Signing into the deployed app as the GitHub account `@agni-eialarasu` produces **two `users` rows that are both the same human**:

| Row | id | github_handle | Role | Owns | Note |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Agni Eialarasu** | `o43801zyav6cwmd` | **Unlinked** | Contributor | None | the OAuth-minted auth record |
| **Eialarasu** | `usr-eialarasu` | `@agni-eialarasu` | Lead | LAB-000..003 | the seeded `data/users.json` record |

**Root cause (verified in `app/web/src/lib/auth.svelte.ts`):** PocketBase creates a **separate auth record per GitHub identity** on sign-in — it does NOT reuse a pre-seeded row. The frontend tries to *link* the OAuth record to a seeded owner by matching `github_handle` case-insensitively; when that match misfires (as here) the user is **authenticated-but-unlinked** and the two identities coexist. Project ownership lives on the *seeded* row; admin/auth lives on the *OAuth* row. They are the same person, split across two sources.

This is the **dual-source model** biting: identity (and the project registry) exist BOTH as committed `data/` masters AND as live PocketBase records, reconciled only by a fragile handle match. Two-way onboarding — seed `data/` *and* sign in via OAuth — is painful to maintain and to test.

## 2. Two decisions, deliberately separated

This RFC makes **Decision 1** firmly and **frames Decision 2** (gating its deletions behind open questions), so the urgent identity fix is not held hostage to the larger registry inversion.

---

## 3. Decision 1 — GitHub handle is the single user identity key (DECIDED)

**`github_handle` is the unique, authoritative key for a human.** There is exactly ONE `users` record per GitHub identity. We eliminate the seed-vs-OAuth duality.

### 3.1 Rules
- `users.github_handle` SHALL be **unique** (enforced at the collection level) and populated from the OAuth identity on first sign-in.
- On GitHub sign-in, the app SHALL **upsert by `github_handle`**: if a record with that handle exists (e.g. a seeded owner), the OAuth session binds to THAT record and enriches it (auth fields, `is_admin`) — it does NOT create a second row. No match ⇒ one new record is created, keyed by handle.
- Seeded "owner" rows that carry a `github_handle` become the **same** record the owner signs into — not a separate link target.
- A seeded owner with `github_handle: null` (e.g. **Arun Elambaram** today) is a **pending** identity: it owns projects but cannot sign in until a handle is set; first sign-in with a matching handle adopts it.

### 3.2 Migration for the existing duplicates
- **Merge** the OAuth row `o43801zyav6cwmd` INTO the seeded `usr-eialarasu` (keep the ownership of LAB-000..003; move `is_admin`/auth onto it; delete the orphan). Same for any future dup.
- This is a **data migration**, scripted and reversible-by-reseed, verified against the live DB — NOT a hand-edit.

### 3.3 Why this is urgent + low-risk
It fixes the visible bug, it is unambiguous, and it is confined to the identity path (auth store + a `users` uniqueness rule + a one-off merge). It does not require touching the registry/scraper spine.

---

## 4. Decision 2 — Retire `data/` masters + README registry + local project skills (FRAMED, gated)

**Direction (proposed):** PocketBase becomes the **source of truth** for projects AND users; `data/` masters stop being authored by hand and either die or become a pure *export artifact*; the README project-registry block and the local `project-*` skillset retire. This is the natural end-state of BK-014 (the app already does live CRUD + reconciliation).

### 4.1 Blast radius (verified 2026-10-08)
| Consumer of `data/` masters | Status under Decision 2 |
| :--- | :--- |
| `generate_registry.py` → README registry block | **Retire** the block (or regenerate from PB export) |
| `validate_portfolio.py` (**registry-lockstep pillar**) | Re-point at PB export, or drop the pillar |
| `generate_pb_schema.py` | Schema authored directly, not generated from `data/` |
| `generate_status_json.py` → `data/status.json` (web app) | Re-point at PB; `status.json` becomes an export |
| `app/web/src/lib/data.ts` (snapshot fallback) | Keep as an **export** snapshot, not a hand-authored master |
| `pb_import.py` / `export_pb_to_data.py` | Import retires; **export** stays (the reconciliation direction) |
| `project-*` skills (6), `projects/` folder, `templates/` | Retire the local project-management workflow |

### 4.2 Correction to an earlier assumption (important)
The **daily 9:30 IST WhatsApp scraper reads `STATUS.md` files, NOT `data/status.json`** (verified in `scripts/generate_status.py`). So **the executive broadcast is NOT blocked by retiring `data/` masters** — `data/status.json` feeds the *web app*, a separate consumer. This shrinks Decision 2's risk: the headline governance output (the broadcast) is `STATUS.md`-sourced and survives untouched.

### 4.3 Open questions that GATE the deletions (must be answered before anything is deleted)
- **OQ-1 — Registry CI pillar:** does the "registry lockstep" pillar re-point at a PB export (`export_pb_to_data.py` output committed), or retire? A control plane with no committed registry snapshot loses its at-rest GitHub view (the thing D68 just reframed).
- **OQ-2 — `data/` as export vs gone:** keep `data/*.json` as a **generated export** (committed via `just export-live-data`, so GitHub still shows the portfolio and `data.ts` fallback still works) — OR delete it entirely (app-only, no offline/at-rest view)? **Lean: keep as export** — cheap, preserves the reconciled-snapshot model (D68) and the app's fallback.
- **OQ-3 — `project-*` skills + `projects/` + `templates/`:** these encode the file-based project lifecycle. Retiring them means project creation/editing is **app-only**. Is that acceptable for the current workflow, or do some (e.g. `project-validate`, `audit-project`) stay because they guard structure the app doesn't? **Needs a per-skill call.**
- **OQ-4 — PB uniqueness/migration safety:** the project `owner` relation is required; a user merge must re-point owned projects atomically (D-CRUD-2's soft-delete guard applies).

### 4.4 Phasing (the deletions wait for OQ answers)
- **Phase 1 (after this RFC merges):** Decision 1 — identity Spec. Handle-unique rule + upsert-by-handle + the dup-merge migration. **Fixes the bug.** No registry change.
- **Phase 2:** Answer OQ-1..OQ-4 (a short design Spec / brainstorm). Decide export-vs-delete and the per-skill retirement list.
- **Phase 3:** Registry inversion Spec(s) — re-point consumers at PB export, retire the hand-authored masters + chosen skills, keeping `data/` as export per the OQ-2 lean.

## 5. Non-goals
- Not changing the daily broadcast's `STATUS.md` source (it stays).
- Not deleting anything in Phase 1.
- Not changing the AIDLC gate — every Phase ships via Spec → `/spec-run` → `/review-pr` → human merge.

## 6. Consequences
- **+** One identity per human; the two-rows bug cannot recur; onboarding is one-way (sign in with GitHub).
- **+** The control plane's live state and its at-rest view stop fighting (D68's reconciled-snapshot model becomes the only model, not a parallel one).
- **−** A data migration touches live records (Phase 1) — scripted, verified, reversible by reseed.
- **−** Retiring `project-*` skills removes a file-based workflow some muscle memory depends on — mitigated by keeping structure-guarding validators if OQ-3 says so.
