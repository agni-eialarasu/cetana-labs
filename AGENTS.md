# Cetana Labs — Universal AI Agent Guidelines

You are acting as the technical delivery assistant and documentation maintainer for **`cetana-labs`**.
Your role is to keep this repository structured, well-documented, clean, and up to date.

---

## 1. Core Operating Principles & Strict Constraints

1. **Master Control Plane (Not Monorepo)**:
   - This repo stores project charters, executive statuses (`STATUS.md`), the sprint tracker ([`SPRINT_TRACKER.md`](SPRINT_TRACKER.md) — committed/in-flight work) and idea backlog ([`BACKLOG.md`](BACKLOG.md) — `BK-` ideas), historical releases ([`CHANGELOG.md`](CHANGELOG.md)), and milestone journals. The three-tier tracking funnel is defined in [`RFC-LAB-000-010`](docs/rfc/RFC-LAB-000-010-tracking-model.md).
   - Documentation lives under [`docs/`](docs/README.md), grouped into `guides/` · `reference/` · `governance/` · `rfc/` · `templates/`. Every `docs/**` markdown file MUST open with the **breadcrumb nav standard** documented in [`docs/README.md`](docs/README.md) (`[🏠 Repo](../../README.md) / [📚 Docs](../README.md) / <Category> / **This Doc**`).
   - For coding projects (mini-apps), the actual source code and operational runbooks live in external Git repositories. Never clone full application source trees directly into this repo.
2. **Strict Portability (No Absolute Local Paths)**:
   - Never write machine-specific absolute paths (e.g. `/Users/...` or `C:\...`) into project documentation.
   - Use relative repository links, GitHub URLs, or generic commands (e.g. `cd <project-folder>`).
3. **Mandatory `STATUS.md` Protocol**:
   - Every project MUST maintain a lightweight, 30-line `STATUS.md` conforming to [`docs/reference/project-protocol.md`](docs/reference/project-protocol.md).
   - Used by `scripts/generate_status.py` to generate instant, WhatsApp-compatible executive broadcasts via `/project-status`.
4. **Flat Directory & Sequential ID Scheme**:
   - Central control hub is indexed as system kernel **`LAB-000`** (`projects/LAB-000-cetana-labs/`).
   - All other projects reside in `projects/LAB-XXX-<slug>/`.
   - `XXX` is a zero-padded sequential 3-digit number (e.g. `LAB-001`, `LAB-002`, `LAB-003`, `LAB-004`, `LAB-005`).
   - `<slug>` is lowercase, hyphen-separated, alphanumeric without spaces.
5. **Synchronized Master Registry & Backlog (PocketBase as Source of Truth)**:
   - PocketBase is the authoritative live master for project metadata; `data/*.json` is the committed export snapshot (`RFC-LAB-000-016` Phase 3).
   - Project metadata creation/updates occur in-app (`admin/projects` CRUD) → followed by `just export-live-data` (export PB → `data/`) and `python3 scripts/generate_registry.py` (export → README). Whenever project health changes, the master table in [README.md](README.md) is regenerated from the export snapshot.
   - When a sprint task is completed, update [`SPRINT_TRACKER.md`](SPRINT_TRACKER.md) (sprint state) and [`CHANGELOG.md`](CHANGELOG.md); [`BACKLOG.md`](BACKLOG.md) holds only `BK-` ideas.
6. **Branch-Based Development (Hybrid Path-Scoped)** — see [`RFC-LAB-000-004`](docs/rfc/RFC-LAB-000-004-branching-model.md):
   - **Application code, migrations, and `data/`** (committed PocketBase exports / schemas) MUST land via a **pull request** on a short-lived `feat/`|`fix/`|`chore/`|`refactor/` branch, with **green CI** (portfolio validator + `/project-validate` 5-pillar gate + registry `--check`) before **squash-merge** into protected `main`.
   - **Governance / documentation** (`STATUS.md`, `journal.md`, `SPRINT_TRACKER.md`, `BACKLOG.md`, `CHANGELOG.md`, `README.md`, `docs/**`) MAY still fast-path directly to `main`; automated skills (`/project-update`, `/sprint-done`, `/ping-leads`, `log-milestone`) retain their direct-commit path.
   - Branch naming: `<type>/<scope>-<slug>` (type mirrors the commit prefixes below). Delete branches after merge; never force-push `main`; roll back via revert PR.
   - In this environment, open PRs via `gh api repos/{owner}/{repo}/pulls` (REST), not `gh pr create`.
   - Tag `vX.Y.0` releases on `main` at each `/sprint-done`.
7. **Task Runner & Cross-Repo Standard (`just`)**:
   - Standardized on **`just`** (`justfile`) as the task runner across Agni repos (Director decision: one shared command vocabulary across Nexus Pulse and Cetana Labs). Run `just` or `just --list` for all recipes.
   - Leads with the 7 shared-core recipes (`start-local`, `stop-local`, `status-local`, `validate-local`, `validate-staging`, `clean-data`, `help` → `just --list`), with identical names across repos. Cetana-specific extras live below the core.
   - `Makefile` is retained as a thin forwarding shim for one sprint (`make <target>` forwards to `just <target>`), reversible via `git revert`.

---

## 2. Commit Message Conventions

When making commits on behalf of the user, use structured prefixes:
- **New Project**: `feat(lab-XXX): init <project-name>`
- **Milestone / Journal**: `log(lab-XXX): <milestone summary>`
- **Executive Status**: `status(lab-XXX): <summary of health/win update>`
- **Project Metadata**: `chore(lab-XXX): update <attribute>`
- **Governance / Sprint**: `feat(governance): <summary>`
- **Docs & Protocol**: `docs: <summary>` or `chore: <summary>`

---

## 3. Supported Project Archetypes & Templates

When scaffolding a new project, use the corresponding template from `templates/` *(note: templates are retained for structural reference; project registration and metadata creation is now app-side via `admin/projects` CRUD, with template cleanup flagged as a Phase-3 follow-up candidate)*:

| Archetype | Icon | Template Path | Remote Codebase |
| :--- | :---: | :--- | :--- |
| **Control Plane** | 💻 | `projects/LAB-000-cetana-labs/` | System Hub & Protocol Engine |
| **Mini-App / Coding** | 💻 | `templates/mini-app/` | External GitHub URL in README |
| **Research / Spike** | 📑 | `templates/research/` | Self-contained or paper links |
| **Data Collection** | 📊 | `templates/data-collection/` | Pipeline scripts/links & schemas |
| **Verification / Benchmark** | 🔬 | `templates/verification/` | Test harnesses & benchmark logs |

---

## 4. Reusable AI Agent Skills Suite (`.kiro/skills/`)

All project `/commands` live in **`.kiro/skills/<name>/SKILL.md`**, committed to the repo — one file, one location. This is the Kiro-native location, and **the "skill hook" is the mechanism by which that single committed file becomes a live `/command` on every surface**:
- **Kiro IDE** and **Kiro Web** read `.kiro/` natively → the skill is an invokable `/command`.
- **Google Antigravity** reads the repo copy in-tree → the skill is available to the primary executor.
- **KiroCrew** symlinks `~/.kiro/crew/skills/cetana-labs → <repo>/.kiro/skills` (machine-local) → the Operator sees the same skills.

**One file, four surfaces, zero duplication.**

> [!IMPORTANT]
> **One skill, one file, one location.** Do NOT duplicate skills into `.agents/skills/` or `.gemini/skills/` (the pre-AIDLC layout — now retired); `.agents/skills/README.md` is a redirect-only stub. Cetana Labs is the canonical source of this convention (`RFC-LAB-000-009`), adopted cross-repo by Nexus Pulse.

**Committed vs machine-local boundary:** everything under `.kiro/` is committed **except** `.kiro/settings/` (gitignored — CLI runtime state). Personal commands (`/sign-in`, `/sign-off`, `/session-save`, `/session-resume`) live in the developer's own `~/.kiro/skills/` and sync via Configuration Sync — they are never committed here.

(Surface roles — Operator / Antigravity primary executor / Kiro IDE escalation / Kiro Web fallback — are defined in [`RFC-LAB-000-007`](docs/rfc/RFC-LAB-000-007-work-environment.md) and [`ai-collaboration-model.md`](docs/governance/ai-collaboration-model.md).)

**Project lifecycle & governance:**
- **`/project-validate [ID]`**: Pre-flight 5-pillar audit (scraper budget ≤ 35 lines, registry lockstep, git hygiene, AST boundaries, live test count) emitting `.gemini/governance/validation_receipt.json`.
- **`/project-status [ID]`**: WhatsApp briefings via `scripts/generate_status.py` (filters completed initiatives and `LAB-000`).
- **App-Side Metadata Management (`admin/projects`)**: Projects are created and edited in the web application (`admin/projects` CRUD) → `just export-live-data` reconciles live PocketBase to committed `data/*.json` → `python3 scripts/generate_registry.py` updates the README master registry. (Replaces retired `/project-add` and `/project-edit` skills; the 5 executive/governance skills `/project-validate`, `/project-status`, `/project-update`, `/audit-doc`, `/audit-project` remain active.)
- **`/project-update <ID>`**: Updates `STATUS.md`, prepends wins, appends a `journal.md` milestone.
**Sprint lifecycle (`RFC-LAB-000-009`) — `brainstorm → implement → verify → done`, phase-aware (order is the contract):**
- **`/sprint-start [goal]`** / **`/sprint-done [sprint_id]`**: Open / close the **sprint container** in `SPRINT_TRACKER.md` (id, window, goal, carry-forward) and sync `STATUS.md` / `CHANGELOG.md`. *(Web — Scope/Record.)* A sprint **contains many plans**. `/sprint-done` refuses to close undelivered (still-in-review) work.
- **`/plan-start [topic]`** *(optional, implicit — any free-form topic is a plan-start)* / **`/plan-done`**: Open / close a **planning session** within a sprint (brainstorm, backlog prep, RFC/doc, author a Spec). `/plan-done` finalizes and **merges the Spec** to `main` as a doc PR (the merge-first rule) → state `READY_TO_BUILD`. *(Web — Scope.)*
- **`/spec-run <spec-id>`**: **IDE one-liner** — the *implement* phase. You supply only the spec id; it owns all repeatable steps (syncs `main`, silent preflight, self-creates the branch the Spec names), executes `tasks.md`, self-validates against the `requirements.md` EARS DoD, opens a PR — then STOP-and-holds. **Never merges.** Requires the Spec merged to `main` (merge-first).
- **`/review-pr [PR]`**: The human PR gate (*verify*) — surfaces CI, diff scope/hygiene, the Spec's EARS DoD per-criterion, and governance lockstep as a checklist, then STOP-and-holds. Never merges or auto-approves.
- **State guards:** every lifecycle command is phase-aware — redundant/already-done ⇒ skip + continue; missing prerequisite or gate ⇒ alert + HOLD (never silently bypass a gate).
- **`/ping-leads`**: Idempotent GitHub issue alerts for stale (> 14 days) / onboarding-pending initiatives (excludes `LAB-000` and completed).
- **`/audit-doc <file>`** / **`/audit-project [ID]`**: Single-file doc review / whole-project (or portfolio) health sweep.
- **`log-milestone`** / **`commit-changes`**: Append journal milestones / standardized commits.
- **`/push-changes`** / **`/commit-and-push-changes`**: Push the **current branch** by explicit name (branch-aware per `RFC-LAB-000-004` — refuses code/`data/`/migration pushes to `main`, validates docs fast-path and hands the human the `main` push, never force-pushes) / commit (via `/commit-changes`) **then** push through that same gate, in one invocation.

**Local & staging infra (task runner: `just`):**
- **`/start-local`** / **`/stop-local`** / **`/status-local`**: Bring up / shut down / inspect the local dev stack (PocketBase `:8090` + SvelteKit `:5173`) via `just start-local` / `just stop-local` / `just status-local`.
- **`/validate-local`**: Full local pre-flight (`just validate-local`) — Python governance validators + SvelteKit type-check/build (mirrors CI).
- **`/status-staging`** / **`/validate-staging`**: Staging probes (`just validate-staging`) — Railway backend + Vercel frontend.

---

## 5. Health Status Legend
- `⏳ Onboarding Pending` — Project registered; awaiting initial `STATUS.md` commit from lead.
- `🟢 On Track` — Milestones progressing smoothly as planned.
- `🟡 At Risk` — Minor delays or dependencies pending; no escalation yet.
- `🔴 Blocked` — Hard blocker requiring management intervention.
- `⏸️ Paused` — Intentionally on hold.
- `✅ Completed` — Finished, operationalized, or successfully verified.

---

## 6. Two-Phase Governance Contract

To prevent metric drift, eliminate hallucinated test numbers, and guarantee scraper stability:

```text
[ /project-validate ]  ──(If GREEN: emits validation_receipt.json)──>  [ /project-status ]
(Automated Pre-Flight Gate)                                            (Scraper Publish & Broadcast)
```

1. **Mandatory Pre-Flight**: Never emit executive status updates without running `/project-validate`.
2. **Deterministic Receipt**: `/project-validate` audits the 5 core pillars and generates `.gemini/governance/validation_receipt.json`.
3. **Scraper Budget**: Root `STATUS.md` must strictly remain `<= 35 lines` to ensure 100% reliability for the daily 9:30 AM IST automated scraper.
