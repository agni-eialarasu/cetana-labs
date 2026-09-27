[🏠 Cetana Labs](../README.md) / **📚 Docs**

# Cetana Labs — Documentation Hub

The documentation index for **Cetana Labs Control Hub (`LAB-000`)**. Docs are grouped by kind so the system is navigable and copyable (this repo is the AIDLC blueprint other repos adopt).

```
docs/
├── guides/       # how-to: onboarding, dev setup, lifecycle, lead protocol
├── reference/    # specs & standards: STATUS protocol, design system
├── governance/   # decision records & collaboration model
├── rfc/          # numbered decision records (RFC-LAB-000-0XX)
├── templates/    # reusable artifact templates
└── index.html    # generated GitHub-Pages dashboard (build artifact — see RFC-LAB-000-011)
```

---

## 📖 Guides

| Doc | Purpose |
| :--- | :--- |
| [User Guide](guides/user-guide.md) | Navigating the portfolio — archetypes, statuses, AI prompts, front-door playbook. |
| [Developer Guide](guides/developer-guide.md) | Local/cloud **setup, commands, and Kiro Web + IDE surfaces** — how to develop on this repo (renamed from `work-environment.md`). |
| [Sprint Lifecycle](guides/sprint-lifecycle.md) | The five-phase AIDLC delivery process (both paths) — visual state + sequence guide. |
| [Project Owner Guide](guides/project-owner-guide.md) | How project **leads write `STATUS.md`** and run the `/status-init` · `/status-update` prompts. |
| [Cloud Dev Guide](guides/cloud-dev-guide.md) | Cloud-only development runbook (⚠️ possibly superseded by the Developer Guide — under review). |

## 📐 Reference

| Doc | Purpose |
| :--- | :--- |
| [Project Protocol](reference/project-protocol.md) | The authoritative 30-line `STATUS.md` standard + 5-pillar validation. |
| [Design System (Nexus Pulse)](reference/DESIGN.md) | The org visual source of truth — tokens, type, color, dark-first. |
| [Design System (LAB-000)](reference/design-system-lab000.md) | The SvelteKit + Tailwind mapping of the Nexus Pulse system for the Sleek UI. |

## ⚖️ Governance

| Doc | Purpose |
| :--- | :--- |
| [Decision Journal](governance/DECISION-JOURNAL.md) | Curated decision-narrative log (problem → options → decision → outcome). |
| [AI Collaboration Model](governance/ai-collaboration-model.md) | The human-directed / AI-assisted / human-gated working methodology. |

## 📜 RFCs

Numbered decision records live in [`rfc/`](rfc/) (`RFC-LAB-000-001` … `-010`) — cloud dev, relational data, PocketBase, branching, UI, auth/RBAC, work-environment, MVP, sprint lifecycle, and the tracking model. Each RFC keeps its own header format.

## 🧩 Templates

Reusable artifact templates live in [`templates/`](templates/) (e.g. `REPORT.template.md`).

---

## 🧭 Navigation standard (breadcrumbs)

Every markdown doc under `docs/` (**except** `rfc/*`, `templates/*`, and `index.html`) **opens with a breadcrumb line** so a reader can always get back to the hub and the repo root:

```markdown
[🏠 Cetana Labs](../../README.md) / [📚 Docs](../README.md) / <Category> / **This Doc**
```

- `<Category>` is the folder label: **Guides** / **Reference** / **Governance**.
- Relative depth: `../../` reaches the repo root `README.md`; `../` reaches this hub (`docs/README.md`). All docs sit one level under a category folder, so these depths are uniform.
- New docs MUST follow this standard (it is the copyable convention — referenced from [`AGENTS.md`](../AGENTS.md)).

> 🔙 Back to the repository root: [`../README.md`](../README.md).
