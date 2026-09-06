---
name: update-runbook
description: Updates operational setup, execution steps, or troubleshooting in a project's runbook.md.
---

# Skill: Update Runbook

## Objective
Update operational instructions, environment variables, commands, or troubleshooting in `projects/LAB-XXX-<slug>/runbook.md`.

---

## Step-by-Step Procedure

1. **Locate Target Runbook**:
   - Find `projects/LAB-XXX-<slug>/runbook.md`.

2. **Apply Updates**:
   - Structure commands with clear markdown code blocks.
   - Never write machine-specific absolute paths (e.g. `/Users/...`). Use relative commands or `git clone` steps.
   - Keep prerequisites and troubleshooting tips clear and testable.

3. **Update Timestamps**:
   - Update `Last Updated` in `projects/LAB-XXX-<slug>/README.md`.
