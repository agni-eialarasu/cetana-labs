# Cetana Labs — Sprint Backlog & Roadmap

This document maintains the active sprint plan, prioritized product backlog, and delivered sprint archives for **Cetana Labs Control Hub (`LAB-000`)**.

---

## 🎯 Current Sprint: Sprint 3 — Portfolio Visualization & Web Dashboard

| Property | Value |
| :--- | :--- |
| **Sprint ID** | `SPRINT-03` |
| **Duration** | 2026-09-24 to 2026-10-08 (2 Weeks) |
| **Sprint Goal** | Implement static single-page Portfolio Web Dashboard (`BK-002`) for visual executive reporting. |
| **Status** | 🟢 Active |
| **Lead** | Eialarasu |

### Planned Sprint Items

| Task ID | Item / Feature | Priority | Assignee | Status | Target Date |
| :---: | :--- | :---: | :---: | :---: | :---: |
| `TSK-017` | Portfolio Web Dashboard architecture & feasibility spike (`BK-002`) | P1 | Eialarasu | 🚧 In Progress | 2026-09-25 |
| `TSK-018` | Static dashboard generator (`scripts/generate_dashboard.py`) & HTML template | P1 | Eialarasu | 📋 Planned | 2026-09-30 |
| `TSK-019` | GitHub Pages deployment workflow for automated dashboard hosting | P2 | Eialarasu | 📋 Planned | 2026-10-05 |

---

## 💡 Prioritized Backlog (Future Sprints)

| Backlog ID | Proposed Initiative / Capability | Priority | Archetype | Target Sprint | Notes |
| :---: | :--- | :---: | :---: | :---: | :--- |
| `BK-001` | Option B: Slack / WhatsApp incoming webhook dispatch | P1 | Automation | Backlog | Direct channel POSTing from GitHub Actions cron via secret URL |
| `BK-003` | Automated Lead Ping Engine | P2 | Automation | Sprint 4 | Auto-creates GitHub issue or alert when status is stale > 14 days |
| `BK-004` | Multi-Repository PR Cross-Referencer | P3 | Integration | Sprint 4 | Link pull requests across sub-projects directly into Cetana journal |
| `BK-005` | PDF Executive Digest Export | P3 | Tooling | Backlog | One-click export for board/investor reporting |

---

## 📦 Delivered Sprints Archive

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
