# Cetana Labs (Master Registry & Lab Notebook)

> 🌐 **Live Portfolio Dashboard:** [agni-eialarasu.github.io/cetana-labs](https://agni-eialarasu.github.io/cetana-labs/)  
> 📖 **User Guide:** [docs/user-guide.md](docs/user-guide.md)  
> 👥 **Project Owner Guide & AI Prompts:** [docs/project-owner-guide.md](docs/project-owner-guide.md)  
> 📋 **Project Status Protocol (`STATUS.md`):** [docs/project-protocol.md](docs/project-protocol.md)  
> 🎯 **Sprint Backlog & Roadmap:** [BACKLOG.md](BACKLOG.md)  
> 📜 **Project Changelog:** [CHANGELOG.md](CHANGELOG.md)  
> 💬 **On-Demand Management Broadcasts:** Run `/project-status` or `/project-status <ID>` for WhatsApp-ready executive updates.

---

Welcome to **Cetana Labs** — the central command plane, master project registry, and operational lab notebook for engineering initiatives, research spikes, mini-apps, data pipelines, and benchmark verifications.

---

## 🧭 Master Project Registry

| ID | Project Name | Archetype | Health | Lead | Codebase / Reference | Executive Status (`STATUS.md`) |
| :---: | :--- | :---: | :---: | :---: | :--- | :---: |
| **`LAB-000`** | **[Cetana Labs Control Hub](projects/LAB-000-cetana-labs/README.md)** (Protocol Engine) | 💻 Control Plane | `🟢 On Track` | Eialarasu | [GitHub Repo](https://github.com/agni-eialarasu/cetana-labs) | [STATUS.md](projects/LAB-000-cetana-labs/STATUS.md) |
| **`LAB-001`** | **[AAMAS](projects/LAB-001-ammas/README.md)** (Autism Activity Monitor) | 💻 Mini-App | `✅ Completed` | Eialarasu | [GitHub Repo](https://github.com/agni-eialarasu/ammas) | [STATUS.md](projects/LAB-001-ammas/STATUS.md) |
| **`LAB-002`** | **[WrenAI Evaluation](projects/LAB-002-wrenai-eval/README.md)** (Semantic GenBI) | 📑 Research | `✅ Completed` | Eialarasu | [getwren.ai](https://www.getwren.ai/) / [LAB-001 Proof](projects/LAB-001-ammas/README.md) | [STATUS.md](projects/LAB-002-wrenai-eval/STATUS.md) |
| **`LAB-003`** | **[Nexus Pulse](projects/LAB-003-nexus-pulse/README.md)** (Vertical Engine) | 💻 Mini-App | `🟢 On Track` | Eialarasu | [GitHub Repo](https://github.com/eAgni-Technologies/nexus-pulse) | [STATUS.md](projects/LAB-003-nexus-pulse/STATUS.md) |
| **`LAB-004`** | **[Zerobea.ai](projects/LAB-004-zerobea-ai/README.md)** (AI Security Control Plane) | 💻 Mini-App | `⏳ Onboarding Pending` | Abishek Singhavi | [GitHub Repo](https://github.com/zerobeadotai/zerobea.ai) | [STATUS.md](projects/LAB-004-zerobea-ai/STATUS.md) |
| **`LAB-005`** | **[Nexus Beacon](projects/LAB-005-nexus-beacon/README.md)** (Operational Alert Service) | 💻 Mini-App | `⏳ Onboarding Pending` | Arun Elambaram | [GitHub Repo](https://github.com/eAgni-Technologies/nexus-beacon) | [STATUS.md](projects/LAB-005-nexus-beacon/STATUS.md) |

> ℹ️ *Note: `LAB-000` is the central control plane kernel. Routine morning portfolio broadcasts report active client/product initiatives (`LAB-003`, `LAB-004`, `LAB-005`). To inspect the Control Hub status specifically, run `/project-status LAB-000`.*

---

## 🗂️ Repository Structure

```text
cetana-labs/
├── README.md                      # Master Dashboard & Project Registry (You are here)
├── STATUS.md                      # 📋 Authoritative Root Status for Cetana Labs (LAB-000)
├── BACKLOG.md                     # 🎯 Sprint Backlog, Roadmap & Delivered Sprints
├── CHANGELOG.md                   # 📜 Keep a Changelog Historical Releases
├── .github/workflows/
│   ├── project-status-cron.yml    # ⏰ Scheduled weekday GitHub Actions broadcast workflow
│   └── deploy-pages.yml           # 🌐 Automated GitHub Pages dashboard deployment workflow
├── scripts/
│   ├── generate_status.py         # 📱 Standalone WhatsApp executive status generator
│   ├── generate_dashboard.py      # 🌐 Static HTML portfolio web dashboard generator
│   └── validate_portfolio.py      # 🛡️ CI linter & project structure validator
├── docs/
│   ├── index.html                 # 🌐 Live Interactive Portfolio Dashboard (GitHub Pages)
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
│   ├── sprint-done/               # Closes sprint, archives tasks & bumps changelog (/sprint-done)
│   ├── log-milestone/             # Appends milestone entries to journal
│   └── commit-changes/            # Standardized trunk-based git commits
├── templates/                     # Standardized scaffolds for rapid onboarding
└── projects/                      # All lab initiatives (flat hierarchy)
    ├── LAB-000-cetana-labs/       # Central Command Plane & Protocol Engine
    ├── LAB-001-ammas/             # Behavioral CV Edge System & GenBI Analytics
    ├── LAB-002-wrenai-eval/       # WrenAI Capabilities & Semantic GenBI Evaluation
    ├── LAB-003-nexus-pulse/       # Governed Operational & Financial Intelligence Engine
    ├── LAB-004-zerobea-ai/        # AI Security Control Plane & Governed Gateway
    └── LAB-005-nexus-beacon/      # Telemetry & Operational Alert Service
```

---

## 🏷️ Project Archetypes

- 💻 **Mini-App / Coding**: Independent software services with external repositories.
- 📑 **Research / Spike**: Feasibility studies, literature surveys, trade-off evaluations, and Go/No-Go decisions.
- 📊 **Data Collection**: Datasets, web scraping pipelines, annotations, and schemas.
- 🔬 **Verification / Benchmark**: Test rigs, SLA validations, model accuracy benchmarks, and stress tests.

For detailed guidelines, see **[docs/user-guide.md](docs/user-guide.md)** and **[docs/project-protocol.md](docs/project-protocol.md)**.
