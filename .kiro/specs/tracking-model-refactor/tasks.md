# Tracking-Model Refactor — Tasks

> Ordered plan for `/spec-run` (Build). Execute on **Kiro IDE**. Do NOT merge; open a PR, emit the Human Verification Plan, STOP in `IN_VERIFICATION`.

## Execution header (self-describing — read by `/spec-run`)

| Field | Value |
| :--- | :--- |
| **Spec id** | `tracking-model-refactor` |
| **Kickoff (IDE one-liner)** | `/spec-run tracking-model-refactor` |
| **Surface** | Kiro **IDE** (edits repo files + runs Python validators) |
| **Branch to create** | `feat/tracking-model-refactor` (off up-to-date `main`, per `RFC-LAB-000-004`) |
| **Base for PR** | `main` |
| **Preflight** | Requirements §0 (P1–P5) + task **T0** — STOP on any ❌ |
| **Self-validation target** | `requirements.md` EARS R1–R8 |
| **Human Verification Plan** | `requirements.md` §4b (V1–V6) |
| **On completion** | Open PR via `gh api`, emit the Verification Plan, STOP → `/verification-done` → `/review-pr` (never merge) |
| **Executor role** | Delegated-agent / onboarded-dev |

---

- [ ] **T0 — Preflight (gate — STOP on any ❌)**
  - Surface = IDE (`/env-doctor`); clean tree; branch `feat/tracking-model-refactor` off fresh `main`; RFC-010 + this Spec on `main` (merge-first).
  - **Baseline green** (P5): run `validate_portfolio.py`, `generate_status_json.py --check`, `project_validate.py --allow-dirty` — all pass *before* changes.
  - Snapshot the pre-refactor id set: extract `SPRINT-`/`TSK-`/`BK-` ids from `BACKLOG.md` (for the T7 audit).
  - _Refs: §0, design §7._

- [ ] **T1 — Create `SPRINT_TRACKER.md`**
  - Move the **Current Sprint** block + **Delivered Sprints Archive** out of `BACKLOG.md` into a new root `SPRINT_TRACKER.md`, verbatim. Add header (title, pointers to BACKLOG/CHANGELOG, RFC-010 link, status legend + Definition-of-Ready note).
  - _Refs: R1.1, R1.2, R4.1, design §2._

- [ ] **T2 — Trim `BACKLOG.md` to the idea bucket**
  - Remove the moved sections; keep intro + Prioritized Backlog only; add a top pointer to `SPRINT_TRACKER.md`; cite RFC-010.
  - _Refs: R2.1, R2.2._

- [ ] **T3 — Remap status vocabulary in the tracker**
  - Apply the §3 vocabulary; re-map SPRINT-09 rows (TSK-051 → `🔨 In Progress`; others → `📋 Backlog`) per design §3 / OQ-2.
  - _Refs: R3.1, R3.2._

- [ ] **T4 — Update `/sprint-start` + `/sprint-done` skills (targets only, behavior unchanged)**
  - Retarget both skills to `SPRINT_TRACKER.md` for sprint state (read highest SPRINT id, write/inspect/archive Current Sprint); TSK-id-uniqueness scan spans both files; lockstep note → tracker+changelog; keep `BACKLOG.md` as the `BK-` idea source.
  - _Refs: R5.1, R5.2, R5.3, design §4._

- [ ] **T5 — Update `project_validate.py` sprint-sync check**
  - Read the Delivered-Archive markers from `SPRINT_TRACKER.md` (not `BACKLOG.md`); keep the `docs/sprints/` → root fallback; ensure it passes for a real reason.
  - _Refs: R7.1, design §5._

- [ ] **T6 — Update references (docs/config)**
  - `AGENTS.md` §1.1/§1.5/§1.6/§4; `docs/sprint-lifecycle.md`; `docs/work-environment.md`; `README.md`; `.github/pull_request_template.md`.
  - Grep for lingering "Current Sprint"/"Delivered Sprints" strings pointing at `BACKLOG.md`.
  - _Refs: R6.1, R6.2, design §6/§7.3._

- [ ] **T7 — Verify: id audit + validators**
  - Confirm post-refactor (`SPRINT_TRACKER.md` ∪ `BACKLOG.md`) contains every pre-refactor id (no loss/dupe).
  - Run all three validators green; confirm the sync check reads the tracker.
  - _Refs: R7.2, R8.1, R8.2, design §7._

- [ ] **T8 — Commit, open PR, emit Human Verification Plan, STOP**
  - Branch `feat/tracking-model-refactor`; semantic commit referencing `TSK-051`/`RFC-LAB-000-010`.
  - Open PR into `main` via `gh api`; ensure CI green; emit the §4b plan (V1–V6); STOP in `IN_VERIFICATION`. **Never merge.**
  - _Refs: R-all, `RFC-LAB-000-009` §3.2._

- [ ] **T9 — After human verification passes: `/verification-done`**
  - The human runs V1–V6; fixes ride the same PR (Single-PR rule); on pass, `/verification-done` writes the Verification Log to this Spec's `REPORT.md` → `IN_REVIEW` → `/review-pr`.
  - _Refs: `RFC-LAB-000-009` §3.2._

---

### Governance lockstep reminder (Record, after merge)
This refactor *is* governance plumbing — after merge, ensure CHANGELOG notes the tracking-model implementation (`TSK-051`), and the new `SPRINT_TRACKER.md` is the live sprint artifact going forward. `/sprint-done` for SPRINT-09 will then operate on the new file.
