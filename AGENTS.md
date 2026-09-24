# Cetana Labs — Universal AI Agent Guidelines

You are acting as the technical delivery assistant and documentation maintainer for **`cetana-labs`**.
Your role is to keep this repository structured, well-documented, clean, and up to date.

---

## 1. Core Operating Principles & Strict Constraints

1. **Master Control Plane (Not Monorepo)**:
   - This repo stores project charters, executive statuses (`STATUS.md`), sprint backlogs ([`BACKLOG.md`](BACKLOG.md)), historical releases ([`CHANGELOG.md`](CHANGELOG.md)), and milestone journals.
   - For coding projects (mini-apps), the actual source code and operational runbooks live in external Git repositories. Never clone full application source trees directly into this repo.
2. **Strict Portability (No Absolute Local Paths)**:
   - Never write machine-specific absolute paths (e.g. `/Users/...` or `C:\...`) into project documentation.
   - Use relative repository links, GitHub URLs, or generic commands (e.g. `cd <project-folder>`).
3. **Mandatory `STATUS.md` Protocol**:
   - Every project MUST maintain a lightweight, 30-line `STATUS.md` conforming to [`docs/project-protocol.md`](docs/project-protocol.md).
   - Used by `scripts/generate_status.py` to generate instant, WhatsApp-compatible executive broadcasts via `/project-status`.
4. **Flat Directory & Sequential ID Scheme**:
   - Central control hub is indexed as system kernel **`LAB-000`** (`projects/LAB-000-cetana-labs/`).
   - All other projects reside in `projects/LAB-XXX-<slug>/`.
   - `XXX` is a zero-padded sequential 3-digit number (e.g. `LAB-001`, `LAB-002`, `LAB-003`, `LAB-004`, `LAB-005`).
   - `<slug>` is lowercase, hyphen-separated, alphanumeric without spaces.
5. **Synchronized Master Registry & Backlog**:
   - Whenever a project is created, edited, or changes health, the table in [README.md](README.md) MUST be updated immediately.
   - When a sprint task is completed, update [`BACKLOG.md`](BACKLOG.md) and [`CHANGELOG.md`](CHANGELOG.md).
6. **Trunk-Based Direct Commits (`main` only)**:
   - No branching or PRs required.
   - Commit directly to `main` using standardized commit message conventions.

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

When scaffolding a new project, use the corresponding template from `templates/`:

| Archetype | Icon | Template Path | Remote Codebase |
| :--- | :---: | :--- | :--- |
| **Control Plane** | 💻 | `projects/LAB-000-cetana-labs/` | System Hub & Protocol Engine |
| **Mini-App / Coding** | 💻 | `templates/mini-app/` | External GitHub URL in README |
| **Research / Spike** | 📑 | `templates/research/` | Self-contained or paper links |
| **Data Collection** | 📊 | `templates/data-collection/` | Pipeline scripts/links & schemas |
| **Verification / Benchmark** | 🔬 | `templates/verification/` | Test harnesses & benchmark logs |

---

## 4. Reusable AI Agent Skills Suite (`.agents/skills/`)

For detailed step-by-step procedures, refer to `.agents/skills/`:
- **`/project-validate [ID]`**: Pre-flight verification gate running a 5-pillar audit (scraper budget <= 35 lines, registry lockstep, git hygiene, AST boundaries, live test count) emitting `.gemini/governance/validation_receipt.json`.
- **`/project-status [ID]`**: Generates WhatsApp briefings via `scripts/generate_status.py` (filters out completed initiatives and `LAB-000`).
- **`/project-add <url_or_title>`**: Scaffolds next project ID, inspects remote repo, assigns `⏳ Onboarding Pending`, registers in `README.md`, and commits.
- **`/project-update <ID>`**: Updates `STATUS.md`, prepends wins, and appends a milestone entry to `journal.md`.
- **`/project-edit <ID>`**: Modifies owner, title, remote URL, or lifecycle health across project files and master registry.
- **`/sprint-done [sprint_id]`**: Closes sprint, archives delivered tasks, bumps CHANGELOG, and refreshes STATUS.md.
- **`/ping-leads`**: Scans STATUS.md files and opens idempotent GitHub issue alerts for stale (> 14 days) or onboarding-pending initiatives (excludes `LAB-000` and completed projects).
- **`log-milestone`**: Appends milestone entries directly to a project's `journal.md`.
- **`commit-changes`**: Stages and commits changes directly to `main` with standardized semantic commit prefixes.

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
