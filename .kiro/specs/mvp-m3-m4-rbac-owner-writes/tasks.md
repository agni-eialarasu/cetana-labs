# MVP M3–M4 — Minimum RBAC + Owner Write Path — Tasks

> Ordered plan for `/spec-run` (Build). Execute on **Kiro IDE**. Do NOT merge; open a PR, emit the Human Verification Plan, STOP in `IN_VERIFICATION`.

## Execution header (self-describing — read by `/spec-run`)

| Field | Value |
| :--- | :--- |
| **Spec id** | `mvp-m3-m4-rbac-owner-writes` |
| **Kickoff (IDE one-liner)** | `/spec-run mvp-m3-m4-rbac-owner-writes` |
| **Surface** | Kiro **IDE** (stack + provisioning + UI + rule tests) |
| **Branch to create** | `feat/mvp-m3-m4-rbac-owner-writes` (off up-to-date `main`, per `RFC-LAB-000-004`) |
| **Base for PR** | `main` |
| **Preflight** | Requirements §0 (P1–P6, incl. M2 auth working) + task **T0** — STOP on any ❌ |
| **Self-validation target** | `requirements.md` EARS R1–R8 |
| **Human Verification Plan** | `requirements.md` §4b (V1–V8; V3 = the RBAC security check) |
| **On completion** | Open PR via `gh api`, emit the Verification Plan, STOP → `/verification-done` → `/review-pr` (never merge) |
| **Executor role** | Delegated-agent / onboarded-dev |

---

- [ ] **T0 — Preflight (gate — STOP on any ❌)**
  - Surface=IDE (`/env-doctor`); clean tree; branch off fresh `main`; this Spec on `main` (merge-first).
  - Baseline green (P5): three validators + `pnpm check`/`build`.
  - **P6:** M2 GitHub OAuth works locally; a signed-in owner links to a seeded `users` record (needed for owner-write tests).
  - _Refs: §0._

- [ ] **T1 — Add the editable status field(s) to `projects` (`pb_provision.py`)**
  - Add `status_health` (select = the STATUS.md health legend) + `status_note` (text), `required=False`; optional `status_updated_at` (OQ-1). Idempotent upsert (in-place field update).
  - Re-run `make provision`; confirm the fields exist and the owner `updateRule` covers them.
  - _Refs: R2.1, R2.2, design §3._

- [ ] **T2 — Seed the new field(s) (`pb_import.py`)**
  - Populate `status_health` from `data/status.json` health where resolvable, else empty; keep seed idempotent.
  - _Refs: R2.3._

- [ ] **T3 — Verify the RBAC rule matrix (M3, tests — not just declared)**
  - Confirm `projects` rules = §4 matrix. Exercise: owner update succeeds; **non-owner update → 403**; anon write → denied; public read → ok. Capture how (SDK/curl) for the Verification Log.
  - _Refs: R1.1, R1.2, R1.3, R5, design §2._

- [ ] **T4 — Read the status field in `data.ts` (R4)**
  - Map `projects.status_*` from PB into the project record; **retain the PB record `id`** for owned-record updates. **Keep** the `status.json` merge + snapshot fallback (no M1 regression).
  - _Refs: R4.1, R6.1, design §4._

- [ ] **T5 — Owner-only edit control + write (M4, R3)**
  - Compute `isOwner` (linked handle === project owner). Show an owner-only edit control (health select + note) — OQ-2 surface. On submit: `pb.collection('projects').update(pbId, {...})`; on success refetch/optimistic so the new value shows (R3.4).
  - Non-owner/anon: no control (UX) — enforcement is the rule (T3).
  - _Refs: R3.1–R3.4, R5.2, design §5._

- [ ] **T6 — Regression + superuser checks**
  - M1 public read + `status.json` legacy status intact; M2 sign-in/guard intact; PB superuser can still edit any project.
  - _Refs: R6, R7._

- [ ] **T7 — Quality gates green**
  - `pnpm --dir app/web check && build && lint`; `make validate-local`.
  - _Refs: R8._

- [ ] **T8 — Commit, open PR, emit Human Verification Plan, STOP**
  - Branch `feat/mvp-m3-m4-rbac-owner-writes`; semantic commit referencing `TSK-050` / `BK-011` M3–M4.
  - Open PR into `main` via `gh api`; CI green; emit §4b plan (V1–V8, **V3 = security check**); STOP in `IN_VERIFICATION`. **Never merge.**
  - _Refs: R-all, `RFC-LAB-000-009` §3.2._

- [ ] **T9 — After human verification passes: `/verification-done`**
  - Human runs V1–V8 (esp. V3 non-owner 403); fixes ride the same PR; on pass, `/verification-done` writes the Verification Log to this Spec'"'"'s `REPORT.md` → `IN_REVIEW` → `/review-pr`.
  - _Refs: `RFC-LAB-000-009` §3.2._

---

### Governance lockstep reminder (Record, after merge)
Note M3–M4 in CHANGELOG (`TSK-050`). **This completes the MVP'"'"'s local auth loop** — logged-in owner edits own status, non-owner denied by rule. Only **M5 (deploy, `RFC-LAB-000-011`/`TSK-054`)** remains for the full MVP. The two-source status reality (PB `status_*` vs `status.json`) is documented dual-track; reconciliation is post-MVP.
