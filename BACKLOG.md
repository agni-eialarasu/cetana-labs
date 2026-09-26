# Cetana Labs — Sprint Backlog & Roadmap

This document maintains the active sprint plan, prioritized product backlog, and delivered sprint archives for **Cetana Labs Control Hub (`LAB-000`)**.

---

## 🎯 Current Sprint: Sprint 7 — Sleek UI Deployment & Auth Foundations

| Property | Value |
| :--- | :--- |
| **Sprint ID** | `SPRINT-07` |
| **Duration** | 2026-11-05 to 2026-11-19 (2 Weeks) |
| **Sprint Goal** | Deploy the Sleek UI (`app/web/`) to GitHub Pages (dual-run), begin BK-008 Phase 3 auth/RBAC scoping (`BK-007`), and deliver multi-repo PR cross-referencing (`BK-004`). |
| **Status** | 🟢 Active |
| **Lead** | Eialarasu |

### Planned Sprint Items

| Task ID | Item / Feature | Priority | Assignee | Status | Target Date |
| :---: | :--- | :---: | :---: | :---: | :---: |
| `TSK-036` | Sleek UI GitHub Pages deployment workflow (`app/web/` build → Pages, dual-run alongside static dashboard) | P1 | Eialarasu | ✅ Done | 2026-11-12 |
| `TSK-037` | BK-008 Phase 3 Scoping — Auth & RBAC (`BK-007`, `RFC-LAB-000-006`): GitHub OAuth identity, per-project role model via memberships, per-collection API rules, audit trail, non-surveillance safeguards | P1 | Eialarasu | ✅ Done | 2026-11-14 |
| `TSK-038` | Kiro-native skillset (Phase A) — migrate skills to `.kiro/skills/`, add infra/lifecycle/audit `/commands`, steering foundation; standardize DX across Kiro Web + IDE | P1 | Eialarasu | 🚧 In Progress | 2026-11-17 |
| `TSK-025` | Multi-Repository PR Cross-Referencer (`BK-004`) — link sub-project PRs into Cetana journal | P2 | Eialarasu | 📋 Planned | 2026-11-17 |
| `TSK-026` | Option B: Slack / WhatsApp incoming webhook dispatch (`BK-001`) | P2 | Eialarasu | 📋 Planned | 2026-11-19 |

---

## 💡 Prioritized Backlog (Future Sprints)

| Backlog ID | Proposed Initiative / Capability | Priority | Archetype | Target Sprint | Notes |
| :---: | :--- | :---: | :---: | :---: | :--- |
| `BK-005` | PDF Executive Digest Export | P3 | Tooling | Backlog | One-click export for board/investor reporting |
| `BK-006` | Project Health Trend Telemetry | P3 | Analytics | Backlog | Historical velocity and health transition graphs on dashboard |
| `BK-007` | On-Demand Git Status Audit Trail & Role-Gated History | P2 | Governance | SPRINT-07 (scoped) | Role-gated history & audit trail. Auth/RBAC scoped in [`RFC-LAB-000-006`](docs/rfc/RFC-LAB-000-006-auth-rbac.md) (`TSK-037`) — GitHub OAuth, per-project roles via `memberships`, per-collection API rules, access-only audit (non-surveillance). Delivered as BK-008 Phase 3 atop the web app. |
| `BK-008` | Control Hub Web App Evolution (PocketBase, db + server) | P2 | Platform | SPRINT-06 (scoping) | Evolve the static control plane into a full PocketBase web application (database + backend server). Scoped in [`RFC-LAB-000-003`](docs/rfc/RFC-LAB-000-003-pocketbase-web-app.md) (`TSK-031`). Prerequisite for `BK-007` RBAC. Cloud dev env shifts Kiro Web → Codespaces per `RFC-LAB-000-001` §5; services declared in `.devcontainer/`. Consumes the `BK-009` relational data layer as its seed schema. |
| `BK-009` | Relational JSON Data Layer (`RFC-LAB-000-002`) | P1 | Data | ✅ Delivered (SPRINT-05, `TSK-030`) | User & project masters + many-to-many memberships join under `data/`; generated README registry; referential-integrity validator pillar. PocketBase-ready schema; foundation for `BK-008` + `BK-007` RBAC. |

---

## 📦 Delivered Sprints Archive

### Sprint 6: Web App Foundation (BK-008 P1–P2) & Branch-Based Development (2026-09-24)
- **Goal**: Stand up the PocketBase web-app foundation on the `BK-009` data layer and adopt industry-standard branch-based development.
- **Deliverables**:
  - `TSK-031`: Web App scoping RFC (`RFC-LAB-000-003`) — PocketBase architecture, collection mapping, phased plan.
  - `TSK-032`: Branch-based development model (`RFC-LAB-000-004`) — GitHub Flow, hybrid path-scoping, PR CI gate; dogfooded as PR #1.
  - `TSK-033`: BK-008 Phase 1 — PocketBase backend scaffolding (`app/pocketbase/pb_schema.json`, `pb_import.py`, devcontainer service) [PR #2].
  - `TSK-034`: BK-008 Phase 2 scoping (`RFC-LAB-000-005`) — SvelteKit static-SPA decision + org design-system adoption (`docs/DESIGN.md`).
  - `TSK-035`: BK-008 Phase 2 build — SvelteKit 5 + pnpm + Tailwind Sleek UI (`app/web/`) at read-parity; `status.json` exporter; Node CI job [PR #3].
- **Carried Forward**: `TSK-025` (Multi-Repo PR Cross-Referencer) and `TSK-026` (Slack/WhatsApp webhook dispatch) → `SPRINT-07`.

### Sprint 5: Ecosystem Integrations & Relational Data Layer (2026-09-24)
- **Goal**: Establish a relational data foundation for the portfolio and prepare the ground for the web-app evolution.
- **Deliverables**:
  - `TSK-030`: Relational JSON Data Layer (`BK-009`, `RFC-LAB-000-002`) — `data/users.json`, `data/portfolio.json` (1:1 `owner_id`), and `data/memberships.json` (many-to-many join) with PocketBase-ready JSON Schemas; generated README master registry (`scripts/generate_registry.py`); shared accessor (`scripts/portfolio_data.py`); referential-integrity validator pillar.
- **Carried Forward**: `TSK-025` (Multi-Repo PR Cross-Referencer) and `TSK-026` (Slack/WhatsApp webhook dispatch) → `SPRINT-06`.

### Sprint 4: Automated Lead Engagement & Ecosystem Integrations (2026-09-24)
- **Goal**: Mature portfolio governance — pre-flight validation, automated lead engagement, cloud-based development, and executive dashboard refinement.
- **Deliverables**:
  - `TSK-024`: Automated Lead Ping Engine (`BK-003`) — `scripts/ping_leads.py` + weekly `lead-ping-cron.yml` workflow + `/ping-leads` skill; idempotent GitHub issue alerts for stale (> 14 days) and onboarding-pending initiatives (excludes `LAB-000` and completed).
  - `TSK-027`: Two-Phase Governance Contract — `/project-validate` 5-pillar pre-flight gate (`scripts/project_validate.py`) emitting immutable `validation_receipt.json`.
  - `TSK-028`: Cloud Dev Migration (`RFC-LAB-000-001`) — Kiro Web primary environment, `Dev Environment` protocol field & registry column, `docs/cloud-dev-guide.md`, and reproducible `.devcontainer/`.
  - `TSK-029`: Dashboard Card Restructure — surfaced the project owner as a top-left identity pill and made the internal Project ID non-visible (retained for search, sort, and hover tooltip).
- **Carried Forward**: `TSK-025` (Multi-Repo PR Cross-Referencer) and `TSK-026` (Slack/WhatsApp webhook dispatch) → `SPRINT-05`.

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
