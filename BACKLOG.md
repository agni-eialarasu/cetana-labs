# Cetana Labs — Sprint Backlog & Roadmap

This document maintains the active sprint plan, prioritized product backlog, and delivered sprint archives for **Cetana Labs Control Hub (`LAB-000`)**.

---

## 🎯 Current Sprint: Sprint 8 — Ecosystem Integrations & Work-Environment Standardization

| Property | Value |
| :--- | :--- |
| **Sprint ID** | `SPRINT-08` |
| **Duration** | 2026-11-19 to 2026-12-03 (2 Weeks) |
| **Sprint Goal** | Deliver multi-repo PR cross-referencing (`BK-004`) and Slack/WhatsApp webhook dispatch (`BK-001`); standardize the Kiro Web + IDE work-environment (`RFC-LAB-000-007`). |
| **Status** | 🟢 Active |
| **Lead** | Eialarasu |

### Planned Sprint Items

| Task ID | Item / Feature | Priority | Assignee | Status | Target Date |
| :---: | :--- | :---: | :---: | :---: | :---: |
| `TSK-039` | Work-Environment Standardization (`RFC-LAB-000-007`) — Kiro Web + IDE surface roles, `.nvmrc`/`.env.example`, Makefile cheat-sheet, Podman-first Containerfile, `/env-doctor`, work-environment guide | P1 | Eialarasu | ✅ Done | 2026-11-26 |
| `TSK-040` | One-time local setup script (`scripts/setup-local.sh` / `make setup`) — idempotent bootstrap: toolchain check, `.env` defaults, web deps, PocketBase superuser, schema-import hint, seed | P2 | Eialarasu | ✅ Done | 2026-11-26 |
| `TSK-041` | Programmatic PocketBase collection provisioning (`scripts/pb_provision.py` / `make provision`) — API-based, version-robust; replaces fragile schema-JSON import (v0.40 import failed) | P1 | Eialarasu | ✅ Done | 2026-11-26 |
| `TSK-042` | MVP scoping (`RFC-LAB-000-008`, `BK-011`) — MVP definition, minimum RBAC (owner-or-not), phase breakdown M1–M5; `make setup` staleness-guard | P1 | Eialarasu | ✅ Done | 2026-11-26 |
| `TSK-043` | Decision Journal (`docs/DECISION-JOURNAL.md`) — curated decision-narrative log (thinking/rationale showcase); inaugural whole-session entry | P2 | Eialarasu | ✅ Done | 2026-11-28 |
| `TSK-044` | `/brainstorm-save` project skill + AI-collaboration model (`docs/ai-collaboration-model.md`) — decision-capture skill (contributor-attributed) + methodology one-pager; Entry 002 | P2 | Eialarasu | ✅ Done | 2026-11-28 |
| `TSK-025` | Multi-Repository PR Cross-Referencer (`BK-004`) — link sub-project PRs into Cetana journal | P2 | Eialarasu | 📋 Planned | 2026-11-28 |
| `TSK-026` | Option B: Slack / WhatsApp incoming webhook dispatch (`BK-001`) | P2 | Eialarasu | 📋 Planned | 2026-12-03 |

---

## 💡 Prioritized Backlog (Future Sprints)

| Backlog ID | Proposed Initiative / Capability | Priority | Archetype | Target Sprint | Notes |
| :---: | :--- | :---: | :---: | :---: | :--- |
| `BK-005` | PDF Executive Digest Export | P3 | Tooling | Backlog | One-click export for board/investor reporting |
| `BK-006` | Project Health Trend Telemetry | P3 | Analytics | Backlog | Historical velocity and health transition graphs on dashboard |
| `BK-007` | On-Demand Git Status Audit Trail & Role-Gated History | P2 | Governance | SPRINT-07 (scoped) | Role-gated history & audit trail. Auth/RBAC scoped in [`RFC-LAB-000-006`](docs/rfc/RFC-LAB-000-006-auth-rbac.md) (`TSK-037`) — GitHub OAuth, per-project roles via `memberships`, per-collection API rules, access-only audit (non-surveillance). Delivered as BK-008 Phase 3 atop the web app. |
| `BK-008` | Control Hub Web App Evolution (PocketBase, db + server) | P2 | Platform | SPRINT-06 (scoping) | Evolve the static control plane into a full PocketBase web application (database + backend server). Scoped in [`RFC-LAB-000-003`](docs/rfc/RFC-LAB-000-003-pocketbase-web-app.md) (`TSK-031`). Prerequisite for `BK-007` RBAC. Cloud dev env shifts Kiro Web → Codespaces per `RFC-LAB-000-001` §5; services declared in `.devcontainer/`. Consumes the `BK-009` relational data layer as its seed schema. |
| `BK-009` | Relational JSON Data Layer (`RFC-LAB-000-002`) | P1 | Data | ✅ Delivered (SPRINT-05, `TSK-030`) | User & project masters + many-to-many memberships join under `data/`; generated README registry; referential-integrity validator pillar. PocketBase-ready schema; foundation for `BK-008` + `BK-007` RBAC. |
| `BK-011` | Control Hub Web App MVP (`RFC-LAB-000-008`) | P1 | Platform | Scoped (`TSK-042`) | MVP: logged-in user sees live portfolio from PocketBase; **owner edits own project's status**; deployed. **Minimum RBAC** = 3 tiers (public / authenticated / owner via `owner_id`), deferring the full 5-role `memberships` model + audit. Phases M1 (wire UI→PB) → M5 (deploy). Foundation verified: provisioning + seed live on PocketBase v0.40. |

---

## 📦 Delivered Sprints Archive

### Sprint 7: Sleek UI Deployment, Auth Scoping & Kiro-Native DX (2026-09-24)
- **Goal**: Make the Sleek UI publicly visible, scope auth/RBAC, and standardize the developer command experience.
- **Deliverables**:
  - `TSK-036`: Sleek UI deployed to GitHub Pages at `/app` (dual-run with the classic dashboard via a combined-artifact `deploy-pages.yml`) [PR #4].
  - `TSK-037`: BK-008 Phase 3 auth/RBAC scoping (`RFC-LAB-000-006`) — GitHub OAuth, per-project roles via `memberships`, per-collection API rules, non-surveillance safeguards.
  - `TSK-038`: Kiro-native project skillset (Phase A) — migrated to `.kiro/skills/`, added infra/lifecycle/audit `/commands` + `.kiro/steering/` foundation [PR #5]. CI caught & fixed a stale `data/status.json`.
  - Personal skillset (Phase B): drafted `/sign-in`, `/sign-off`, `/session-save`, `/session-resume` for the developer's `~/.kiro/` + Configuration Sync (not committed to the shared repo).
- **Carried Forward**: `TSK-025` (Multi-Repo PR Cross-Referencer) and `TSK-026` (Slack/WhatsApp webhook dispatch) → `SPRINT-08`.

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
