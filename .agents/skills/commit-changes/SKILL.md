---
name: commit-changes
description: Stages changed documentation/project files and commits directly to main with standardized commit messages.
---

# Skill: Commit Changes

## Objective
Stage and commit changes directly to `main` following trunk-based conventions without creating branches or PRs.

---

## Step-by-Step Procedure

1. **Inspect Status**:
   - Check `git status` to verify the modified, untracked, or deleted files.
   - Verify that no untracked secrets, `.env` files, or IDE configurations (`.idea/`) are staged.

2. **Select Commit Prefix & Message**:
   - For a new project: `feat(lab-XXX): init <project-name>`
   - For a milestone update: `log(lab-XXX): <milestone summary>`
   - For an executive status update: `status(lab-XXX): <health/win summary>`
   - For project metadata edit: `chore(lab-XXX): update <attribute>`
   - For global repo updates: `docs: <summary>`, `chore: <summary>`, or `feat(core): <summary>`

3. **Stage and Commit**:
   ```bash
   git add .
   git commit -m "<type>(<scope>): <summary>"
   git push origin main
   ```
