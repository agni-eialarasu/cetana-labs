---
name: project-update
description: >-
  Updates a project's executive status (STATUS.md), logs milestone journal entries, and synchronizes health badges using remote-first inspection or direct text (e.g. "/project-update LAB-003", "/project-update LAB-001 'Added 3D pose sync'").
---

# Skill: Update Project Status & Wins (`/project-update`)

## Objective
Record new deliveries, business wins, health changes, or blockers for a project in `STATUS.md` and `journal.md`, ensuring management updates are always up to date.

---

## 1. Trigger Patterns
Activate this skill whenever the user invokes:
- `/project-update <ID>` (e.g. `/project-update LAB-003`)
- `/project-update <ID> "<win description>"`
- `/project-update <ID> --health [on-track|at-risk|blocked|completed]`
- `/project-update <ID> --focus "<upcoming focus>"`
- *"Update status for LAB-XXX"*

---

## 2. Step-by-Step Procedure

### Step 1: Locate Target Project
- Validate that `projects/<ID>-<slug>/` exists.
- Read existing `projects/<ID>/STATUS.md` and `projects/<ID>/README.md`.

### Step 2: Remote-First Inspection (If No Text Given)
If no explicit win text was passed:
1. Extract the remote repository URL from `projects/<ID>/README.md`.
2. Inspect the latest 5 commits or recent pull requests on remote:
   ```bash
   gh repo view <org/repo> --json latestRelease
   # or check recent commits
   gh api repos/<org>/<repo>/commits?per_page=5 --jq '.[].commit.message'
   ```
3. Synthesize the top 1-2 business deliverables into plain-English executive wins.

### Step 3: Update `STATUS.md`
Edit `projects/<ID>/STATUS.md`:
1. Update `**Last Updated**` to today's date (`YYYY-MM-DD`).
2. If health was specified, update `**Current Health**`.
3. Prepend the new deliverable bullet under `### 2. Latest Deliveries & Business Wins` (retain top 3-4 most relevant wins).
4. Update `### 3. Current Focus & Next Milestone` if provided.
5. Update `### 4. Blockers & Risks` if provided.

### Step 4: Record Milestone in `journal.md`
Append a new milestone entry at the top of the Milestone Log in `projects/<ID>/journal.md`:
```markdown
### [YYYY-MM-DD] Milestone: [Win Summary]
- **Context**: [Details of capability delivered]
- **Impact**: [Business / operational outcome]
```

### Step 5: Sync Master `README.md`
If `Current Health` changed (e.g. from `🟢 On Track` to `🟡 At Risk`), update the health badge in the Master Table in root `README.md`.

### Step 6: Commit and Push
```bash
git add . && git commit -m "status(<id>): <summary of update>"
git push origin main
```

### Step 7: Output Preview
Run `python3 scripts/generate_status.py <ID>` and display the refreshed WhatsApp briefing to the user.
