---
name: log-milestone
description: Appends a high-level milestone or phase transition to a project's journal.md.
---

# Skill: Log Milestone

## Objective
Record a new dated milestone, architectural decision, or phase transition in a project's `journal.md` and keep the metadata synchronized.

---

## Step-by-Step Procedure

1. **Locate Target Project**:
   - Find `projects/LAB-XXX-<slug>/journal.md`.

2. **Format Milestone Entry**:
   - Add a reverse-chronological entry (newest on top of the Milestone Log section):
   ```markdown
   ### [YYYY-MM-DD] Milestone: <Title>
   - **Context**: Summary of what was worked on or achieved.
   - **Key Decisions & Technical Architecture**:
     - Decision 1 (trade-offs, rationale).
   - **Outcomes / Artifacts**:
     - Links or references to deliverables.
   - **Next Steps**:
     - Immediate next priorities.
   ```

3. **Update Phase Status (If Applicable)**:
   - If a milestone completes or starts a phase, update the **Phase Summary** table in `journal.md` (e.g. `🟢 Active` $\rightarrow$ `✅ Completed`).

4. **Update Project Metadata**:
   - Update `Last Updated` in `projects/LAB-XXX-<slug>/README.md`.
   - If overall project status changed, update `projects/LAB-XXX-<slug>/README.md` and the master table in root `README.md`.
