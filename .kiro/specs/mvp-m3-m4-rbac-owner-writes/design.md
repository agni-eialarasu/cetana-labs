# MVP M3–M4 — Minimum RBAC + Owner Write Path — Design

> Companion to `requirements.md`. RBAC via PocketBase API rules (no library); a minimal owner-editable status field on `projects`; an owner-only write path in the SvelteKit UI. Enforcement is server-side rules; UI affordance is UX only.

---

## 1. Approach: activate rules + add one editable field + wire one write

M3 is mostly **verification** — the owner `updateRule` already exists (`pb_provision.py`). M4 is the net-new work: **add a status field** to `projects`, **read it** in `data.ts`, and **wire an owner-only edit** via the SDK. No RBAC library, no new rule engine — the datastore is the engine.

## 2. RBAC = PocketBase API rules (M3, R1/R5)

The `projects` rule matrix (mostly provisioned; verify + keep):
```
listRule   = ""                                                   # public summary (M1)
viewRule   = ""                                                   # public summary (M1)
createRule = null                                                 # superuser-only
updateRule = '@request.auth.id != "" && owner = @request.auth.id' # OWNER-ONLY (exists)
deleteRule = null                                                 # superuser-only
```
- **This IS the RBAC.** The rule runs server-side on every write; it is the authoritative boundary (R5.1). The new status fields are automatically covered by `updateRule` (R2.2) — no per-field rule needed at MVP.
- **Verification, not assumption (R1.2):** the Human Verification Plan V3 exercises a non-owner write and expects a 403 — proving the rule, not the hidden button.

## 3. Editable status field on `projects` (M4, R2)

Add to `projects_spec.fields` in `pb_provision.py` (idempotent upsert already updates fields in place — the M2 `upsert_collection` fix):
```python
f_select("status_health", HEALTH_VALUES, required=False),  # the health legend values
f_text("status_note"),                                     # short free text
# optional: an auto/updated timestamp if trivial (OQ-1)
```
- `HEALTH_VALUES` mirrors the STATUS.md health legend (`🟢 On Track`, `🟡 At Risk`, `🔴 Blocked`, `⏸️ Paused`, `✅ Completed`, `⏳ Onboarding Pending`) — reuse the existing legend, don'"'"'t invent new states.
- **Seeding (R2.3):** `pb_import.py` populates `status_health` from the current `data/status.json` health where resolvable, else leaves empty; re-seed stays idempotent.

## 4. Read the field (R4)

`data.ts` `loadFromPocketBase()` maps the new `status_*` fields into the project record it returns, so the UI can display/edit the PB-sourced status. **Keep the `status.json` merge** for the legacy/executive status (R6) — the two coexist for MVP:
- PB `status_*` = the owner-editable, in-app value (new).
- `status.json` = the executive-broadcast cadence (unchanged).
- Document the dual-track clearly in the UI/code comment so it'"'"'s not mistaken for a bug.

## 5. Owner write path in the UI (M4, R3)

- **Ownership check (UX):** `project.owner_id`/`github_handle` === `auth.user`'"'"'s linked handle → `isOwner`. Show the edit control only when `isOwner` (R3.3 UX layer).
- **Edit surface (OQ-2):** an owner-only inline edit (health select + note) on the project card, or a small `(member)` detail view. Lean: inline on the card for the owned project, using existing components.
- **Write (R3.2):** `pb.collection('projects').update(project.pbId, { status_health, status_note })` via the shared `pb` client (authenticated → the owner `updateRule` permits it). Needs the PocketBase **record id** (not `lab_id`) — ensure `loadFromPocketBase()` retains the PB `id` for owned-record updates.
- **Reflect (R3.4):** on success, refetch the single record (or optimistic-set) so the new value shows without reload.

## 6. Enforcement vs UX (R5 — the distinction that matters)

| Layer | Where | Purpose |
| :--- | :--- | :--- |
| **Enforcement** | PocketBase `updateRule` (server) | The security boundary — a non-owner write is 403 regardless of UI |
| **Affordance** | UI `isOwner` show/hide | Convenience only — never relied on for security |

V3 (non-owner write via SDK/console → 403) proves the enforcement layer independently of the UI.

## 7. Verification (feeds `tasks.md` + `/verification-done`)

Maps to V1–V8: owner edits + persists + visible; PB record changed; **non-owner rule-denied (403)**; non-owner/anon see no control; public read intact; superuser intact; gates green. V3 is the security-critical step.

## 8. Trade-offs

| Decision | Chosen | Rejected | Why |
| :--- | :--- | :--- | :--- |
| RBAC | PocketBase API rules | RBAC library (Casbin/oso) | Datastore already enforces; a library duplicates + splits source of truth (`RFC-LAB-000-003`). |
| Status storage | field on `projects` (§9.1a) | `status_snapshots` history (§9.1b) | Minimal for MVP; owner `updateRule` already covers it; history deferred. |
| Two status sources | dual-track (PB field + `status.json`) for MVP | migrate `status.json` → PB now | Keeps the broadcast cadence stable; reconciliation is post-MVP. |
| Roles | owner-via-`owner_id` only | 5-role `memberships` | Minimum RBAC (`RFC-LAB-000-008` §4); memberships stays in schema, unused. |
| Edit reflect | refetch single record | optimistic only | Correctness first; optimistic only if trivial. |
