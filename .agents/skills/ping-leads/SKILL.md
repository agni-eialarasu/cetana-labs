---
name: ping-leads
description: >-
  Scans authoritative STATUS.md files and generates automated lead "ping" alerts (idempotent GitHub issues) for stale (> 14 days) or onboarding-pending initiatives (e.g. "/ping-leads", "/ping-leads --create-issues"). Excludes the LAB-000 control hub and completed projects.
---

# Skill: Automated Lead Ping Engine (`/ping-leads`)

## Objective
Enforce sprint cadence and onboarding discipline (`BK-003`) by automatically detecting initiatives that need lead attention and pinging them via idempotent GitHub issues — without manual chasing.

Two-tier detection, mirroring the executive portfolio digest filter:
- **Stale**: an active (non-completed) project whose `Last Updated` is older than 14 days.
- **Onboarding Pending**: a project still awaiting its initial `STATUS.md` baseline.

> **Exclusions**: The `LAB-000` control-hub kernel and all `✅ Completed` initiatives are never pinged.

---

## 1. Trigger Patterns
Activate this skill whenever the user invokes:
- `/ping-leads`
- `/ping-leads --create-issues`
- *"Ping stale project leads"*
- *"Which projects are overdue for a status update?"*
- *"Alert leads who haven't onboarded"*

---

## 2. Automated Execution Engine

```bash
# Dry-run preview (default, safe — no issues created)
python3 scripts/ping_leads.py

# Machine-readable JSON of pending pings
python3 scripts/ping_leads.py --json

# Live dispatch: create/refresh idempotent GitHub issues on each project repo
python3 scripts/ping_leads.py --create-issues

# Pull the freshest remote STATUS.md before evaluating cadence
python3 scripts/ping_leads.py --create-issues --sync-remote
```

---

## 3. Core Behavior & Rules

1. **Reuses the authoritative parser** (`generate_status.parse_status_file`) — no parsing logic drift.
2. **Idempotent issue creation**: each ping issue carries a stable title marker
   `[Cetana Ping] <LAB-ID>: ...`. Before creating, the engine searches for an
   existing OPEN issue with that marker; if found, it appends a refresh comment
   instead of opening a duplicate.
3. **Issue routing**: pings target the sub-project's own GitHub repo (parsed from
   its `README.md`). If the repo cannot be resolved, the ping falls back to a
   tracking issue on the control hub (`agni-eialarasu/cetana-labs`).
4. **Onboarding precedence**: onboarding-pending projects receive the onboarding
   CTA (`/status-init`) and are not additionally flagged as stale.
5. **CI signal**: exits non-zero if any issue dispatch fails.

---

## 4. Automated Cadence (GitHub Actions)

The engine runs unattended via `.github/workflows/lead-ping-cron.yml`:
- **Scheduled**: every Monday 10:00 AM IST (04:30 UTC) — always dispatches.
- **Manual (`workflow_dispatch`)**: honors a `dry_run` input (defaults to preview-only).

---

## 5. Presentation
- Dry-run output is a concise, scannable console report (project, reason, lead, target repo).
- Issue bodies are executive-friendly Markdown with the exact CTA (`/status-init` or `/status-update`) and a link to the Project Protocol.
