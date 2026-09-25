# Changelog

All notable changes to **Cetana Labs Control Hub (`LAB-000`)** and master management plane will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]
### Added
- **Sleek UI GitHub Pages Deployment (`TSK-036`)**: Extended `deploy-pages.yml` to build the SvelteKit Sleek UI (with a `/cetana-labs/app` base path) and publish a **single combined site artifact** — the classic static dashboard at root (`/`) and the Sleek UI at `/app/` — enabling dual-run per `RFC-LAB-000-005` §6 (one Pages deployment, no race). Added cross-links: an "✨ Open Sleek UI (beta)" action on the classic dashboard and a "← Classic dashboard" link in the app footer.
### Changed
### Fixed

---

## [0.8.0] - 2026-09-24
### Added
- **BK-008 Phase 2 Build — Sleek UI (`TSK-035`)**: Built the SvelteKit 5 + pnpm + Tailwind static SPA under `app/web/`, styled with the Nexus Pulse design tokens (blue accent, IBM Plex Sans/Mono, dark-first theme toggle) and responsive across small/medium/large. Reaches read-parity with the static dashboard — KPI bar, filter tabs, Executive-Priority/Recent/ID sort, live search, and owner-first project cards (owner pill, health pill, blocker banner) — driven by the bundled `data/` snapshot. Added `scripts/generate_status_json.py` (interim live-status export → `data/status.json`, reusing the authoritative parser) and a Node `web-build` CI job (pnpm install + type-check + static build); wired `generate_status_json.py --check` into CI.
- **BK-008 Phase 2 Scoping — Sleek UI (`RFC-LAB-000-005`, `TSK-034`)**: Scoped the read-parity frontend — decided on **SvelteKit in static-SPA mode** consuming the PocketBase JS SDK client-side (per PocketBase's own SPA-first guidance), served from `pb_public/` with GitHub Pages dual-run. Includes the architecture, a read-parity checklist against `docs/index.html`, deploy plan, and phased build steps. **Open questions resolved:** interim `data/status.json` live-status source; split hosting (Pages UI + container PocketBase); **Svelte 5 (Runes) + pnpm**; and adoption of the org **Nexus Pulse Design System**.
- **Design System Adoption**: Added the org design system verbatim at [`docs/DESIGN.md`](docs/DESIGN.md) (authoritative visual source of truth — blue accent, IBM Plex Sans/Mono, dark-first, `--np-*` tokens) plus [`docs/design-system-lab000.md`](docs/design-system-lab000.md) mapping it to the SvelteKit + Tailwind stack with sm/md/lg responsive targets and a token/framework split.
- **BK-008 Phase 1 — PocketBase Backend Scaffolding (`TSK-033`)**: Added the `app/pocketbase/` backend scaffold with a PocketBase collections schema (`pb_schema.json`) generated from the `data/` masters (`scripts/generate_pb_schema.py`), an idempotent seed importer (`scripts/pb_import.py`, dry-run by default) that maps `data/` → `users`/`projects`/`memberships` records via the PocketBase REST API, a devcontainer PocketBase service (`.devcontainer/setup-pocketbase.sh` + port 8090), and a P1 runbook. Wired `generate_pb_schema.py --check` into CI so the backend schema stays derived from `data/`.
- **Branch-Based Development Model (`RFC-LAB-000-004`)**: Adopted GitHub Flow with a hybrid, path-scoped policy — application code, migrations, and `data/` land via pull requests with green CI and squash-merge into protected `main`, while governance/docs retain their fast path. Added a `pull_request`-triggered CI workflow (`.github/workflows/ci-validate.yml`) running the portfolio validator, registry `--check`, and the 5-pillar gate as required status checks, plus a PR template. Updated `AGENTS.md` §1.6.
- **Web App Evolution Scoping (`BK-008`, `RFC-LAB-000-003`, `TSK-031`)**: Authored the scoping RFC for evolving `LAB-000` into a full **PocketBase** web application (single Go binary + embedded SQLite) atop the `BK-009` relational data layer — covering collection mapping (`users`/`projects`/`memberships`/`status_snapshots`/`sprints`), auth & RBAC via per-collection API rules (seeding `BK-007`), a file→DB migration strategy with `data/` export-on-write, and a phased P0–P5 delivery plan.
### Changed
### Fixed

---

## [0.7.0] - 2026-09-24
### Added
- **Relational JSON Data Layer (`BK-009`, `RFC-LAB-000-002`, `TSK-030`)**: Introduced a `data/` relational layer as the source of truth for structural portfolio metadata — `users.json` (user master), `portfolio.json` (project master with 1:1 `owner_id`), and `memberships.json` (many-to-many user↔project join with roles), each with a Draft-07 JSON Schema authored to PocketBase field types.
- **Generated Master Registry**: Added `scripts/generate_registry.py`, which renders the root `README.md` registry table from `data/` (owner resolved via the user master, live health from `STATUS.md`) inside `<!-- BEGIN:registry -->` / `<!-- END:registry -->` markers. The table is no longer hand-maintained; `--check` mode gates staleness.
- **Referential-Integrity Validator Pillar**: Extended `scripts/validate_portfolio.py` to enforce `owner_id` resolution, `data/`↔`projects/` directory lockstep, membership FK resolution (incl. a matching `owner` membership per project), and `STATUS.md` owner-name drift detection.
- **Shared Data Accessor**: Added `scripts/portfolio_data.py` and wired `generate_dashboard.py` / `generate_status.py` to prefer the structured `data/` layer for archetype, repo URL, and owner (with Markdown fallback), eliminating a class of regex-parsing fragility.
### Changed
### Fixed

---

## [0.6.0] - 2026-09-24
### Added
- **Two-Phase Governance Contract (`/project-validate`, `TSK-027`)**: Implemented pre-flight programmatic verification engine (`scripts/project_validate.py`) enforcing the 5 core verification pillars: Scraper Budget (<= 35 lines), Multi-Registry Lockstep, Git Hygiene, Architectural Boundaries/Portability, and Live Test Auto-Count.
- **Cryptographic Audit Receipt**: Automatically emits `.gemini/governance/validation_receipt.json` certifying verified metrics before `/project-status` or `/status-update` emission.
- **AI Agent Skill (`.agents/skills/project-validate/SKILL.md`)**: Registered `/project-validate` across all Cetana Labs agent environments and documented in `AGENTS.md`, `docs/project-protocol.md`, and `docs/project-owner-guide.md`.
- **Cloud-Based Development Migration (`RFC-LAB-000-001`, `TSK-028`)**: Ratified the decision to develop `LAB-000` entirely in the cloud (primary: **Kiro Web**; fallback: GitHub Codespaces), freeing the local machine for the stateful fullstack initiative. Authored the RFC under a new `docs/rfc/` convention.
- **Environment Classification Protocol**: Added a first-class `Dev Environment` field to the `STATUS.md` schema (`docs/project-protocol.md` §4a) and a `Dev Env` column to the master registry, plus a reusable ☁️ Cloud vs 💻 Local classification heuristic.
- **Cloud Dev Onboarding Runbook**: Published `docs/cloud-dev-guide.md` covering the Kiro Web workflow, dashboard preview, and verification checklist.
- **Reproducible Dev Container**: Added `.devcontainer/` (Python 3.11 + GitHub CLI) for reproducible cloud environments and forward compatibility with the planned web-app (db + server) + RBAC evolution.
- **Backlog Registration**: Registered `BK-008` (Control Hub Web App Evolution — db + server), the prerequisite platform for `BK-007` RBAC.
- **Automated Lead Ping Engine (`BK-003`, `TSK-024`)**: Built `scripts/ping_leads.py` to scan portfolio `STATUS.md` files and generate idempotent GitHub issue alerts for stale (> 14 days) and onboarding-pending initiatives (excludes `LAB-000` and completed projects). Supports dry-run, `--json`, and live `--create-issues` modes with duplicate-safe issue routing to each sub-project repo.
- **Lead Ping Cadence Workflow**: Added `.github/workflows/lead-ping-cron.yml` running a weekly Monday 10:00 AM IST scan plus `workflow_dispatch` (dry-run by default), and registered the `/ping-leads` AI agent skill (`.agents/skills/ping-leads/SKILL.md`, `AGENTS.md`).

### Changed
- **Dashboard Card Restructure — Owner-First Identity (`TSK-029`)**: Replaced the top-left internal Project ID badge on each dashboard card with a prominent **owner-name pill** (`👤 Lead`), surfacing accountability at a glance for executive viewers. Removed the now-duplicate lead line from the card meta row (archetype only). The Project ID is retained internally (search, sort, and hover tooltip) but no longer clutters the card face; empty/generic leads render a `— Unassigned` pill.
### Fixed

---

## [0.5.0] - 2026-09-24
### Added
- **Portfolio Web Dashboard (`BK-002`)**: Built standalone generator (`scripts/generate_dashboard.py`) creating an interactive executive dashboard (`docs/index.html`) with real-time text search, status filtering, and 1-click WhatsApp briefings.
- **Automated GitHub Pages Deployment**: Configured `.github/workflows/deploy-pages.yml` to automatically build and host the dashboard on GitHub Pages on every push to `main` (hosted live at `https://agni-eialarasu.github.io/cetana-labs/`).
- **Executive Blocker Alerting & Highlighting**: Surface Section 4 blockers directly in the dashboard UI with crimson alert cards, pulsating card borders (`has-blocker`), and dedicated top KPI metric ("Hard Blockers") with 1-click filter.
- **Executive Attention Sorting**: Implemented multi-tier attention-priority ordering (Blocked/At Risk ➔ Active Products ➔ Pending Onboarding ➔ Completed ➔ Control Plane) with interactive Sort dropdown (Executive Priority, Recently Updated, Project ID).
- **Default Active Products Landing**: Set default dashboard view to "Active Products" tab so management immediately sees in-flight deliverables without historical noise.
- **1-Click On-board Prompt in Dashboard**: Embedded dynamic, project-specific AI setup prompts directly into each project card. Project leads on `⏳ Onboarding Pending` cards can click "🚀 Copy On-board Prompt" for a complete, pre-filled prompt containing their exact project ID, lead, title, and protocol requirements ready to paste into Cursor/Claude Code/Copilot.
- **System / Light / Dark Theme Support**: Added adaptive UI theme toggle defaulting to the host OS color scheme with persistent user preference storage.

---

## [0.4.0] - 2026-09-23
### Added
- **Remote `STATUS.md` Auto-Fetcher**: Added `--sync-remote` flag to `scripts/generate_status.py` using `gh api` and raw GitHub fallbacks to automatically fetch the latest `STATUS.md` committed by project leads.
- **CI Linter & Portfolio Integrity Validator**: Created `scripts/validate_portfolio.py` to enforce strict directory naming, required documentation files, health badges, and master README sync.
- **Automated Sprint Closeout Skill**: Authored `/sprint-done` skill playbook (`.agents/skills/sprint-done/SKILL.md`) for 1-click sprint archiving and changelog bumping.

### Changed
- **Compacted Project ID Sequence**: Reindexed `LAB-005` (Zerobea.ai) $\rightarrow$ `LAB-004` and `LAB-006` (Nexus Beacon) $\rightarrow$ `LAB-005` to maintain a continuous, contiguous ID sequence (`LAB-000` through `LAB-005`).
- **Moved to Backlog**: Moved Option B webhook dispatch to future sprint backlog (`BK-001`).

---

## [0.3.0] - 2026-09-23
### Added
- **Constructive Visibility Protocol**: Implemented `⏳ Onboarding Pending` alert to hold project leads accountable for running `/status-init`.\n- **Sprint Cadence Staleness Tracking**: Automated 14-day staleness detection in `scripts/generate_status.py` to maintain bi-weekly update discipline.
- **Bare-Minimum Sprint Tracking**: Introduced root `BACKLOG.md` and `CHANGELOG.md` to maintain planned sprint items, prioritized backlogs, and historical releases.
- **New Initiatives Onboarded**: Registered `LAB-004` (Zerobea.ai) and `LAB-005` (Nexus Beacon) into the portfolio.

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
