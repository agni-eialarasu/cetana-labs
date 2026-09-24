# LAB-000: Cetana Labs Control Hub — Project Journal & Timeline

## 📌 Phase Summary

| Phase | Scope & Milestones | Status | Completion Date |
| :--- | :--- | :--- | :--- |
| **Phase 1: Architecture & Repository Initialization** | Master hub, templates, AGENTS.md, trunk-based commit protocol | ✅ Completed | 2026-09-06 |
| **Phase 2: Project Onboarding Baseline** | Initialized LAB-001 (AAMAS), LAB-002 (WrenAI), LAB-003 (Nexus Pulse) | ✅ Completed | 2026-09-09 |
| **Phase 3: Automated Status & Command Suite** | STATUS.md protocol, scripts/generate_status.py, GitHub Actions CI cron, /project-* skills | ✅ Completed | 2026-09-23 |
| **Phase 4: Sprint Tracking & Delivery Governance** | BACKLOG.md, CHANGELOG.md, Constructive Visibility, 14-day staleness tracking | ✅ Completed | 2026-09-23 |
| **Phase 5: Automation Maturation & Portfolio Validation** | Remote sync, CI validator, /sprint-done skill, sequence compaction | ✅ Completed | 2026-09-23 |
| **Phase 6: Portfolio Visualization & Web Dashboard** | Static HTML single-page dashboard (BK-002), GitHub Pages deployment | ✅ Completed | 2026-09-24 |
| **Phase 7: Automated Lead Engagement & Ecosystem Integrations** | Stale status ping engine (BK-003), multi-repo PR cross-referencing | 🟢 Active | 2026-10-08 |

---

## 📅 Milestone Log

### [2026-09-24] Milestone: Dashboard Card Restructure — Owner-First Identity
- **Context**: Change request to surface the **project owner** (accountability) instead of the internal Project ID on the face of each dashboard card. The Project ID is valueless to executive viewers and is now kept internal-only.
- **Key Deliverables**:
  - Replaced the top-left `id-badge` with an **owner-name pill** (`👤 Lead`) in `scripts/generate_dashboard.py`; health pill remains top-right.
  - Removed the duplicate lead from the card meta row (now archetype-only) to avoid showing the owner twice.
  - Retained the Project ID internally — `data-id` (sort), `data-search` (search still matches on ID), and a hover `title` tooltip on the owner pill for traceability.
  - Added graceful `— Unassigned` fallback (`.owner-pill.unassigned`) for empty/generic leads.
  - Regenerated `docs/index.html` (6/6 cards) and validated the portfolio.

---

### [2026-09-24] Milestone: Automated Lead Ping Engine (`BK-003` / `TSK-024`)
- **Context**: Delivered Sprint 4 P1 item — automated detection and pinging of initiatives that fall behind sprint cadence or never onboard, eliminating manual lead chasing. Per directive, the `LAB-000` control hub is excluded from pinging.
- **Key Deliverables**:
  - Built `scripts/ping_leads.py` reusing the authoritative `generate_status.parse_status_file` parser; detects **stale** (`Last Updated` > 14 days, non-completed) and **onboarding-pending** initiatives.
  - **Exclusions**: `LAB-000` kernel and `✅ Completed` projects are never pinged (mirrors the executive portfolio digest filter).
  - **Idempotent GitHub issue dispatch** via `gh` — stable `[Cetana Ping] <LAB-ID>` title marker; refreshes existing open issues instead of duplicating; routes to each sub-project repo with a control-hub fallback.
  - Added scheduled workflow `.github/workflows/lead-ping-cron.yml` (weekly Monday 10:00 AM IST + manual dry-run dispatch) and the `/ping-leads` skill (`.agents/skills/ping-leads/SKILL.md`, registered in `AGENTS.md`).
  - Closed `TSK-024` in `SPRINT-04`; synchronized `BACKLOG.md` and `CHANGELOG.md`.

---

### [2026-09-24] Milestone: Cloud-Based Development Migration (`RFC-LAB-000-001`)
- **Context**: The maintainer ran IntelliJ IDEA + Antigravity for both `LAB-000` and a separate stateful fullstack project on one machine, causing performance degradation. Since `LAB-000` has no local runtime dependency (docs + zero-dependency Python; automation runs in CI), it was migrated to cloud-based development to free the local machine for the fullstack initiative.
- **Key Deliverables**:
  - Authored and ratified [`RFC-LAB-000-001`](../../docs/rfc/RFC-LAB-000-001-cloud-dev-migration.md) under a new `docs/rfc/` convention — **Kiro Web** as primary cloud environment, GitHub Codespaces as fallback for future services.
  - Defined a reusable **☁️ Cloud vs 💻 Local classification heuristic** (RFC §4) and made `Dev Environment` a first-class field in the `STATUS.md` protocol (`docs/project-protocol.md` §4a) and the master registry (`Dev Env` column).
  - Published cloud dev onboarding runbook (`docs/cloud-dev-guide.md`) and a reproducible dev container (`.devcontainer/`, Python 3.11 + GitHub CLI).
  - Registered `BK-008` (Control Hub Web App evolution — db + server) as the platform prerequisite for `BK-007` RBAC; RFC §5 anticipates the cloud env shifting Kiro Web → Codespaces at that point.
  - Closed `TSK-027` in `SPRINT-04`; synchronized `BACKLOG.md` and `CHANGELOG.md`.

---

### [2026-09-24] Milestone: Adopted RFC for `/project-validate` & Two-Phase Governance Contract
- **Context**: Formally ratified and adopted the RFC authored by Agni Eialarasu (LAB-003 Nexus Pulse) establishing the Two-Phase Governance Contract across Cetana Labs initiatives.
- **Key Deliverables**:
  - Implemented universal 5-pillar validation engine (`scripts/project_validate.py`) enforcing scraper line budget (<= 35 lines), multi-registry lockstep, git hygiene, architectural boundaries, and live test counts.
  - Automatically emits immutable `.gemini/governance/validation_receipt.json` pre-flight audit receipt artifact.
  - Created standardized AI agent skill (`.agents/skills/project-validate/SKILL.md`).
  - Updated universal protocol guidelines (`AGENTS.md`, `docs/project-protocol.md`, `docs/project-owner-guide.md`).

---

### [2026-09-24] Milestone: Sprint 3 Closeout & v0.5.0 Release
- **Context**: Executed formal sprint closeout (`/sprint-done`) for Sprint 3.
- **Key Deliverables**:
  - Developed and launched the **Portfolio Web Dashboard (`BK-002`)** deployed live via GitHub Actions on GitHub Pages at [https://agni-eialarasu.github.io/cetana-labs/](https://agni-eialarasu.github.io/cetana-labs/).
  - Built an executive **Blocker Alerting & Highlighting engine** rendering crimson alerts and an interactive "Hard Blockers" KPI metric.
  - Implemented **Executive Attention Priority sorting** and defaulted dashboard landing to **Active Products**.
  - Built **1-Click AI On-board Prompts (`🚀 Copy On-board Prompt`)** eliminating all documentation friction for incoming project leads.
  - Delivered seamless **System / Light / Dark theme support** with dynamic OS auto-switching.
  - Verified remote status sync for `LAB-003: Nexus Pulse` (v1.2.0 baseline, 431 tests passing).
  - Bumper CHANGELOG release to `v0.5.0` and initialized `SPRINT-04`.

---

### [2026-09-23] Milestone: Sprint 2 Closeout & v0.4.0 Release
- **Context**: Executed formal sprint closeout (`/sprint-done`) for Sprint 2.
- **Key Deliverables**:
  - Compacted project sequence to `LAB-000` through `LAB-005` with zero sequence gaps.
  - Deployed remote status auto-sync (`--sync-remote`) querying external GitHub repos directly.
  - Implemented `scripts/validate_portfolio.py` for automated CI protocol and structural validation.
  - Authored automated `/sprint-done` skill playbook.
  - Promoted CHANGELOG release to `v0.4.0` and kicked off `SPRINT-03` targeting Portfolio Web Dashboard (`BK-002`).

---

### [2026-09-23] Milestone: Initialized Bare-Minimum Sprint Tracking System
- **Context**: Added lightweight, zero-overhead sprint tracking and delivery governance directly into the repository root.
- **Key Deliverables**:
  - Created [`BACKLOG.md`](../../BACKLOG.md) capturing active Sprint 2 tasks, prioritized future backlog, and delivered sprint archives.
  - Created [`CHANGELOG.md`](../../CHANGELOG.md) adhering to Keep a Changelog standards spanning releases v0.1.0, v0.2.0, and v0.3.0.
  - Synchronized `STATUS.md` and linked resources in master `README.md`.\n
---\n
