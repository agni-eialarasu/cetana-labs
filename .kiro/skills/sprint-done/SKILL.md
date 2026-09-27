---
name: sprint-done
description: >-
  Closes out an active sprint in Cetana Labs: archives completed tasks in SPRINT_TRACKER.md, bumps version in CHANGELOG.md, synchronizes STATUS.md wins, logs milestone in journal.md, and commits to main (e.g. "/sprint-done", "/sprint-done SPRINT-02").
---

# Skill: Sprint Closeout Protocol (`/sprint-done`)

## Objective
Execute a zero-friction, automated sprint closeout for Cetana Labs (`LAB-000`). Moves completed items into the archive, updates the historical CHANGELOG, synchronizes authoritative status, and pushes directly to `main`.

---

## 1. Trigger Patterns
Activate this skill whenever the user invokes:
- `/sprint-done`
- `/sprint-done <sprint_id>` (e.g. `/sprint-done SPRINT-02`)
- *"Close out the current sprint"*
- *"Wrap up sprint and bump changelog"*

---

## 2. Step-by-Step Execution Procedure

### Step 0: State guard (phase-aware — `RFC-LAB-000-009` state machine)
`/sprint-done` is the **Record / done** phase — it closes a sprint whose work has been **verified and merged**. Before archiving, confirm the lifecycle state:
- **Any Spec work still IN_REVIEW (open, unmerged PR for a sprint item) ⇒ ALERT + HOLD:** "PR #NN for `<spec/task>` is still open — closing the sprint now would record undelivered work. Merge via `/review-pr` first, or confirm you're intentionally deferring it (carry-forward)." *(A missing gate — the PR hasn't passed review/merge — is a HOLD, never a silent skip.)*
- **Items marked `✅ Done` with merged PRs ⇒ proceed.**
- **No active sprint / already closed (redundant) ⇒ skip + continue:** report "no open sprint to close" rather than fabricating a closeout. *(Redundant ⇒ skip.)*
- Never mark a sprint `DELIVERED` for work that isn't merged to `main` — the human gate (`/review-pr`) is upstream of this step.

### Step 1: Inspect `SPRINT_TRACKER.md`
1. Read the **Current Sprint** section in `SPRINT_TRACKER.md` (the sprint tracker — sprint state lives here, not in `BACKLOG.md`, per `RFC-LAB-000-010`).
2. Identify all tasks marked `✅ Done`.
3. Identify any unfinished or carried-over tasks (`🔨 In Progress`, `🔍 In Verification`, `👀 In Review`, or `📋 Backlog`).

### Step 2: Archive Sprint in `SPRINT_TRACKER.md`
1. Move the finished sprint into the **Delivered Sprints Archive** section of `SPRINT_TRACKER.md`.
2. Initialize the **Next Sprint** block (e.g. increment `SPRINT-02` $\rightarrow$ `SPRINT-03` with the next 14-day date window).
3. Carry forward any remaining incomplete tasks into the new sprint.

### Step 3: Bump `CHANGELOG.md`
1. Determine the next semantic version (e.g. `v0.3.0` $\rightarrow$ `v0.4.0` for new features or `v0.3.1` for maintenance).
2. Move items from `[Unreleased]` into the new release header: `## [vX.Y.Z] - YYYY-MM-DD`.
3. Reset `[Unreleased]` with empty categories (`Added`, `Changed`, `Fixed`).

### Step 4: Synchronize `STATUS.md` (`LAB-000`)
1. Edit `projects/LAB-000-cetana-labs/STATUS.md` and copy to root `STATUS.md`.
2. Update `**Last Updated**` to today's date (`YYYY-MM-DD`).
3. Update `### 2. Latest Deliveries & Business Wins` highlighting the major achievements of the closed sprint.
4. Update `### 3. Current Focus & Next Milestone` with the newly planned sprint goals.

### Step 5: Append Milestone to `journal.md`
Append a reverse-chronological entry to `projects/LAB-000-cetana-labs/journal.md`:
```markdown
### [YYYY-MM-DD] Milestone: Sprint XX Closeout & vX.Y.Z Release
- **Delivered Capabilities**: [Summary of completed tasks]
- **Next Horizon**: [Goals for upcoming sprint]
```

### Step 6: Validate Integrity & Commit
```bash
python3 scripts/validate_portfolio.py
git add .
git commit -m "feat(governance): closeout <sprint_id> and release v<version>"
git push origin main
```

### Step 7: Present Preview
Run `python3 scripts/generate_status.py LAB-000` and display the updated executive briefing to the user.
