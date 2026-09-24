---
name: project-validate
description: >-
  Executes the 5-pillar programmatic pre-flight validation gate for repository hygiene, scraper line budget, multi-registry lockstep, architecture/portability parity, and test suite counts prior to status emission (e.g. "/project-validate", "/project-validate LAB-003"). Emits validation_receipt.json.
---

# Skill: Programmatic Pre-Flight Project Validation (`/project-validate`)

## Objective
Enforce the Two-Phase Governance Contract across Cetana Labs initiatives:
`[ /project-validate ] ──(If GREEN)──> [ /project-status ]`

Runs an automated 5-pillar audit to prevent metric drift, eliminate hallucinated test tallies, guarantee `< 35 lines` STATUS.md scraper budget, and ensure 100% registry lockstep before executive broadcasts or sprint closeouts.

---

## 1. Trigger Patterns
Activate this skill whenever the user invokes:
- `/project-validate`
- `/project-validate [project_id_or_path]`
- `/validate-project`
- *"Run pre-flight check on LAB-003"*
- Prior to running `/project-status` or `/status-update` in high-governance mode.

---

## 2. Automated Execution Engine

Execute the authoritative Python verification engine:
```bash
# Validate Cetana Labs Control Hub (LAB-000)
python3 scripts/project_validate.py

# Validate a specific subproject / initiative
python3 scripts/project_validate.py --dir projects/LAB-003-nexus-pulse

# Allow dirty working tree during local development
python3 scripts/project_validate.py --allow-dirty

# Emit machine-readable validation receipt
python3 scripts/project_validate.py --json
```

---

## 3. The 5 Core Verification Pillars

1. **Pillar 1: Scraper Line Budget & Schema Compliance**
   - Asserts root `STATUS.md` is strictly `<= 35 lines`.
   - Asserts required metadata table keys: `Project ID`, `Project Name`, `Current Health`, `Owner / Lead`, `Last Updated`.
   - Asserts all 5 required section headers are present.
   - Flags any syntax deviation that would break the daily 9:30 AM IST automated scraper.

2. **Pillar 2: Multi-Registry Synchronization (Lockstep Invariant)**
   - Confirms synchronized alignment across `CHANGELOG.md`, `BACKLOG.md` (or `SPRINT_TRACKER.md`), and `journal.md`.
   - Asserts semantic release or milestone date formatting.
   - Asserts delivered deliverables contain verifiable commit SHAs or PR references.

3. **Pillar 3: Git Hygiene & Worktree Parity**
   - Asserts git working tree is clean (zero unstaged/untracked files).
   - Asserts local branch is up to date with origin remote tracking branch.

4. **Pillar 4: Architectural Boundaries & Deterministic Math Parity**
   - Executes AST layer isolation checks (e.g. 42/42 AST layer isolation checks).
   - Verifies zero absolute local path violations in documentation (Principle 2).
   - Reconciles deterministic calculation kernels against canonical golden datasets if configured.

5. **Pillar 5: Live Test Suite Verification & Auto-Count**
   - Executes the live test suite (pytest, npm test, or `validate_portfolio.py`).
   - Extracts exact real-time test counts (passed, skipped, failed) for direct ingestion by `/project-status`.

---

## 4. Verification Receipt Artifact

Upon execution, the engine writes an immutable receipt to:
`.gemini/governance/validation_receipt.json`

This JSON payload certifies the commit SHA, timestamp, and per-pillar PASS/FAIL metrics to serve as the cryptographically reproducible proof for status generation.
