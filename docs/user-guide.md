# Cetana Labs — User Guide & Playbook

Welcome to **Cetana Labs**! This repository serves as our master engineering notebook, project registry, sprint roadmap, and operational control plane.

This guide is written for both **maintainers** and **collaborators** to help you quickly find what you need and work with AI assistants in this repository.

---

## 1. What is Cetana Labs?

`cetana-labs` is **not a code monorepo**. Instead, it is the single source of truth for:
- 🧭 **Master Registry**: An indexed catalog of all active, completed, and onboarding initiatives.
- 📋 **Executive Statuses**: Up-to-date, 30-line `STATUS.md` summaries for instant management updates.
- 🎯 **Sprint Roadmap & Backlog**: Centrally tracked active sprint deliverables and future capabilities in [`BACKLOG.md`](../BACKLOG.md).
- 📜 **Historical Releases**: Semantic delivery changelog maintained in [`CHANGELOG.md`](../CHANGELOG.md).
- 🗓️ **Journals & Milestones**: High-level milestone timelines, architectural decisions, and phase histories.
- 🔗 **Pointers**: Direct links to external code repositories, datasets, and research papers.

---

## 2. How to Navigate Projects

Every project is organized in a flat structure under `projects/LAB-XXX-<name>/`:

```text
projects/
├── LAB-000-cetana-labs/   # 💻 Central Command Plane & Protocol Kernel
├── LAB-001-ammas/         # ✅ Completed: Edge Computer Vision & GenBI System
├── LAB-002-wrenai-eval/   # ✅ Completed: Semantic Modeling Research Spike
├── LAB-003-nexus-pulse/   # 🟢 Active: Enterprise Operations & Margin Engine
├── LAB-005-zerobea-ai/    # ⏳ Onboarding: AI Security Control Plane
└── LAB-006-nexus-beacon/  # ⏳ Onboarding: Operational Alert Service
```

Each project folder contains standard documents:
- `README.md` — Project Charter (Summary, architecture, tech stack & remote repo links).
- `STATUS.md` — Authoritative 30-line Executive Status card for management broadcasts.
- `journal.md` — Reverse-chronological milestone log, phase history, and architectural decisions.

### Quick Path Finder:
- **"Where is the source code & setup guide?"** $\rightarrow$ Open `projects/<ID>/README.md` and check the **Remote Repository** link (operational runbooks live directly inside each project's codebase).
- **"What is the current business status & health?"** $\rightarrow$ Open `projects/<ID>/STATUS.md`.
- **"What is the active sprint plan & backlog?"** $\rightarrow$ Open root [`BACKLOG.md`](../BACKLOG.md).
- **"What was shipped recently across versions?"** $\rightarrow$ Open root [`CHANGELOG.md`](../CHANGELOG.md).
- **"Why was a decision made or what's the latest milestone?"** $\rightarrow$ Open `projects/<ID>/journal.md`.

---

## 3. Project Archetypes & Health Legend

### Archetypes
| Archetype | Icon | Focus & Description |
| :--- | :---: | :--- |
| **Control Plane** | 💻 | Central hub, management engine, and protocol kernel (`LAB-000`). |
| **Mini-App / Coding** | 💻 | Standalone applications or microservices (code in remote repo). |
| **Research / Spike** | 📑 | Feasibility evaluations, tech trade-offs, and Go/No-Go decisions. |
| **Data Collection** | 📊 | Data pipelines, web scrapers, schemas, and dataset catalogs. |
| **Verification / Benchmark** | 🔬 | Test harnesses, performance benchmarks, and SLA validation. |

### Health Badges (`STATUS.md`)
- `⏳ Onboarding Pending` — Project registered in portfolio; awaiting lead's initial `/status-init` commit.
- `🟢 On Track` — Milestones progressing smoothly as planned.
- `🟡 At Risk` — Minor delays or dependencies pending; no escalation yet.
- `🔴 Blocked` — Hard blocker requiring management intervention.
- `⏸️ Paused` — Intentionally on hold.
- `✅ Completed` — Finished, operationalized, or successfully verified.

---

## 4. The AI Command Suite (`/project-*`)

You can execute the following standardized slash commands directly in chat with your AI agent:

### 📱 `/project-status [ID]` (Management Broadcast)
Generates an emoji-rich, mobile-friendly WhatsApp broadcast block for leadership:
- `/project-status` $\rightarrow$ Portfolio digest of **active, non-completed product initiatives** (`LAB-003`, `LAB-005`, `LAB-006`).
- `/project-status LAB-000` $\rightarrow$ Deep-dive briefing on the Cetana Labs Control Hub kernel.
- `/project-status LAB-003` $\rightarrow$ Deep-dive briefing on a single project.

### ➕ `/project-add <repo_url_or_title>` (Onboard Project)
Scaffolds the next sequential `LAB-XXX` directory, fetches remote repository metadata, initializes `STATUS.md` in `⏳ Onboarding Pending` state, registers the project in the master table, and commits to `main`:
- `/project-add https://github.com/org/repo --owner "Lead Name"`
- `/project-add "Edge Model Benchmark" research Eialarasu`

### 🔄 `/project-update <ID>` (Log Wins & Health)
Records delivery wins, health updates, or blockers in `STATUS.md` and appends a milestone entry to `journal.md`:
- `/project-update LAB-003` (Auto-inspects remote repository commits)
- `/project-update LAB-003 "Shipped margin signal rule SIG-01"`
- `/project-update LAB-003 --health at-risk --blocker "Awaiting staging API key"`

### ✏️ `/project-edit <ID>` (Administrative Metadata)
Modifies project ownership, titles, repository links, or archives an initiative:
- `/project-edit LAB-003 --owner "Eialarasu"`
- `/project-edit LAB-002 --health completed`

---

## 5. Periodic Automated Broadcasts (GitHub Actions)

This repository includes a scheduled GitHub Actions workflow (`.github/workflows/project-status-cron.yml`):
- **Schedule**: Weekdays (Monday–Friday) at 9:30 AM IST (4:00 AM UTC).
- **Execution**: Runs `python3 scripts/generate_status.py --github-summary`.
- **Output (Option A)**: Publishes the WhatsApp-ready text directly on the GitHub Job Summary page for 1-click copy-pasting.
- **Future Extension (Option B)**: Directly dispatches to a team WhatsApp / Slack incoming webhook (`TSK-013`).

---

## 6. Commit Guidelines (Trunk-Based / Main Only)

We follow a simple **direct-to-`main`** commit workflow without branches or PR overhead.

### Commit Message Prefixes
| Type | Prefix Format | Example |
| :--- | :--- | :--- |
| **New Project** | `feat(<id>): init <name>` | `feat(lab-006): init nexus-beacon project` |
| **Milestone / Journal** | `log(<id>): <summary>` | `log(lab-001): record phase 3 genbi milestone` |
| **Status Update** | `status(<id>): <summary>` | `status(lab-003): update health to on-track after signals merge` |
| **Project Edit** | `chore(<id>): update <attribute>` | `chore(lab-003): update lead to Eialarasu` |
| **Global Docs & Config** | `docs: <summary>` or `chore: <summary>` | `docs: update user guide and backlog` |
| **Governance / Sprint** | `feat(governance): <summary>` | `feat(governance): initialize bare-minimum sprint tracking` |
