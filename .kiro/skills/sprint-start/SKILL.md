---
name: sprint-start
description: >-
  Opens a new sprint in Cetana Labs — creates the Current Sprint block in BACKLOG.md (next SPRINT-XX id, 2-week window, goal, planned items incl. carried-forward tasks), and syncs STATUS.md focus. Pairs with /sprint-done. Use when the user runs /sprint-start or asks to start/plan a new sprint.
---

# Skill: Sprint Kickoff (`/sprint-start`)

## Objective
Initialize a new sprint cleanly in `BACKLOG.md` — the counterpart to `/sprint-done`. Normally `/sprint-done` already seeds the next sprint block; use `/sprint-start` to open a sprint from scratch, refine the goal, or (re)plan the item list.

## Trigger Patterns
- `/sprint-start`
- `/sprint-start <goal>` (trailing text = the sprint goal / theme)
- "start a new sprint", "plan the next sprint"

## Steps

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

## Notes
- Guard against duplicate `TSK` ids (a past defect) — scan `BACKLOG.md` for the id before assigning.
- Keep `BACKLOG.md` and `CHANGELOG.md` in lockstep (Pillar 2).
