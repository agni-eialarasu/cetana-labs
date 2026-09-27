# Tracking-Model Refactor — Requirements

| Property | Value |
| :--- | :--- |
| **Spec ID** | `tracking-model-refactor` |
| **Feature** | Implement `RFC-LAB-000-010` — split `SPRINT_TRACKER.md` from `BACKLOG.md`; align status vocab to the state machine; wire the skills/validators |
| **Backlog** | `TSK-051` (SPRINT-09) |
| **Status** | 🟡 Proposed (contract authored on Kiro Web; execution on Kiro IDE) |
| **RFCs** | `RFC-LAB-000-010` (tracking model — decision of record), `RFC-LAB-000-009` (state machine / lifecycle), `RFC-LAB-000-004` (branching) |
| **Executor role** | Delegated-agent / onboarded-dev (full Spec — `RFC-LAB-000-009` §5) |

---

## 1. Introduction

`RFC-LAB-000-010` decided the three-tier tracking funnel. This Spec is its **mechanical implementation**: physically split the artifacts, align the status vocabulary to the lifecycle state machine, add the Definition-of-Ready framing, and update every skill / validator / doc that references the current single-file layout — with **no loss of history** and **validators staying green**.

This refactor is deliberately **dogfooded through the AIDLC lifecycle** (it is itself a `/spec-run` unit of work), so the tracking blueprint is proven on its own repo.

**Scope of this Spec:** file/section moves + reference updates + status-vocab remap. **Not** a behavior change to the lifecycle commands (only their *file targets* change).

## 0. Preconditions (preflight — verify BEFORE any change; enforced by `tasks.md` T0)

- **P1 — Surface:** Kiro **IDE / local** (this refactor edits repo files + runs Python validators locally). `/env-doctor` reports IDE-ready.
- **P2 — Toolchain:** Python 3.11+ (validators); git.
- **P3 — Branch:** feature branch `feat/tracking-model-refactor` off an up-to-date `main`; clean tree; not `main`/`master`.
- **P4 — Merge-first:** `RFC-LAB-000-010` is merged to `main` (it is — the decision of record). This Spec is itself merged to `main` before `/spec-run` (per merge-first).
- **P5 — Baseline green:** `python3 scripts/validate_portfolio.py`, `python3 scripts/generate_status_json.py --check`, and `python3 scripts/project_validate.py --allow-dirty` all pass *before* changes (so any post-change failure is attributable to this work).

## 2. Current-state facts (of record — verified against the repo)

- **`BACKLOG.md`** currently contains three things: the **Current Sprint** block, the **Prioritized Backlog** (idea bucket), and the **Delivered Sprints Archive**.
- **Skills that read/write it:** `/sprint-start` (reads highest SPRINT id; writes Current Sprint block; scans for duplicate TSK ids; keeps BACKLOG/CHANGELOG lockstep) and `/sprint-done` (inspects Current Sprint; archives to Delivered; carries forward). `/plan-*`, `/spec-run`, `/review-pr` reference backlog rows/ids but do not parse structure.
- **`scripts/project_validate.py`** already **supports `SPRINT_TRACKER.md`** — it checks `docs/sprints/SPRINT_TRACKER.md`, falls back to root `SPRINT_TRACKER.md`, and its sync check looks for `Delivered Sprints Archive|Delivered Tasks|### Sprint N` markers **in `BACKLOG.md`** (this marker location moves to the tracker — see R5).
- **Docs referencing the layout:** `AGENTS.md` §1.1/§1.5/§1.6, `docs/work-environment.md` (Sprint row), `docs/sprint-lifecycle.md` (verb map / merge-first), `README.md`, `.github/pull_request_template.md`.
- **No CI workflow parses `BACKLOG.md` structurally** (only `project_validate.py` inspects it; the status generators read `STATUS.md`, not the backlog).

## 3. Requirements (EARS acceptance criteria = Definition of Done)

### R1 — Create `SPRINT_TRACKER.md` (root)
- **R1.1** The system SHALL create a root `SPRINT_TRACKER.md` containing the **Current Sprint** block (id, window, goal, lead, item table) and the **Delivered Sprints Archive**, moved from `BACKLOG.md`.
- **R1.2** History SHALL be preserved — the moved content is the same content (no rewrite of delivered-archive entries).

### R2 — Trim `BACKLOG.md` to the idea bucket
- **R2.1** After the move, `BACKLOG.md` SHALL contain **only** the Prioritized Backlog (`BK-` initiatives) — no Current Sprint block, no Delivered Archive.
- **R2.2** `BACKLOG.md` SHALL open with a one-line pointer to `SPRINT_TRACKER.md` for active work and cite `RFC-LAB-000-010`.

### R3 — Status vocabulary = the state machine (`RFC-LAB-000-009` §3.1 / `RFC-LAB-000-010` §4)
- **R3.1** The `SPRINT_TRACKER.md` item-status column SHALL use the state-machine vocabulary: `✅ Ready` (`READY_TO_BUILD`), `🔨 In Progress`, `🔍 In Verification`, `👀 In Review`, `✅ Done` (`RECORDED`); `📋 Backlog` for pre-funnel ideas.
- **R3.2** Existing SPRINT-09 rows SHALL be re-mapped to this vocabulary (e.g. `📋 Planned` → `📋 Backlog`/`✅ Ready` per whether their Spec is merged).

### R4 — Definition of Ready documented in the tracker
- **R4.1** `SPRINT_TRACKER.md` SHALL state the backlog→sprint entry gate: an item is `✅ Ready` only when its Spec is merged to `main` (`READY_TO_BUILD`), per `RFC-LAB-000-010` §5.

### R5 — Update skills to the new file targets (behavior unchanged)
- **R5.1** `/sprint-start` SHALL read/write the **Current Sprint** block in `SPRINT_TRACKER.md` (not `BACKLOG.md`); it still reads `BACKLOG.md` for `BK-` ideas and TSK-id uniqueness across both files.
- **R5.2** `/sprint-done` SHALL inspect + archive the Current Sprint in `SPRINT_TRACKER.md`; CHANGELOG/STATUS/journal steps unchanged.
- **R5.3** Both skills' front-matter/descriptions and step text SHALL reference the correct files; the lockstep reminder becomes `SPRINT_TRACKER.md` + `CHANGELOG.md`.

### R6 — Update references across docs/config
- **R6.1** `AGENTS.md` (§1.1 artifacts list, §1.5 lockstep rule, §1.6 governance fast-path list, §4 verb map) SHALL reference `SPRINT_TRACKER.md` for sprint state and `BACKLOG.md` for ideas.
- **R6.2** `docs/work-environment.md`, `docs/sprint-lifecycle.md`, `README.md`, and `.github/pull_request_template.md` SHALL be updated to the split layout.

### R7 — Validator conformance
- **R7.1** `scripts/project_validate.py`'s sprint-sync check SHALL recognize the Delivered-Archive markers in **`SPRINT_TRACKER.md`** (their new home) — updated so the check still passes and isn't silently satisfied by the wrong file.
- **R7.2** WHEN the refactor is complete, `python3 scripts/validate_portfolio.py`, `generate_status_json.py --check`, and `project_validate.py --allow-dirty` SHALL all pass.

### R8 — No regressions / traceability intact
- **R8.1** The traceability chain (`RFC-LAB-000-010` §6) SHALL remain walkable: tracker rows cite `BK-`/`TSK-`/Spec; delivered archive keeps PR/tag references.
- **R8.2** No `TSK-`/`BK-`/`SPRINT-` id SHALL be lost or duplicated in the move (diff-verified).

## 4b. Human Verification Plan (emitted by `/spec-run`; recorded by `/verification-done`)

- **V1 — Split is clean:** `SPRINT_TRACKER.md` shows the Current Sprint + Delivered Archive; `BACKLOG.md` shows only the idea bucket; no content duplicated across the two.
- **V2 — No id loss:** every `SPRINT-`, `TSK-`, `BK-` id present before the move is present after (compare against pre-refactor `BACKLOG.md`).
- **V3 — Status vocab:** tracker rows use the state-machine vocabulary; SPRINT-09 rows re-mapped sensibly.
- **V4 — Skills point right:** read `/sprint-start` + `/sprint-done` — they target `SPRINT_TRACKER.md` for sprint state; a dry mental run doesn't reference the old location.
- **V5 — Validators green:** `validate_portfolio.py` ✅, `generate_status_json.py --check` ✅, `project_validate.py --allow-dirty` ✅ (and the sprint-sync check reads the tracker, not a stale backlog marker).
- **V6 — Docs coherent:** `AGENTS.md`, `sprint-lifecycle.md`, `work-environment.md`, `README`, PR template all describe the split.

**Verdict rule:** V1–V6 pass (fixes on the same PR, re-verified) before `/verification-done`.

## 5. Out of Scope (deferred)
- Changing lifecycle command *behavior* (only file targets change).
- A new validator pillar enforcing status-vocab/traceability (`RFC-LAB-000-010` OQ-3) — candidate follow-up, not this Spec.
- Moving the delivered archive into a separate `docs/sprints/` history (`RFC-LAB-000-010` OQ-2) — keep it in `SPRINT_TRACKER.md` for now.
- Multiple concurrent sprints (OQ-1).

## 6. Open Questions (resolve at build start)
1. **Tracker location:** root `SPRINT_TRACKER.md` (matches `project_validate.py` fallback) vs `docs/sprints/SPRINT_TRACKER.md` (its primary check). *(Leaning: root — simplest, and the validator already falls back to it; revisit if a `docs/sprints/` history emerges.)*
2. **SPRINT-09 status re-map:** which current `📋 Planned` rows become `✅ Ready` vs stay `📋 Backlog` — depends on whether each item's Spec is merged. *(Leaning: TSK-051's own Spec is merged → `✅ Ready`/`🔨 In Progress`; others stay `📋 Backlog` until their Spec lands.)*
