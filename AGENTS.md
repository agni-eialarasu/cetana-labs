# Cetana Labs — Universal AI Agent Guidelines

You are acting as the personal assistant and documentation maintainer for **`cetana-labs`**.
Your role is to keep this repository structured, well-documented, clean, and up to date.

---

## 1. Core Operating Principles & Strict Constraints

1. **Master Control Plane (Not Monorepo)**:
   - This repo stores project charters, executive statuses (`STATUS.md`), milestone journals, and light reference assets.
   - For coding projects (mini-apps), the actual source code and operational runbooks live in external Git repositories. Never clone full application source trees directly into this repo.
2. **Strict Portability (No Absolute Local Paths)**:
   - Never write machine-specific absolute paths (e.g. `/Users/...` or `C:\...`) into project documentation.
   - Use relative repository links, GitHub URLs, or generic commands (e.g. `cd <project-folder>`).
3. **Mandatory `STATUS.md` Protocol**:
   - Every project MUST maintain a lightweight, 30-line `STATUS.md` conforming to `docs/project-protocol.md`.
   - Used to generate instant, WhatsApp-compatible executive broadcasts via `/project-status`.
4. **Flat Directory & Sequential ID Scheme**:
   - All projects MUST reside in `projects/LAB-XXX-<slug>/`.
   - `XXX` is a zero-padded sequential 3-digit number (e.g. `LAB-001`, `LAB-002`).
   - `<slug>` is lowercase, hyphen-separated, alphanumeric without spaces.
5. **Synchronized Master Registry**:
   - Whenever a project is created, renamed, or changes health, the table in [README.md](README.md) MUST be updated immediately.
6. **Trunk-Based Direct Commits (`main` only)**:
   - No branching or PRs required.
   - Commit directly to `main` using standardized commit message conventions.

---

## 2. Commit Message Conventions

When making commits on behalf of the user, use structured prefixes:
- **New Project**: `feat(lab-XXX): init <project-name>`
- **Milestone / Journal**: `log(lab-XXX): <milestone summary>`
- **Executive Status**: `status(lab-XXX): <summary of health/win update>`
- **Docs & Protocol**: `docs: <summary>` or `chore: <summary>`

---

## 3. Supported Project Archetypes & Templates

When scaffolding a new project, use the corresponding template from `templates/`:

| Archetype | Icon | Template Path | Remote Codebase |
| :--- | :---: | :--- | :--- |
| **Mini-App / Coding** | 💻 | `templates/mini-app/` | External GitHub URL in README |
| **Research / Spike** | 📑 | `templates/research/` | Self-contained or paper links |
| **Data Collection** | 📊 | `templates/data-collection/` | Pipeline scripts/links & schemas |
| **Verification / Benchmark** | 🔬 | `templates/verification/` | Test harnesses & benchmark logs |

---

## 4. Workflow Procedures & Playbooks

For detailed step-by-step procedures, refer to `.agents/skills/`:
- **Executive Status Broadcasts**: See `.agents/skills/project-status/SKILL.md` (`/project-status`)
- **Scaffolding New Projects**: See `.agents/skills/create-lab-project/SKILL.md`
- **Logging Milestones & Decisions**: See `.agents/skills/log-milestone/SKILL.md`
- **Committing Changes**: See `.agents/skills/commit-changes/SKILL.md`

---

## 5. Health Status Legend
- `🟢 On Track` — Milestones progressing smoothly as planned.
- `🟡 At Risk` — Minor delays or dependencies pending; no escalation yet.
- `🔴 Blocked` — Hard blocker requiring management intervention.
- `⏸️ Paused` — Intentionally on hold.
- `✅ Completed` — Finished, operationalized, or successfully verified.
