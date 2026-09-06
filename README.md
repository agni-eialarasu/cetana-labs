# Cetana Labs (Master Registry & Lab Notebook)

> 📖 **Looking for how to use this repository, navigate projects, or prompt AI agents?**  
> Check out the **[User Guide & Playbook (docs/user-guide.md)](docs/user-guide.md)**.

---

Welcome to **Cetana Labs** — the central command plane, master project registry, and operational lab notebook for engineering initiatives, research spikes, mini-apps, data pipelines, and benchmark verifications.

---

## 🧭 Master Project Registry

| ID | Project Name | Archetype | Status | Primary Owner | Codebase / Reference | Runbook | Journal |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`LAB-001`** | **[AAMAS (Autism Activity Monitoring & Alerting System)](projects/LAB-001-ammas/README.md)** | 💻 Mini-App | `🟢 Active` | Eialarasu | [GitHub Repo](https://github.com/agni-eialarasu/ammas) | [Runbook](projects/LAB-001-ammas/runbook.md) | [Journal](projects/LAB-001-ammas/journal.md) |

---

## 🗂️ Repository Structure

```text
cetana-labs/
├── README.md                      # Master Dashboard & Project Registry (You are here)
├── docs/
│   └── user-guide.md              # 👤 Human Guide: Navigation, Archetypes, Statuses & AI Prompts
├── AGENTS.md                      # 🤖 Universal AI Instructions (Rules, Constraints, Workflows)
├── CLAUDE.md                      # 🤖 Agent pointer for Claude Code
├── .agents/skills/                # 🤖 Reusable AI playbooks (create-project, log-milestone, etc.)
├── templates/                     # Standardized scaffolds for rapid onboarding
│   ├── mini-app/                  # For projects with independent code repos
│   ├── research/                  # For literature reviews, spikes & tech evaluations
│   ├── data-collection/           # For data pipelines, datasets & web scraping
│   └── verification/              # For benchmarks, test harnesses & QA audits
└── projects/                      # All lab initiatives (flat hierarchy)
    └── LAB-001-ammas/             # Behavioral CV Edge System & GenBI Analytics
        ├── README.md              # Project Charter & Architecture
        ├── runbook.md             # Setup, Execution, & Commands
        └── journal.md             # Phase History & Milestone Timeline
```

---

## 🏷️ Project Archetypes

- 💻 **Mini-App / Coding**: Independent software services with external repositories.
- 📑 **Research / Spike**: Feasibility studies, literature surveys, trade-off evaluations, and Go/No-Go decisions.
- 📊 **Data Collection**: Datasets, web scraping pipelines, annotations, and schemas.
- 🔬 **Verification / Benchmark**: Test rigs, SLA validations, model accuracy benchmarks, and stress tests.

For detailed guidelines, see **[docs/user-guide.md](docs/user-guide.md)**.
