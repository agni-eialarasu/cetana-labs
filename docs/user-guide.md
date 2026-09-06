# Cetana Labs — User Guide & Playbook

Welcome to **Cetana Labs**! This repository serves as our master engineering notebook, project registry, and operational control plane. 

This guide is written for both **maintainers** and **read-only collaborators** to help you quickly find what you need and work with AI assistants in this repository.

---

## 1. What is Cetana Labs?

`cetana-labs` is **not a code monorepo**. Instead, it is the single source of truth for:
- 📌 **Registry**: An indexed catalog of all active, past, and upcoming initiatives.
- 📘 **Runbooks**: Exact, reproducible setup and operational instructions.
- 🗓️ **Journals**: High-level milestone timelines, architectural decisions, and phase histories.
- 🔗 **Pointers**: Direct links to external code repositories, datasets, and research papers.

---

## 2. How to Navigate Projects

Every project is organized in a flat structure under `projects/LAB-XXX-<name>/`:

```text
projects/LAB-XXX-<name>/
├── README.md       # Project Charter (Summary, architecture, tech stack & remote repo links)
├── runbook.md      # Operations & Setup (Prerequisites, copy-paste commands, troubleshooting)
├── journal.md      # Timeline & Decisions (Phased progress and major milestone logs)
└── assets/         # (Optional) Small diagrams, configs, reference outputs
```

### Quick Path Finder:
- **"Where is the source code?"** $\rightarrow$ Open `projects/<ID>/README.md` and check the **Remote Repository** link.
- **"How do I run or test this project?"** $\rightarrow$ Open `projects/<ID>/runbook.md`.
- **"Why was a decision made or what's the latest status?"** $\rightarrow$ Open `projects/<ID>/journal.md`.

---

## 3. Project Archetypes & Status Legend

### Archetypes
| Archetype | Icon | Focus & Description |
| :--- | :---: | :--- |
| **Mini-App / Coding** | 💻 | Standalone applications or microservices (code in remote repo). |
| **Research / Spike** | 📑 | Feasibility evaluations, tech trade-offs, and Go/No-Go decisions. |
| **Data Collection** | 📊 | Data pipelines, web scrapers, schemas, and dataset catalogs. |
| **Verification / Benchmark** | 🔬 | Test harnesses, performance benchmarks, and SLA validation. |

### Status Badges
- `🟢 Active` — Actively being developed, tested, or executed.
- `🟡 In Progress` — Scoped and progressing through planned milestones.
- `⏸️ Paused` — On hold pending external dependencies or resources.
- `✅ Completed` — Finished, operationalized, or successfully verified.
- `📦 Archived` — Preserved for historical context; no further work planned.

---

## 4. Commit Guidelines (Trunk-Based / Main Only)

Since this repository is maintained primarily by one maintainer with read-only collaborators, we follow a simple **direct-to-`main`** commit workflow without branches or PR overhead.

### Commit Message Prefixes
| Type | Prefix Format | Example |
| :--- | :--- | :--- |
| **New Project** | `feat(<id>): init <name>` | `feat(lab-002): scaffold edge-llm-eval research project` |
| **Milestone / Journal** | `log(<id>): <summary>` | `log(lab-001): record phase 3 genbi milestone` |
| **Runbook / Docs** | `docs(<id>): <summary>` | `docs(lab-001): update local webcam runbook instructions` |
| **Repo / Global Structure** | `docs: <summary>` or `chore: <summary>` | `docs: update user-guide and template schemas` |

---

## 5. Working with AI Agents in this Repo

This repository is optimized for AI-assisted maintenance. You can use any AI tool (Antigravity, Cursor, Claude Code, GitHub Copilot, ChatGPT, etc.) to perform clerical and documentation work.

Here are copy-pasteable prompt templates:

### A. Creating a New Project
> *"Create a new [Mini-App / Research / Data / Verification] project titled '[Project Name]'. Objective: [Brief summary]. Owner: [Name]. Remote repo: [URL if applicable]."*

### B. Logging a Milestone & Committing
> *"Add a milestone to project [LAB-XXX]. Title: [Milestone Title]. Context: [What was accomplished]. Please commit the changes directly to main."*

### C. Updating an Operational Runbook
> *"Update the runbook for [LAB-XXX] with the following setup steps: [Paste steps/commands]."*

### D. Cross-Lab Summary
> *"Provide a summary of all active lab projects, their current phases, and pending milestones."*
