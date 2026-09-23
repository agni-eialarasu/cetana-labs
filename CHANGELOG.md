# Changelog

All notable changes to **Cetana Labs Control Hub (`LAB-000`)** and master management plane will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]
### Planned
- Autonomous remote `STATUS.md` fetching from project GitHub repositories.
- Option B direct webhook dispatcher for WhatsApp / Slack channels.
- Single-page static web dashboard for portfolio-level visualization.

---

## [0.3.0] - 2026-09-23
### Added
- **Constructive Visibility Protocol**: Implemented `⏳ Onboarding Pending` alert to hold project leads accountable for running `/status-init`.
- **Sprint Cadence Staleness Tracking**: Automated 14-day staleness detection in `scripts/generate_status.py` to maintain bi-weekly update discipline.
- **Bare-Minimum Sprint Tracking**: Introduced root `BACKLOG.md` and `CHANGELOG.md` to maintain planned sprint items, prioritized backlogs, and historical releases.
- **New Initiatives Onboarded**: Registered `LAB-005` (Zerobea.ai) and `LAB-006` (Nexus Beacon) into the portfolio.

### Changed
- **Kernel Architecture Reindex**: Reindexed Cetana Labs control hub from `LAB-004` to system zero-index `LAB-000`.
- **Digest Filtering**: Refined default portfolio broadcast to show only active, non-completed product engineering initiatives, keeping leadership briefings concise and noise-free.

---

## [0.2.0] - 2026-09-23
### Added
- **`STATUS.md` Protocol Standard**: Defined strict 30-line, 5-section schema for executive project tracking (`docs/project-protocol.md`).
- **Executive Status Generator**: Created standalone zero-dependency Python generator (`scripts/generate_status.py`) rendering mobile-friendly WhatsApp briefings.
- **Automated Morning Broadcast**: Configured weekday GitHub Actions workflow (`.github/workflows/project-status-cron.yml`) running at 9:30 AM IST (04:00 UTC).
- **AI Slash Command Playbooks**: Created `.agents/skills/` suite for autonomous project lifecycle management:
  - `/project-status`: Generates instant WhatsApp updates.
  - `/project-add`: Onboards new initiatives via remote-first inspection.
  - `/project-update`: Logs wins and synchronizes health badges.
  - `/project-edit`: Updates owners, URLs, and lifecycle states.
- **Developer Playbook**: Authored `docs/project-owner-guide.md` with copy-paste AI prompt packs for `/status-init` and `/status-update`.

---

## [0.1.0] - 2026-09-09
### Added
- **Cetana Labs Master Hub**: Initialized control plane, repository registry, and universal AI agent guidelines (`AGENTS.md`, `CLAUDE.md`).
- **Standardized Archetype Templates**: Scaffolds for `mini-app`, `research`, `data-collection`, and `verification`.
- **Initial Portfolio Initiatives**:
  - `LAB-001`: AAMAS (Autism Activity Monitoring & Alerting System).
  - `LAB-002`: WrenAI Capabilities & Semantic GenBI Evaluation.
  - `LAB-003`: Nexus Pulse (Governed Deterministic Vertical Engine).
- **Trunk-Based Commit Standard**: Automated commit-changes playbook and linear main branch policy.
