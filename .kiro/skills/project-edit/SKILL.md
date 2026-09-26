---
name: project-edit
description: >-
  Modifies metadata (owner, title, remote URL, archetype, or lifecycle status) across an existing project and keeps the master registry synchronized (e.g. "/project-edit LAB-003 --owner 'Jane Doe'", "/project-edit LAB-002 --health completed").
---

# Skill: Edit Project Metadata & Lifecycle (`/project-edit`)

## Objective
Update administrative and lifecycle metadata for an initiative while ensuring strict synchronization between `README.md`, `STATUS.md`, and the root Master Project Registry.

---

## 1. Trigger Patterns
Activate this skill whenever the user invokes:
- `/project-edit <ID> --owner "<New Owner>"`
- `/project-edit <ID> --title "<New Title>"`
- `/project-edit <ID> --url "<New GitHub URL>"`
- `/project-edit <ID> --health [on-track|at-risk|blocked|paused|completed]`
- *"Change owner of LAB-XXX to..."*
- *"Archive project LAB-XXX"*

---

## 2. Step-by-Step Procedure

### Step 1: Locate Target Project
- Validate that `projects/<ID>-<slug>/` exists.
- Read `projects/<ID>/README.md` and `projects/<ID>/STATUS.md`.

### Step 2: Apply Updates Across Project Files
1. **`projects/<ID>/README.md`**:
   - Update Property table (Owner, Title, Remote Repository link, Status).
2. **`projects/<ID>/STATUS.md`**:
   - Update Property table (Project Name, Current Health, Owner / Lead, Last Updated).
3. **`projects/<ID>/journal.md`**:
   - If health was changed to `⏸️ Paused`, `✅ Completed`, or `📦 Archived`, append a lifecycle transition note in the journal.

### Step 3: Synchronize Root `README.md`
Update the project's row in the **Master Project Registry** table:
- Project Name & Link
- Health badge
- Primary Owner
- Remote Repository Link

### Step 4: Commit Directly to `main`
```bash
git add . && git commit -m "chore(<id>): update project metadata (<attribute>)"
git push origin main
```
