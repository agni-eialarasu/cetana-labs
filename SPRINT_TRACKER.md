# Cetana Labs — Sprint Tracker

The **committed, in-flight work** for **Cetana Labs Control Hub (`LAB-000`)** — the current sprint and the delivered-sprints archive. This is the middle tier of the three-tier tracking funnel defined in [`RFC-LAB-000-010`](docs/rfc/RFC-LAB-000-010-tracking-model.md):

```
BACKLOG.md            SPRINT_TRACKER.md              CHANGELOG.md
(ideas / the shelf)   (committed, in-flight work)    (shipped history)
```

> 💡 **Ideas / future initiatives:** [`BACKLOG.md`](BACKLOG.md) · 📜 **Shipped releases:** [`CHANGELOG.md`](CHANGELOG.md)

## Status vocabulary (= the lifecycle state machine, `RFC-LAB-000-009` §3.1)

| Status | Meaning | Lifecycle state |
| :--- | :--- | :--- |
| `📋 Backlog` | An idea, not yet committed (lives in `BACKLOG.md`) | — (pre-funnel) |
| `✅ Ready` | Committed to a sprint; **Spec merged** to `main` | `READY_TO_BUILD` |
| `🔨 In Progress` | Being implemented (`/spec-run` running / interactive build) | (Build) |
| `🔍 In Verification` | Human functional verification loop | `IN_VERIFICATION` |
| `👀 In Review` | At the human PR gate | `IN_REVIEW` |
| `✅ Done` | Merged + recorded | `RECORDED` |

**Definition of Ready (backlog → sprint gate):** an item is `✅ Ready` only when its Kiro Spec is **authored and merged to `main`** (the merge-first `/plan-done` transition → `READY_TO_BUILD`), per [`RFC-LAB-000-010`](docs/rfc/RFC-LAB-000-010-tracking-model.md) §5. Lead-paired work uses a lighter ready-bar (a scoped tracker row), per progressive formality (`RFC-LAB-000-009` §5).

---

## 🎯 Current Sprint: Sprint 10 — Post-MVP Hardening & First Product Feature

| Property | Value |
| :--- | :--- |
| **Sprint ID** | `SPRINT-10` |
| **Duration** | 2026-12-17 to 2026-12-31 (2 Weeks) |
| **Sprint Goal** | Harden the shipped MVP — resolve the deployed-PocketBase version workaround (`BK-018`) and formalize the production cutover (`BK-019`) — and begin the first post-MVP product capability: app-level settings (`BK-012`) as the foundation for branding/white-label (`BK-013`). Carry-forward ecosystem integrations (`BK-004`, `BK-001`). |
| **Status** | 🟢 Active |
| **Lead** | Eialarasu |

### Sprint Items

| Task ID | Item / Feature | Priority | Assignee | Status | Target Date |
| :---: | :--- | :---: | :---: | :---: | :---: |
| `TSK-055` | `BK-018` **spike** (`spike-bk018-pb040-oauth`) — root-caused the PB 0.40 realtime/OAuth-through-Railway-proxy failure; chose H1 (redirect `authWithOAuth2Code`); finding on `main` (Journal Entry 011, RFC-011 §4.5). Fix authored as `TSK-058` | P1 | Eialarasu | ✅ Done | 2026-09-29 |
| `TSK-058` | `BK-018` **fix** (Spec `fix-bk018-oauth-redirect`) — switch GitHub sign-in to the redirect `authWithOAuth2Code` flow (no `/api/realtime`) + un-pin `Containerfile` PB 0.28.4→0.40+; preserve `github_handle` hook + owner-write; verify on a throwaway 0.40 Railway via RFC-012 CLI + `verify-bundle`. Live prod cutover = separate `BK-019`. **Verified V1–V8 on throwaway 0.40 (REPORT.md); PR #46 open.** | P1 | Eialarasu | 👀 In Review | 2026-12-24 |
| `TSK-056` | `BK-017` + `BK-020` — deploy scaffold (Spec `deploy-scaffold`, implements `RFC-LAB-000-012`): `railway.json`, `make deploy-staging`→`scripts/deploy.sh` (CLI-first), `make verify-bundle` (artifact-assertion helper), `developer-guide` Deploy-Ops runbook (casual→qualified), **+ fix the `status.json` date-drift (`BK-020`)**. Unblocks the deferred BK-018 OAuth fix. `BK-019` (real prod cutover) remains separate | P2 | Eialarasu | ✅ Done | 2026-09-29 |
| `TSK-057` | `BK-012` — app-level settings (RFC + Spec): configurable settings collection + typed accessors, minimal now, grows over time; foundation for `BK-013` branding | P2 | Eialarasu | 📋 Backlog | 2026-12-31 |
| `TSK-025` | Multi-Repository PR Cross-Referencer (`BK-004`) — link sub-project PRs into Cetana journal | P2 | Eialarasu | 📋 Backlog | 2026-12-24 |
| `TSK-026` | Option B: Slack / WhatsApp incoming webhook dispatch (`BK-001`) | P2 | Eialarasu | 📋 Backlog | 2026-12-31 |

---

## 📦 Delivered Sprints Archive

### Sprint 9: MVP Delivery — Auth → RBAC → Owner Writes → Deploy (2026-09-28) — `v0.11.0` · **MVP complete (`BK-011`)**
- **Goal**: Complete the Control Hub Web App MVP via the AIDLC lifecycle — sign-in, minimum RBAC, owner writes, deployed.
- **Deliverables**:
  - `TSK-051`: Three-tier tracking-model refactor (`RFC-LAB-000-010`) — dogfooded via the lifecycle [PR #25].
  - `TSK-052`: Docs reorganization + breadcrumb nav standard (`docs/` grouped) [PR #27].
  - `TSK-049`: **MVP M2** — GitHub OAuth sign-in (auth store, link-by-handle, route guard) [PR #31].
  - `TSK-050`: **MVP M3–M4** — minimum RBAC (PocketBase rules, no library) + owner status write path [PR #34].
  - `TSK-053`: Deployment architecture RFC (`RFC-LAB-000-011`; amended GCP→Railway, Entry 010) [PRs #36].
  - `TSK-054`: **MVP M5** — deployed (SvelteKit → Vercel, PocketBase → Railway); retired the GitHub-Pages stopgap; **MVP complete** [PR #38].
- **Milestone**: **`BK-011` delivered** — a logged-in owner edits their own project status, deployed and usable (`v0.11.0`). 6 AIDLC `/spec-run`s; the human-verification loop caught real bugs pre-merge (M3–M4 owner-rule mismatch; M5 deploy version saga).
- **Deferred/follow-ups**: `BK-016` (terminal-state edit policy), `BK-017` (deploy automation), `BK-018` (latest-PB on Railway), `BK-019` (prod cutover).
- **Carried Forward**: `TSK-025` (`BK-004`) + `TSK-026` (`BK-001`) → `SPRINT-10`.

### Sprint 8: Work-Environment Standardization, AIDLC Sprint Lifecycle & MVP M1 (2026-09-27) — `v0.10.0`
- **Goal**: Standardize the Kiro Web + IDE work-environment, define and tool an AIDLC sprint lifecycle, and deliver the first MVP feature.
- **Deliverables**:
  - `TSK-039`: Work-Environment Standardization (`RFC-LAB-000-007`) — surface roles, `.env.example`, Makefile cheat-sheet, Podman-first Containerfile, `/env-doctor`, `docs/work-environment.md`.
  - `TSK-040`/`TSK-041`: One-command local bootstrap (`make setup`) + programmatic PocketBase provisioning (`scripts/pb_provision.py`), version-robust and idempotent (fixes for v0.40).
  - `TSK-042`: MVP scoping (`RFC-LAB-000-008`, `BK-011`) — MVP definition + minimum RBAC + phase breakdown M1–M5.
  - `TSK-043`/`TSK-044`: Decision Journal (`docs/DECISION-JOURNAL.md`, Entries 001–002) + `/brainstorm-save` skill + `docs/ai-collaboration-model.md`.
  - `TSK-045`: Sprint lifecycle & AIDLC engine (`RFC-LAB-000-009`) — five-phase human-gated lifecycle on Kiro Specs + Autonomous mode; §3.1 state machine; first AIDLC Spec + `docs/sprint-lifecycle.md` [PRs #14, #15, #18, #19, #20].
  - `TSK-046`: Lifecycle command suite — `/spec-run`, `/plan-start`, `/plan-done`, `/review-pr`, state guards; `REPORT.md` template [PRs #16, #17].
  - `TSK-047`: **MVP M1 delivered (`BK-011`)** — Sleek UI wired to live PocketBase via the AIDLC lifecycle [PR #21].
  - `TSK-048`: Human functional-verification loop (`RFC-LAB-000-009` §3.2) — `IN_VERIFICATION` + `/verification-done`; Decision Journal Entries 003–004 [PR #22].
- **Milestone**: First feature (`M1`) delivered end-to-end via the new AIDLC lifecycle; the run itself surfaced and closed the human-verification gap same-cycle.
- **Carried Forward**: `TSK-025` (Multi-Repo PR Cross-Referencer) and `TSK-026` (Slack/WhatsApp webhook dispatch) → `SPRINT-09`.

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
