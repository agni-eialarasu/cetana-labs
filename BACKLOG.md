# Cetana Labs — Sprint Backlog & Roadmap

This document maintains the active sprint plan, prioritized product backlog, and delivered sprint archives for **Cetana Labs Control Hub (`LAB-000`)**.

---

## 🎯 Current Sprint: Sprint 2 — Sprint Tracking & Automation Maturation

| Property | Value |
| :--- | :--- |
| **Sprint ID** | `SPRINT-02` |
| **Duration** | 2026-09-24 to 2026-10-08 (2 Weeks) |
| **Sprint Goal** | Implement bare-minimum sprint tracking, enhance automated remote sync, portfolio integrity validation, and sprint closeout tooling. |
| **Status** | 🟢 Active |
| **Lead** | Eialarasu |

### Planned Sprint Items

| Task ID | Item / Feature | Priority | Assignee | Status | Target Date |
| :---: | :--- | :---: | :---: | :---: | :---: |
| `TSK-010` | Bare-minimum sprint tracking system (`BACKLOG.md` & `CHANGELOG.md`) | P0 | Eialarasu | ✅ Done | 2026-09-24 |
| `TSK-011` | Synchronize current `LAB-000` status with sprint tracking milestone | P0 | Eialarasu | ✅ Done | 2026-09-24 |
| `TSK-012` | Autonomous remote `STATUS.md` auto-fetcher (`--sync-remote`) | P1 | Eialarasu | ✅ Done | 2026-09-24 |
| `TSK-014` | Add automated sprint closeout skill (`/sprint-done` for Cetana Labs) | P1 | Eialarasu | ✅ Done | 2026-09-24 |
| `TSK-015` | Automated CI linter & portfolio integrity validator (`validate_portfolio.py`) | P1 | Eialarasu | ✅ Done | 2026-09-24 |
| `TSK-016` | Compact project ID sequence (`LAB-000` through `LAB-005`) | P1 | Eialarasu | ✅ Done | 2026-09-24 |

---

## 💡 Prioritized Backlog (Future Sprints)

| Backlog ID | Proposed Initiative / Capability | Priority | Archetype | Target Sprint | Notes |
| :---: | :--- | :---: | :---: | :---: | :--- |
| `BK-001` | Option B: Slack / WhatsApp incoming webhook dispatch | P1 | Automation | Sprint 3 | Direct channel POSTing from GitHub Actions cron via secret URL |
| `BK-002` | Portfolio Web Dashboard | P2 | Mini-App | Sprint 3 | Static single-page HTML/JS view hosted via GitHub Pages |
| `BK-003` | Automated Lead Ping Engine | P2 | Automation | Sprint 3 | Auto-creates GitHub issue or Slack alert when status is stale > 14 days |
| `BK-004` | Multi-Repository PR Cross-Referencer | P3 | Integration | Sprint 4 | Link pull requests across sub-projects directly into Cetana journal |
| `BK-005` | PDF Executive Digest Export | P3 | Tooling | Backlog | One-click export for board/investor reporting |

---

## 📦 Delivered Sprints Archive

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
