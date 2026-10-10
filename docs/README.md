[🏠 Cetana Labs](../README.md) / **📚 Docs**

# Cetana Labs — Documentation Hub

The documentation index for **Cetana Labs Control Hub (`LAB-000`)**. Docs are grouped by kind so the system is navigable and copyable (this repo is the AIDLC blueprint other repos adopt).

```
docs/
├── guides/       # how-to: user, developer (setup), AIDLC, mini-AIDLC, sprint-lifecycle, release, project-owner, RGS
├── reference/    # specs & standards: STATUS protocol, capability map, design system
├── governance/   # decision records, collaboration model, intake, registry-retirement
├── rfc/          # numbered decision records (RFC-LAB-000-0XX)
└── templates/    # reusable artifact templates
```
> The live app is the deployed **Sleek UI** (Vercel + Railway, `RFC-LAB-000-011` / M5). The old generated GitHub-Pages dashboard (`docs/index.html`) was retired at M5.

---

## 📖 Guides

| Doc | Purpose |
| :--- | :--- |
| [User Guide](guides/user-guide.md) | Navigating the portfolio — archetypes, statuses, AI prompts, front-door playbook. |
| [Developer Guide](guides/developer-guide.md) | Local **setup, commands, database & auth** — how to run this repo locally (process + deploy content split out into the AIDLC + Release guides). |
| [AIDLC Guide](guides/aidlc-guide.md) | **What AIDLC is & how we practise it** — the delivery method, work-class routing (functional vs engineering vs governance), who executes (Operator · Antigravity · Kiro IDE · Web), RGS. |
| [Mini-AIDLC Guide](guides/mini-aidlc-guide.md) | **POC-speed AIDLC** — the lightweight sibling; when to use it + the maturity ladder (points to the `aidlc-mini/` kickstarter). |
| [Sprint Lifecycle](guides/sprint-lifecycle.md) | The five-phase AIDLC delivery process **runbook** (both paths) — visual state machine + command sequence. |
| [Release Guide](guides/release-guide.md) | **Promote to staging & operate** — the deploy model (merge = promotion), Vercel + Railway, CLI ops, verify-bundle, the real Vercel signal. |
| [Project Owner Guide](guides/project-owner-guide.md) | How project **leads write `STATUS.md`** and run the `/status-init` · `/status-update` prompts. |
| [RGS Guide](guides/rgs-guide.md) | How to use **`/rgs`** (Requirement Gathering System) — turn a fuzzy ask into a ledger-ready `INTAKE-NNN` entry; the chat-only elicitation flow + where drafts land. |

## 📐 Reference

| Doc | Purpose |
| :--- | :--- |
| [Project Protocol](reference/project-protocol.md) | The authoritative 30-line `STATUS.md` standard + 5-pillar validation. |
| [Capability Map](reference/capability-map.md) | What the app does — capability domains + user journey (doc counterpart of the App Functionality artifact). |
| [Design System (Nexus Pulse)](reference/DESIGN.md) | The org visual source of truth — tokens, type, color, dark-first. |
| [Design System (LAB-000)](reference/design-system-lab000.md) | The SvelteKit + Tailwind mapping of the Nexus Pulse system for the Sleek UI. |

## ⚖️ Governance

| Doc | Purpose |
| :--- | :--- |
| [Decision Journal](governance/DECISION-JOURNAL.md) | Curated decision-narrative log (problem → options → decision → outcome). |
| [AI Collaboration Model](governance/ai-collaboration-model.md) | The human-directed / AI-assisted / human-gated working methodology. |
| [Requirements Intake](governance/REQUIREMENTS_INTAKE.md) | The `/rgs` requirement-draft register and its state machine (RFC-016 / D69). |
| [Registry-Retirement Design](governance/registry-retirement-design.md) | RFC-016 Phase 2 (BK-035): the OQ-1..OQ-4 answers that gate the registry inversion. |

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

### Footer navigation (smooth back-nav)

Every doc also **closes with a minimal footer-nav line** so a reader at the bottom of a long doc can jump back without scrolling up:

```markdown
---

> 🧭 **Navigation:** [⬆️ Top](#) · [🏠 Repo](../../README.md) · [📚 Docs Hub](../README.md)
```

- **⬆️ Top** (`#`) returns to the top of the current page; **🏠 Repo** is the repo root; **📚 Docs Hub** is this index (the "back to parent").
- A doc MAY add a second `> 🔗 **Related:** …` line beneath it with sibling/RFC cross-links.
- Same uniform depths as the breadcrumb (`../../` repo root, `../` hub).

---

> 🧭 **Navigation:** [⬆️ Top](#) · [🏠 Repo](../README.md)
