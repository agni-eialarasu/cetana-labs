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

### [2026-09-24] Milestone: BK-008 Phase 2 Build — Sleek UI (`TSK-035`)
- **Context**: First application build under the branch-based model — the SvelteKit "Sleek UI" reaching read-only parity with the static dashboard, styled by the org design system.
- **Key Deliverables**:
  - Scaffolded `app/web/` — **SvelteKit 5 (Runes) + pnpm + Tailwind + adapter-static**, PocketBase JS SDK, IBM Plex via `@fontsource`.
  - Wired the **Nexus Pulse `--np-*` tokens** (light/dark), Tailwind token map, and a dark-first System/Light/Dark theme toggle; responsive sm/md/lg.
  - Read-parity dashboard: header, KPI bar, filter tabs, 3 sort modes, live search, owner-first project cards (owner pill, health pill, blocker banner) — merging structural `data/` + interim `data/status.json`.
  - Added `scripts/generate_status_json.py` (reuses `generate_status.py` parser) and a Node `web-build` CI job; both `status.json --check` and the SvelteKit build now gate PRs.
  - Verified: `svelte-check` 0 errors/0 warnings; static build succeeds; all Python validators green.
- **Next Horizon**: Land via PR; then Phase 3 (auth + RBAC / `BK-007`) or wire the SPA to a live PocketBase instance.

---

### [2026-09-24] Milestone: Phase 2 Design Decisions & Org Design System Adopted
- **Context**: Resolved the four `RFC-LAB-000-005` open questions and brought the org design system into the repo ahead of the Phase 2 build.
- **Decisions**:
  - **Q1 Live status** → interim `data/status.json` export (reuse `generate_status.py` parser; `STATUS.md` stays canonical until Phase 4).
  - **Q2 Hosting** → split hosting: SvelteKit static UI on GitHub Pages + PocketBase on a container host with a persistent SQLite volume.
  - **Q3 Framework** → **Svelte 5 (Runes) + pnpm**.
  - **Q4 Styling** → adopt the org **Nexus Pulse Design System** (Tailwind-based).
- **Key Deliverables**:
  - Stored the org design system verbatim at `docs/DESIGN.md` (authoritative visual SoT).
  - Authored `docs/design-system-lab000.md` mapping it to SvelteKit + Tailwind — token/framework split, IBM Plex via `@fontsource`, `--np-*` Tailwind token map, sm/md/lg responsive tiers, and LAB-000-specific IA (not Nexus Pulse's nav).
  - Marked `RFC-LAB-000-005` Accepted with resolutions recorded.
- **Next Horizon**: Build Phase 2 on a `feat/` branch via PR — scaffold `app/web/` (SvelteKit 5 + pnpm + Tailwind), wire tokens/fonts, port components to read-parity.

---

### [2026-09-24] Milestone: BK-008 Phase 2 Scoping — Sleek UI (`RFC-LAB-000-005` / `TSK-034`)
- **Context**: Scoped the Phase 2 frontend — a "Sleek UI" SPA reaching read-only feature parity with `docs/index.html`, driven by the Phase 1 PocketBase backend.
- **Key Deliverables**:
  - Authored [`RFC-LAB-000-005`](../../docs/rfc/RFC-LAB-000-005-web-app-phase2-ui.md).
  - **Framework decision: SvelteKit static-SPA** (`adapter-static`, `ssr=false`) consuming the PocketBase JS SDK **client-side** — aligns with PocketBase's SPA-first guidance and keeps the cheap-static-artifact property (deployable to `pb_public/` or GitHub Pages during dual-run).
  - Defined the read-parity checklist (KPIs, filters, sort, search, owner-pill cards, theme toggle), deploy/dual-run story, and phased build steps.
  - Registered `TSK-034` (Done); marked `TSK-033` (P1) done.
- **Next Horizon**: Build Phase 2 on a `feat/` branch via PR — scaffold `app/web/`, wire the PB read client, port components to parity.

---

### [2026-09-24] Milestone: BK-008 Phase 1 — PocketBase Backend Scaffolding (`TSK-033`)
- **Context**: First implementation phase of the PocketBase web app (`RFC-LAB-000-003` P1), delivered on a `feat/` branch via PR under the new branch-based model.
- **Key Deliverables**:
  - `app/pocketbase/pb_schema.json` — PocketBase collections (`users` auth, `projects`, `memberships`) generated from the `data/` masters by `scripts/generate_pb_schema.py`; owner/membership FKs become native relation fields.
  - `scripts/pb_import.py` — idempotent, stdlib-only seed importer (dry-run default; `--apply` upserts by natural `seed_id`/`lab_id`) mapping `data/` → PocketBase records.
  - `.devcontainer/setup-pocketbase.sh` + port 8090 forwarding — provisions PocketBase in Codespaces (best-effort; not required in the Kiro Web sandbox).
  - CI now enforces `generate_pb_schema.py --check` so the backend schema stays derived from `data/`; `pb_data/` + binary gitignored.
- **Next Horizon**: Run the server in Codespaces, apply the import, then Phase 2 (read-UI parity).

---

### [2026-09-24] Milestone: Adopted Branch-Based Development (`RFC-LAB-000-004`)
- **Context**: With `BK-008` introducing runnable code, a database, and migrations, trunk-based direct commits are no longer appropriate for application changes. Moved to industry-standard branch-based development ahead of P1.
- **Key Deliverables**:
  - Authored [`RFC-LAB-000-004`](../../docs/rfc/RFC-LAB-000-004-branching-model.md) — GitHub Flow, protected `main`, short-lived feature branches, squash-merge, hybrid path-scoping (app code/`data/`/migrations → PR; governance/docs → fast-path).
  - Added `pull_request` CI workflow (`.github/workflows/ci-validate.yml`) running the portfolio validator, registry `--check`, and the 5-pillar gate as required status checks, plus a PR template.
  - Updated `AGENTS.md` §1.6 from trunk-based to the hybrid branch model.
  - **Dogfooded**: this change was landed as the repository's first pull request.
- **Next Horizon**: Enable branch protection on `main`; begin `BK-008` Phase 1 (PocketBase stand-up + `data/` importer) on a `feat/` branch via PR.

---

### [2026-09-24] Milestone: Sprint 5 Closeout & v0.7.0 Release
- **Context**: Executed formal sprint closeout (`/sprint-done`) for Sprint 5.
- **Delivered Capabilities**:
  - `TSK-030`: Relational JSON Data Layer (`BK-009`) — user & project masters, many-to-many memberships join, generated README registry, referential-integrity validator pillar, and PocketBase-ready JSON Schemas.
- **Release**: Promoted CHANGELOG to `v0.7.0`; synchronized root & `LAB-000` `STATUS.md`.
- **Next Horizon**: Initialized `SPRINT-06` (2026-10-22 → 2026-11-05). Added `TSK-031` to scope the PocketBase Control Hub web app (`BK-008`, `RFC-LAB-000-003`) atop the new data layer; carried forward `TSK-025` (Multi-Repo PR Cross-Referencer) and `TSK-026` (Slack/WhatsApp webhook dispatch).

---

### [2026-09-24] Milestone: Relational JSON Data Layer (`BK-009` / `RFC-LAB-000-002`)
- **Context**: Portfolio metadata was fragmented across Markdown (per-project READMEs, STATUS.md, and a hand-maintained root registry table) and owner identity was free text. Introduced a relational `data/` layer as the structural source of truth and the seed schema for the future PocketBase web app (`BK-008`) and RBAC (`BK-007`).
- **Key Deliverables**:
  - Authored [`RFC-LAB-000-002`](../../docs/rfc/RFC-LAB-000-002-relational-data-model.md) — Option A model (JSON = structural source of truth; `STATUS.md` = live status; README table generated).
  - Created `data/users.json` (user master), `data/portfolio.json` (project master, 1:1 `owner_id`), and `data/memberships.json` (many-to-many join with roles) + Draft-07 JSON Schemas mapped to PocketBase field types.
  - Added `scripts/generate_registry.py` to render the README master table from `data/` (marker-delimited, `--check` staleness gate) and `scripts/portfolio_data.py` shared accessor.
  - Wired `generate_dashboard.py` / `generate_status.py` to prefer the `data/` layer (owner names now resolve from the user master; the `.ai` TLD regex bug is moot).
  - Added a referential-integrity validator pillar (owner_id resolution, dir↔record lockstep, membership FKs, STATUS name-drift) — verified it catches orphaned FKs.
  - Registered `TSK-030` (Done) in `SPRINT-05` and `BK-009` (Delivered) in the backlog; synchronized `CHANGELOG.md`.

---

### [2026-09-24] Milestone: Sprint 4 Closeout & v0.6.0 Release
- **Context**: Executed formal sprint closeout (`/sprint-done`) for Sprint 4. Fixed a duplicate `TSK-027` ID (split into `TSK-027` Two-Phase Governance and `TSK-028` Cloud Migration) and captured the dashboard restructure as `TSK-029` prior to archiving.
- **Delivered Capabilities**:
  - `TSK-024`: Automated Lead Ping Engine (`BK-003`) — `scripts/ping_leads.py`, weekly `lead-ping-cron.yml`, `/ping-leads` skill; idempotent stale/onboarding GitHub issue alerts (excludes `LAB-000` & completed).
  - `TSK-027`: Two-Phase Governance Contract — `/project-validate` 5-pillar pre-flight gate with immutable `validation_receipt.json`.
  - `TSK-028`: Cloud Dev Migration (`RFC-LAB-000-001`) — Kiro Web primary env, `Dev Environment` protocol field, cloud dev guide, reproducible `.devcontainer/`.
  - `TSK-029`: Owner-first dashboard cards — surfaced project owner, made Project ID internal.
- **Release**: Promoted CHANGELOG to `v0.6.0`; synchronized root & `LAB-000` `STATUS.md`.
- **Next Horizon**: Initialized `SPRINT-05` (2026-10-08 → 2026-10-22) carrying forward `TSK-025` (Multi-Repo PR Cross-Referencer, `BK-004`) and `TSK-026` (Slack/WhatsApp webhook dispatch, `BK-001`).

---

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
