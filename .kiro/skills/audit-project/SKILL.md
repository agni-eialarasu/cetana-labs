---
name: audit-project
description: >-
  Runs a whole-project health sweep for a Cetana Labs initiative (or the portfolio) — registry lockstep, STATUS.md freshness/staleness, referential integrity, and required-doc presence — and reports a prioritized findings summary. Use when the user runs /audit-project [ID] or asks for a project/portfolio health check.
---

# Skill: Project Health Audit (`/audit-project`)

## Objective
A broad governance & hygiene sweep across a project (or the whole portfolio), aggregating the automated validators plus higher-level checks into one prioritized report. Complements `/audit-doc` (single-file review) and `/project-validate` (the pre-flight gate).

## Trigger Patterns
- `/audit-project` (whole portfolio)
- `/audit-project LAB-003` (a specific initiative)
- "audit the project", "portfolio health check"

## Steps

### 1. Run the automated validators
```bash
python3 scripts/validate_portfolio.py            # structure, protocol, referential integrity, README reg
python3 scripts/generate_registry.py --check       # README registry vs data/
python3 scripts/generate_pb_schema.py --check       # PocketBase schema vs data/
python3 scripts/generate_status_json.py --check      # status.json vs STATUS.md
python3 scripts/project_validate.py --allow-dirty    # 5-pillar gate (scoped to --dir for one project)
```
For a single ID: `python3 scripts/project_validate.py --dir projects/<ID>-<slug>`.

### 2. Freshness & cadence
- For each active (non-completed) project: compute days since `Last Updated`; flag `> 14 days` (stale) and `⏳ Onboarding Pending`.
- Cross-reference `/ping-leads` logic (do not open issues here — report only).

### 3. Lockstep & consistency
- `README.md` registry, `BACKLOG.md`, `CHANGELOG.md`, `data/*.json`, and `projects/` directories agree (owner_id resolves, dir↔record, no duplicate `TSK`/`LAB` ids).
- CHANGELOG version ladder is monotonic; `[Unreleased]` present.

### 4. Required docs present
- Each `projects/LAB-XXX/` has `README.md`, `STATUS.md`, `journal.md`.

### 5. Report
- Prioritized summary: ❌ blockers → ⚠️ warnings → ✅ healthy, grouped by project.
- End with a one-line verdict (GREEN / needs-attention) and the top 3 recommended actions.
- Read-only: propose fixes, don't apply them unless asked.

## Notes
- This is a reporting/diagnostic skill — it never mutates state or opens issues.
- Use before `/sprint-done` or a release to catch drift early.
