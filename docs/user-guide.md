# Cetana Labs — User Guide & Playbook

Welcome to **Cetana Labs**! This repository serves as our master engineering notebook, project registry, and operational control plane. 

This guide is written for both **maintainers** and **read-only collaborators** to help you quickly find what you need and work with AI assistants in this repository.

---

## 1. What is Cetana Labs?

`cetana-labs` is **not a code monorepo**. Instead, it is the single source of truth for:
- 📌 **Registry**: An indexed catalog of all active, past, and upcoming initiatives.
- 📋 **Executive Statuses**: Up-to-date, 30-line `STATUS.md` summaries for instant management updates.
- 🗓️ **Journals & Milestones**: High-level milestone timelines, architectural decisions, and phase histories.
- 🔗 **Pointers**: Direct links to external code repositories, datasets, and research papers.

---

## 2. How to Navigate Projects

Every project is organized in a flat structure under `projects/LAB-XXX-<name>/`:

```text
projects/LAB-XXX-<name>/
├── README.md       # Project Charter (Summary, architecture, tech stack & remote repo links)
├── STATUS.md       # 📋 Authoritative 30-line Executive Status (for management broadcasts)
├── journal.md      # Timeline & Decisions (Phased progress and major milestone logs)
└── assets/         # (Optional) Small diagrams, configs, reference outputs
```

### Quick Path Finder:
- **"Where is the source code & setup guide?"** $\rightarrow$ Open `projects/<ID>/README.md` and check the **Remote Repository** link (operational runbooks live directly inside each project's codebase).
- **"What is the current business status & health?"** $\rightarrow$ Open `projects/<ID>/STATUS.md`.
- **"Why was a decision made or what's the latest milestone?"** $\rightarrow$ Open `projects/<ID>/journal.md`.

---

## 3. Project Archetypes & Health Legend

### Archetypes
| Archetype | Icon | Focus & Description |
| :--- | :---: | :--- |
| **Mini-App / Coding** | 💻 | Standalone applications or microservices (code in remote repo). |
| **Research / Spike** | 📑 | Feasibility evaluations, tech trade-offs, and Go/No-Go decisions. |
| **Data Collection** | 📊 | Data pipelines, web scrapers, schemas, and dataset catalogs. |
| **Verification / Benchmark** | 🔬 | Test harnesses, performance benchmarks, and SLA validation. |

### Health Badges (`STATUS.md`)
- `🟢 On Track` — Milestones progressing smoothly as planned.
- `🟡 At Risk` — Minor delays or dependencies pending; no escalation yet.
- `🔴 Blocked` — Hard blocker requiring management intervention.
- `⏸️ Paused` — Intentionally on hold.
- `✅ Completed` — Finished, operationalized, or successfully verified.

---

## 4. The `STATUS.md` Protocol & Management Broadcasts

Every project adheres to the **[Project Status Protocol (docs/project-protocol.md)](project-protocol.md)**.
Whenever leadership asks for an update, you can generate a **WhatsApp-compatible message** in seconds:

- **All Projects Digest**: `/project-status` or `/project-status all`
- **Specific Project Deep-Dive**: `/project-status LAB-003`

The AI agent parses `STATUS.md` across repositories and formats a scannable, mobile-ready update.

---

## 5. Commit Guidelines (Trunk-Based / Main Only)

Since this repository is maintained primarily by one maintainer with read-only collaborators, we follow a simple **direct-to-`main`** commit workflow without branches or PR overhead.

### Commit Message Prefixes
| Type | Prefix Format | Example |
| :--- | :--- | :--- |
| **New Project** | `feat(<id>): init <name>` | `feat(lab-002): scaffold edge-llm-eval research project` |
| **Milestone / Journal** | `log(<id>): <summary>` | `log(lab-001): record phase 3 genbi milestone` |
| **Status Update** | `status(<id>): <summary>` | `status(lab-003): update health to on-track after signals merge` |
| **Repo / Global Structure** | `docs: <summary>` or `chore: <summary>` | `docs: update user-guide and template schemas` |

---

## 6. Working with AI Agents in this Repo

This repository is optimized for AI-assisted maintenance. You can use any AI tool (Antigravity, Cursor, Claude Code, GitHub Copilot, ChatGPT, etc.) to perform clerical and documentation work.

Here are copy-pasteable prompt templates:

### A. Generating WhatsApp Status Updates
> *"/project-status"*  
> *"/project-status LAB-003"*

### B. Creating a New Project
> *"Create a new [Mini-App / Research / Data / Verification] project titled '[Project Name]'. Objective: [Brief summary]. Owner: [Name]. Remote repo: [URL if applicable]."*

### C. Logging a Milestone & Committing
> *"Add a milestone to project [LAB-XXX]. Title: [Milestone Title]. Context: [What was accomplished]. Please commit the changes directly to main."*

### D. Updating Project Status
> *"Update STATUS.md for [LAB-XXX] with latest win: [Description]. Health: 🟢 On Track."*
