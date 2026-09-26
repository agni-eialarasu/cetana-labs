---
name: sprint-start
description: >-
  Opens the SPRINT CONTAINER in Cetana Labs (RFC-LAB-000-009 Phase 1 Scope, Kiro Web) — creates the Current Sprint block in BACKLOG.md (next SPRINT-XX id, 2-week window, goal, planned items incl. carried-forward tasks) and syncs STATUS.md focus. A sprint CONTAINS MANY plans: within it you run /plan-start -> /plan-done per feature (each producing one merged Spec). Pairs with /sprint-done. Use when the user runs /sprint-start or asks to start/plan a new sprint.
---

# Skill: Sprint Kickoff (`/sprint-start`)

## Objective
Open the **sprint container** — the top-level Scope artifact of the lifecycle (`RFC-LAB-000-009` §3.1). It initializes the Current Sprint block in `BACKLOG.md` (id, window, goal, planned items) and is the counterpart to `/sprint-done`. Normally `/sprint-done` already seeds the next sprint block; use `/sprint-start` to open one from scratch, refine the goal, or (re)plan the item list. Runs on **Kiro Web** (plan) — no code.

### Lifecycle position (sprint ⊃ plans ⊃ Spec — decided: option a)
```
/sprint-start  ── opens the SPRINT container (SPRINT-XX, 2-week window, goal)   [once per sprint]
   └── /plan-start … /plan-done   ── a planning session per feature            [many per sprint]
          └── output: a MERGED Spec (.kiro/specs/<id>/)
                 └── /spec-run <id>  →  /review-pr <PR>  →  /sprint-done
```
`/sprint-start` opens the **container**; the per-feature brainstorming that fills it happens in `/plan-start` → `/plan-done` sessions. Don't author individual Specs here — that's `/plan-start`.

## Trigger Patterns
- `/sprint-start`
- `/sprint-start <goal>` (trailing text = the sprint goal / theme)
- "start a new sprint", "plan the next sprint"

## Steps

### 0. State guard (phase-aware — `RFC-LAB-000-009` state machine)
- **No active sprint (or the prior one is closed) ⇒ proceed** to open a new container.
- **A sprint is already active (redundant) ⇒ skip + continue:** report "SPRINT-XX is already active" and offer to *refine the goal / (re)plan items* instead of opening a duplicate. Do not create a second Current Sprint block. *(Redundant ⇒ skip.)*
- **The prior sprint has unclosed, delivered work ⇒ ALERT:** suggest `/sprint-done` to close it first so carry-forwards compute correctly. *(Missing prerequisite ⇒ alert, don't silently overwrite.)*

### 1. Determine the next sprint
1. Read `BACKLOG.md`. Find the highest `SPRINT-XX` (in Current or the Delivered Archive).
2. Next id = increment (e.g. `SPRINT-07` → `SPRINT-08`), zero-padded.
3. Window = 2 weeks from the prior sprint's end date (or today if none).

### 2. Compose the Current Sprint block
Write/replace the **Current Sprint** section with:
```markdown
## 🎯 Current Sprint: Sprint XX — <Theme>

| Property | Value |
| :--- | :--- |
| **Sprint ID** | `SPRINT-XX` |
| **Duration** | YYYY-MM-DD to YYYY-MM-DD (2 Weeks) |
| **Sprint Goal** | <goal> |
| **Status** | 🟢 Active |
| **Lead** | Eialarasu |

### Planned Sprint Items
| Task ID | Item / Feature | Priority | Assignee | Status | Target Date |
| :---: | :--- | :---: | :---: | :---: | :---: |
| `TSK-0XX` | ... | P? | Eialarasu | 📋 Planned | YYYY-MM-DD |
```
- **Carry forward** any `📋 Planned` / `🚧 In Progress` items not delivered in the prior sprint.
- Assign new `TSK-0XX` ids continuing the global sequence (no gaps, no duplicates — check the whole file).

### 3. Sync focus
- Update `### 3. Current Focus & Next Milestone` in root `STATUS.md` and `projects/LAB-000-cetana-labs/STATUS.md` to the new sprint goal (keep ≤ 35 lines; keep the two files identical).

### 4. Validate & commit
- Run `/validate-local` (at minimum `validate_portfolio.py` + `project_validate.py --allow-dirty`).
- Governance/docs change → may fast-path to `main` per `RFC-LAB-000-004`; commit `feat(governance): start <SPRINT-XX> — <theme>`.

### 5. Hand off to per-feature planning
- After the container is open, remind the user of the flow within it: brainstorm each feature via **`/plan-start`** (optional/implicit — any free-form topic counts) → **`/plan-done`** (merges its Spec to `main`) → **`/spec-run <spec-id>`** (IDE) → **`/review-pr`** → **`/sprint-done`** (close the container).

## Notes
- **Container vs. plan:** `/sprint-start` opens the sprint; individual feature Specs are authored in `/plan-start` sessions, not here. Keep the boundary (mirrors the `/env-doctor` vs `/validate` discipline — Decision Journal D8).
- Guard against duplicate `TSK` ids (a past defect) — scan `BACKLOG.md` for the id before assigning.
- Keep `BACKLOG.md` and `CHANGELOG.md` in lockstep (Pillar 2).
- **Web/plan only** — no code, no feature branch (that's `/spec-run` on the IDE).
