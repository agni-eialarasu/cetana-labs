# Cetana Labs — Sprint Backlog & Roadmap

This document maintains the active sprint plan, prioritized product backlog, and delivered sprint archives for **Cetana Labs Control Hub (`LAB-000`)**.

---

## 🎯 Current Sprint: Sprint 2 — Sprint Tracking & Automation Maturation

| Property | Value |
| :--- | :--- |
| **Sprint ID** | `SPRINT-02` |
| **Duration** | 2026-09-24 to 2026-10-08 (2 Weeks) |
| **Sprint Goal** | Implement bare-minimum sprint tracking, enhance automated remote sync, and prototype webhook dispatches. |
| **Status** | 🟢 Active |
| **Lead** | Eialarasu |

### Planned Sprint Items

| Task ID | Item / Feature | Priority | Assignee | Status | Target Date |
| :---: | :--- | :---: | :---: | :---: | :---: |
| `TSK-010` | Bare-minimum sprint tracking system (`BACKLOG.md` & `CHANGELOG.md`) | P0 | Eialarasu | ✅ Done | 2026-09-24 |
| `TSK-011` | Synchronize current `LAB-000` status with sprint tracking milestone | P0 | Eialarasu | ✅ Done | 2026-09-24 |
| `TSK-012` | Autonomous remote `STATUS.md` auto-fetcher (querying project repos directly) | P1 | Eialarasu | 📋 Planned | 2026-10-01 |
| `TSK-013` | Option B: Slack / WhatsApp incoming webhook dispatch prototype | P1 | Eialarasu | 📋 Planned | 2026-10-05 |
| `TSK-014` | Add automated sprint closeout skill (`/sprint-done` for Cetana Labs) | P2 | Eialarasu | 📋 Planned | 2026-10-08 |

---

## 💡 Prioritized Backlog (Future Sprints)

| Backlog ID | Proposed Initiative / Capability | Priority | Archetype | Target Sprint | Notes |
| :---: | :--- | :---: | :---: | :---: | :--- |
| `BK-001` | Portfolio Web Dashboard | P2 | Mini-App | Sprint 3 | Static single-page HTML/JS view hosted via GitHub Pages |
| `BK-002` | Automated Lead Ping Engine | P2 | Automation | Sprint 3 | Auto-creates GitHub issue or Slack alert when status is stale > 14 days |
| `BK-003` | Multi-Repository PR Cross-Referencer | P3 | Integration | Sprint 4 | Link pull requests across sub-projects directly into Cetana journal |
| `BK-004` | PDF Executive Digest Export | P3 | Tooling | Backlog | One-click export for board/investor reporting |

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
  - Onboarded `LAB-005` (Zerobea.ai) and `LAB-006` (Nexus Beacon).

### Sprint 0: Foundation & Initial Archetypes (2026-09-06 to 2026-09-09)
- **Goal**: Establish central engineering hub, directory conventions, and initial templates.
- **Deliverables**:
  - Master registry, `AGENTS.md`, and trunk-based git commit protocol.
  - Scaffolds for `mini-app`, `research`, `data-collection`, and `verification`.
  - Onboarded `LAB-001` (AAMAS), `LAB-002` (WrenAI), and `LAB-003` (Nexus Pulse).
