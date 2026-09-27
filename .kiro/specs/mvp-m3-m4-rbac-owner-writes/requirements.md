# MVP M3–M4 — Minimum RBAC + Owner Write Path — Requirements

| Property | Value |
| :--- | :--- |
| **Spec ID** | `mvp-m3-m4-rbac-owner-writes` |
| **Feature** | MVP Phases M3 (minimum RBAC) + M4 (owner edits own project status) — `RFC-LAB-000-008` §6 |
| **Backlog** | `TSK-050` (SPRINT-09), epic `BK-011` |
| **Status** | 🟡 Proposed (contract authored on Kiro Web; execution on Kiro IDE) |
| **RFCs** | `RFC-LAB-000-008` (MVP §4 minimum RBAC, §6 M3/M4, §9.1 status storage), `RFC-LAB-000-006` (auth/RBAC), `RFC-LAB-000-003` (PocketBase) |
| **Executor role** | Delegated-agent / onboarded-dev (full Spec) |

---

## 1. Introduction

M1 wired the UI to live PocketBase (read); M2 added GitHub OAuth sign-in. **M3–M4 completes the MVP'"'"'s auth loop:** enforce **minimum RBAC** (public read / authenticated / owner-writes-own) via **PocketBase API rules**, and give an **owner an in-app write path to edit their own project'"'"'s status**, persisting to PocketBase.

**Decisions of record (settled at planning):**
- **RBAC engine = PocketBase per-collection API rules — NO RBAC library** (`RFC-LAB-000-003/006/008`). Enforcement is server-side rules; any UI show/hide is UX only, never the security boundary.
- **Minimum RBAC = 3 tiers** (public / authenticated / owner-via-`owner_id`). The full 5-role `memberships` model is **deferred** (`RFC-LAB-000-008` §4).
- **Status storage (§9.1) = a minimal status field on `projects`** (option a). The owner edits it via the **existing** `updateRule`; the UI **reads it back** so the edit is visible. The `status.json` → executive-broadcast cadence is **untouched for MVP** (dual-run, §9.4); reconciling the two status sources is **post-MVP**.

## 0. Preconditions (preflight — verify BEFORE any change; enforced by `tasks.md` T0)

- **P1 — Surface:** Kiro **IDE / local** (runs stack, edits provisioning + UI). `/env-doctor` IDE-ready.
- **P2 — Toolchain:** Node 22 + pnpm ~10.27; Python 3.11+; `pocketbase` binary + JS SDK.
- **P3 — Branch:** `feat/mvp-m3-m4-rbac-owner-writes` off up-to-date `main`; clean tree; not `main`/`master`.
- **P4 — Merge-first:** this Spec merged to `main` before `/spec-run`.
- **P5 — Baseline green:** three validators + `pnpm --dir app/web check && build` pass before changes.
- **P6 — Auth works (M2):** GitHub OAuth sign-in functions locally (M2 merged); a signed-in owner identity links to a seeded `users` record by `github_handle` (needed to test owner-writes-own).

## 2. Current-state facts (of record — verified against the repo)

- **`projects` rules today** (`pb_provision.py`): `listRule`/`viewRule` = `""` (public, M1); `createRule`/`deleteRule` = superuser-only; **`updateRule` already = `@request.auth.id != "" && owner = @request.auth.id`** (the owner-write rule — provisioned, not yet exercised).
- **No status field on `projects`** — the collection has structural fields only; **status lives in `status.json`** (snapshot, read by `data.ts`). M4 adds an editable status field.
- **UI:** `data.ts` reads structural data from PB + merges `status.json` status; M2 added the `auth` store (`isAuthenticated`, `user` linked by `github_handle`) and the `(member)` route guard.
- **Owner resolution:** the UI already knows a project'"'"'s `owner` (via `owner_id`/`github_handle`); comparing to the signed-in user determines "is this my project."

## 3. Requirements (EARS acceptance criteria = Definition of Done)

### R1 — Minimum RBAC rule matrix (verify + complete; PocketBase rules)
- **R1.1** The `projects` API rules SHALL enforce the §4 matrix: `list`/`view` public (summary tier), `update` owner-only (`@request.auth.id != "" && owner = @request.auth.id`), `create`/`delete` superuser-only.
- **R1.2** The rule matrix SHALL be **verified by test**, not just declared: an owner can update their own project; a non-owner (authenticated) is denied; an anonymous user is denied write; everyone can read the public summary.
- **R1.3** `memberships`-based multi-role writes SHALL NOT be implemented (deferred — `RFC-LAB-000-008` §4).

### R2 — Editable status field on `projects` (§9.1 option a)
- **R2.1** The `projects` collection SHALL gain minimal, owner-editable status field(s) — at least `status_health` (select: the health legend) and `status_note` (text); provisioned idempotently in `pb_provision.py`.
- **R2.2** These fields SHALL be covered by the existing owner `updateRule` (no new rule needed) and SHALL NOT be writable by non-owners (enforced by R1).
- **R2.3** Seeding (`pb_import.py`) SHALL populate the new field(s) from existing data where available (or leave sensibly empty); re-provision/seed stays idempotent.

### R3 — Owner write path in the UI (M4)
- **R3.1** WHEN a signed-in user views a project they own, the UI SHALL present an **edit control** for the status field(s).
- **R3.2** WHEN the owner submits an edit, the system SHALL persist it via the PocketBase SDK (`pb.collection('projects').update(id, {...})`) — succeeding because the owner `updateRule` permits it.
- **R3.3** WHEN a non-owner (or anonymous) views a project, the edit control SHALL NOT be shown (UX), AND a direct write attempt SHALL be denied by the rule (security) — the two layers are distinct (R5).
- **R3.4** WHEN an edit persists, the UI SHALL reflect the new value (optimistic update or refetch) by **reading the PB status field back** — so the change is visible without a full reload.

### R4 — Read the editable status field (so edits are visible)
- **R4.1** `data.ts` SHALL read the new `projects.status_*` field(s) from PocketBase and surface them to the UI for the owner-edit view. *(The `status.json` merge for the executive/legacy status remains for MVP — R6; do not remove it.)*

### R5 — Enforcement vs. UX separation (explicit)
- **R5.1** Security enforcement SHALL be the PocketBase `updateRule` (server-side) — the authoritative boundary.
- **R5.2** The UI edit control visibility SHALL be **UX convenience only**; hiding it SHALL NOT be relied on for security. A test SHALL confirm a non-owner write is rule-denied even if the control were forced.

### R6 — No regression to M1/M2
- **R6.1** The public dashboard read path (M1: live PB + `status.json` merge + snapshot fallback) SHALL remain intact; the `status.json` executive-broadcast cadence SHALL be untouched (dual-run, `RFC-LAB-000-008` §9.4).
- **R6.2** M2 sign-in/out, link-by-handle, and the route guard SHALL remain functional.

### R7 — Superuser escape hatch preserved
- **R7.1** The PocketBase superuser retains full access (create/delete/update any) — `RFC-LAB-000-006` §5.

### R8 — Quality gates green
- **R8.1** `pnpm --dir app/web check && build && lint` and `make validate-local` SHALL pass.

## 4b. Human Verification Plan (emitted by `/spec-run`; recorded by `/verification-done`)

Run locally, signed in as a seeded **owner** (linked by `github_handle`):
- **V1 — Owner edits own status:** open a project you own → edit control visible → change `status_health`/`status_note` → save → **persists** and the UI shows the new value.
- **V2 — Persisted to PB:** verify in the PB admin UI (or refetch) that `projects.status_*` changed.
- **V3 — Non-owner denied (rule):** signed in as a user who does NOT own project X, attempt an update (via console/SDK) → **rule-denied** (403). *(The security bar — not just a hidden button.)*
- **V4 — Non-owner sees no edit control (UX):** viewing a project you don'"'"'t own shows no edit affordance.
- **V5 — Anonymous denied:** signed out → no edit control; a write attempt is denied.
- **V6 — Public read intact:** anonymous dashboard still renders (M1 parity); `status.json`-sourced legacy status still displays.
- **V7 — Superuser:** PB admin can still edit any project.
- **V8 — Gates:** `pnpm check`/`build`/`lint` + `make validate-local` green.

**Verdict rule:** V1–V8 pass (fixes on the same PR, re-verified) before `/verification-done`. Note V3 is the RBAC security check and MUST be exercised, not assumed.

## 5. Out of Scope (deferred)
- The full 5-role `memberships` model / per-project multi-role writes (`RFC-LAB-000-008` §4; future `BK-007`/`BK-014`).
- `status_snapshots` history collection + migrating `status.json` into PB (post-MVP; §9.1 option b not chosen).
- Reconciling the two status sources (PB `status_*` vs `status.json` broadcast) — MVP runs them dual-track; reconciliation is post-MVP.
- Audit trail (`RFC-LAB-000-006` §6); create/delete of projects in-app (owner edits existing status only — `RFC-LAB-000-008` §4).
- Deploy (M5 / `RFC-LAB-000-011`).

## 6. Open Questions (resolve at build start)
1. **Status field shape:** `status_health` (select, health legend) + `status_note` (text) only, or also `status_updated_at`? *(Leaning: health + note + an auto `status_updated_at` if trivial; keep minimal.)*
2. **Edit UX surface:** inline on the project card vs. the `(member)` account/detail view. *(Leaning: an owner-only inline edit on the card, or a simple member detail view — decide at build for the cleanest UX with the existing components.)*
3. **Optimistic vs refetch (R3.4):** optimistic update vs. re-fetch after save. *(Leaning: refetch the single record for correctness; optimistic only if trivial.)*
