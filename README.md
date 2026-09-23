# Cetana Labs (Master Registry & Lab Notebook)

> 📖 **User Guide:** [docs/user-guide.md](docs/user-guide.md)  
> 👥 **Project Owner Guide & AI Prompts:** [docs/project-owner-guide.md](docs/project-owner-guide.md)  
> 📋 **Project Status Protocol (`STATUS.md`):** [docs/project-protocol.md](docs/project-protocol.md)  
> 💬 **On-Demand Management Broadcasts:** Run `/project-status` or `/project-status <ID>` for WhatsApp-ready executive updates.

---

Welcome to **Cetana Labs** — the central command plane, master project registry, and operational lab notebook for engineering initiatives, research spikes, mini-apps, data pipelines, and benchmark verifications.

---

## 🧭 Master Project Registry

| ID | Project Name | Archetype | Health | Lead | Codebase / Reference | Executive Status (`STATUS.md`) |
| :---: | :--- | :---: | :---: | :---: | :--- | :---: |
| **`LAB-001`** | **[AAMAS](projects/LAB-001-ammas/README.md)** (Autism Activity Monitor) | 💻 Mini-App | `✅ Completed` | Eialarasu | [GitHub Repo](https://github.com/agni-eialarasu/ammas) | [STATUS.md](projects/LAB-001-ammas/STATUS.md) |
| **`LAB-002`** | **[WrenAI Evaluation](projects/LAB-002-wrenai-eval/README.md)** (Semantic GenBI) | 📑 Research | `🟢 On Track` | Eialarasu | [getwren.ai](https://www.getwren.ai/) / [LAB-001 Proof](projects/LAB-001-ammas/README.md) | [STATUS.md](projects/LAB-002-wrenai-eval/STATUS.md) |
| **`LAB-003`** | **[Nexus Pulse](projects/LAB-003-nexus-pulse/README.md)** (Vertical Engine) | 💻 Mini-App | `🟢 On Track` | Hariharasubramanian | [GitHub Repo](https://github.com/eAgni-Technologies/nexus-pulse) | [STATUS.md](projects/LAB-003-nexus-pulse/STATUS.md) |
| **`LAB-004`** | **[Cetana Labs Control Hub](projects/LAB-004-cetana-labs/README.md)** (Protocol Engine) | 💻 Mini-App | `🟢 On Track` | Eialarasu | [GitHub Repo](https://github.com/agni-eialarasu/cetana-labs) | [STATUS.md](projects/LAB-004-cetana-labs/STATUS.md) |

---

## 🗂️ Repository Structure

```text
cetana-labs/
├── README.md                      # Master Dashboard & Project Registry (You are here)
├── STATUS.md                      # 📋 Authoritative Root Status for Cetana Labs (LAB-004)
├── .github/workflows/
│   └── project-status-cron.yml    # ⏰ Scheduled weekday GitHub Actions broadcast workflow
├── scripts/
│   └── generate_status.py         # 📱 Standalone WhatsApp executive status generator
├── docs/
│   ├── user-guide.md              # 👤 Human Guide: Navigation, Archetypes, Statuses & AI Prompts
│   ├── project-owner-guide.md     # 👥 Developer & Lead Guide: AI Prompts (/status-init, /status-update)
│   └── project-protocol.md        # 📋 Authoritative STATUS.md specification
├── AGENTS.md                      # 🤖 Universal AI Instructions (Rules, Constraints, Workflows)
├── CLAUDE.md                      # 🤖 Agent pointer for Claude Code
├── .agents/skills/                # 🤖 Reusable AI playbooks
│   ├── project-status/            # Generates WhatsApp-ready updates on-demand (/project-status)
│   ├── project-add/               # Onboards new initiatives via remote inspection (/project-add)
│   ├── project-update/            # Logs delivery wins, health & milestones (/project-update)
│   ├── project-edit/              # Modifies metadata, leads & lifecycle states (/project-edit)
│   ├── log-milestone/             # Appends milestone entries to journal
│   └── commit-changes/            # Standardized trunk-based git commits
├── templates/                     # Standardized scaffolds for rapid onboarding
└── projects/                      # All lab initiatives (flat hierarchy)
    ├── LAB-001-ammas/             # Behavioral CV Edge System & GenBI Analytics
    ├── LAB-002-wrenai-eval/       # WrenAI Capabilities & Semantic GenBI Evaluation
    ├── LAB-003-nexus-pulse/       # Governed Operational & Financial Intelligence Engine
    └── LAB-004-cetana-labs/       # Central Command Plane & Protocol Engine
```

---

## 🏷️ Project Archetypes

- 💻 **Mini-App / Coding**: Independent software services with external repositories.
- 📑 **Research / Spike**: Feasibility studies, literature surveys, trade-off evaluations, and Go/No-Go decisions.
- 📊 **Data Collection**: Datasets, web scraping pipelines, annotations, and schemas.
- 🔬 **Verification / Benchmark**: Test rigs, SLA validations, model accuracy benchmarks, and stress tests.

For detailed guidelines, see **[docs/user-guide.md](docs/user-guide.md)** and **[docs/project-protocol.md](docs/project-protocol.md)**.
