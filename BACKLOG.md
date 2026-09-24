# Cetana Labs — Sprint Backlog & Roadmap

This document maintains the active sprint plan, prioritized product backlog, and delivered sprint archives for **Cetana Labs Control Hub (`LAB-000`)**.

---

## 🎯 Current Sprint: Sprint 4 — Automated Lead Engagement & Ecosystem Integrations

| Property | Value |
| :--- | :--- |
| **Sprint ID** | `SPRINT-04` |
| **Duration** | 2026-09-24 to 2026-10-08 (2 Weeks) |
| **Sprint Goal** | Implement automated lead ping engine (`BK-003`) for stale statuses and multi-repo PR cross-referencing (`BK-004`). |
| **Status** | 🟢 Active |
| **Lead** | Eialarasu |

### Planned Sprint Items

| Task ID | Item / Feature | Priority | Assignee | Status | Target Date |
| :---: | :--- | :---: | :---: | :---: | :---: |
| `TSK-024` | Automated Lead Ping Engine (`BK-003`) — issue/alert generation for stale status (> 14 days) | P1 | Eialarasu | 📋 Planned | 2026-10-01 |
| `TSK-025` | Multi-Repository PR Cross-Referencer (`BK-004`) — link sub-project PRs into Cetana journal | P2 | Eialarasu | 📋 Planned | 2026-10-05 |
| `TSK-026` | Option B: Slack / WhatsApp incoming webhook dispatch (`BK-001`) | P2 | Eialarasu | 📋 Planned | 2026-10-08 |
| `TSK-027` | Cloud Dev Migration (`RFC-LAB-000-001`) — Kiro Web primary env, Dev Environment protocol field, cloud dev guide & reproducible devcontainer | P1 | Eialarasu | ✅ Done | 2026-09-24 |
| `TSK-027` | Two-Phase Governance Contract (`/project-validate` pre-flight gate & `validation_receipt.json`) | P1 | Eialarasu | ✅ Completed | 2026-09-24 |

---

## 💡 Prioritized Backlog (Future Sprints)

| Backlog ID | Proposed Initiative / Capability | Priority | Archetype | Target Sprint | Notes |
| :---: | :--- | :---: | :---: | :---: | :--- |
| `BK-005` | PDF Executive Digest Export | P3 | Tooling | Backlog | One-click export for board/investor reporting |
| `BK-006` | Project Health Trend Telemetry | P3 | Analytics | Backlog | Historical velocity and health transition graphs on dashboard |
| `BK-007` | On-Demand Git Status Audit Trail & Role-Gated History | P3 | Governance | Backlog | Reconstructs historical sprint baselines & health transitions from Git logs of `STATUS.md`. On-demand CLI initially; plan simple auth / RBAC for future dashboard access to prevent developer surveillance perceptions. |
| `BK-008` | Control Hub Web App Evolution (db + server) | P2 | Platform | Backlog | Evolve the static control plane into a full web application (database + backend server). Prerequisite for `BK-007` RBAC. Cloud dev env shifts Kiro Web → Codespaces per `RFC-LAB-000-001` §5; services declared in `.devcontainer/`. |

---

## 📦 Delivered Sprints Archive

### Sprint 3: Portfolio Visualization & Web Dashboard (2026-09-23 to 2026-09-24)
- **Goal**: Implement static single-page Portfolio Web Dashboard (`BK-002`) with automated GitHub Pages hosting for visual executive reporting.
- **Deliverables**:
  - `TSK-017`: Portfolio Web Dashboard architecture & feasibility spike (`BK-002`).
  - `TSK-018`: Static dashboard generator (`scripts/generate_dashboard.py`) & HTML template (`docs/index.html`).
  - `TSK-019`: GitHub Pages deployment workflow (`.github/workflows/deploy-pages.yml`) for automated hosting.
  - `TSK-020`: System / Light / Dark theme toggle with persistent user storage and dynamic OS auto-switching.
  - `TSK-021`: 1-Click project-tailored AI On-board Prompt generation (`🚀 Copy On-board Prompt`).
  - `TSK-022`: Executive blocker alerting, crimson highlighting, and top KPI metric ("Hard Blockers").
  - `TSK-023`: Executive Attention Priority sorting and default Active Products landing tab.

### Sprint 2: Sprint Tracking & Automation Maturation (2026-09-23)
- **Goal**: Implement bare-minimum sprint tracking, enhance automated remote sync, portfolio integrity validation, and sprint closeout tooling.
- **Deliverables**:
  - `TSK-010`: Bare-minimum sprint tracking system (`BACKLOG.md` & `CHANGELOG.md`).
  - `TSK-011`: Synchronized current `LAB-000` status with sprint tracking milestone.
  - `TSK-012`: Autonomous remote `STATUS.md` auto-fetcher (`scripts/generate_status.py --sync-remote`).
  - `TSK-014`: Automated sprint closeout skill (`/sprint-done` for Cetana Labs).
  - `TSK-015`: Automated CI linter & portfolio integrity validator (`scripts/validate_portfolio.py`).
  - `TSK-016`: Compacted project ID sequence (`LAB-000` through `LAB-005`) with zero gaps.

### Sprint 1: Management Command Plane & Status Engine (2026-09-10 to 2026-09-23)
- **Goal**: Build zero-overhead executive status reporting and onboard active initiatives.
- **Deliverables**:
  - Authoritative 30-line `STATUS.md` standard and parser (`scripts/generate_status.py`).
  - GitHub Actions weekday morning cron broadcast at 9:30 AM IST.
  - Constructive Visibility (`⏳ Onboarding Pending`) and 14-day staleness tracking.
  - Reindexed control hub to system zero-index `LAB-000`.
  - Slash commands: `/project-status`, `/project-add`, `/project-update`, `/project-edit`.
  - Onboarded `LAB-004` (Zerobea.ai) and `LAB-005` (Nexus Beacon).

### Sprint 0: Foundation & Initial Archetypes (2026-09-06 to 2026-09-09)
- **Goal**: Establish central engineering hub, directory conventions, and initial templates.
- **Deliverables**:
  - Master registry, `AGENTS.md`, and trunk-based git commit protocol.
  - Scaffolds for `mini-app`, `research`, `data-collection`, and `verification`.
  - Onboarded `LAB-001` (AAMAS), `LAB-002` (WrenAI), and `LAB-003` (Nexus Pulse).
