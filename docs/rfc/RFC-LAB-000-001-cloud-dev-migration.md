# RFC-LAB-000-001: Cloud-Based Development Migration & Environment Classification

| Property | Value |
| :--- | :--- |
| **RFC ID** | `RFC-LAB-000-001` |
| **Title** | Cloud-Based Development Migration & Repo Environment Classification |
| **Author** | Eialarasu (LAB-000 Control Hub) |
| **Status** | ✅ Accepted |
| **Date** | 2026-09-24 |
| **Supersedes** | — |
| **Affected Initiatives** | `LAB-000` (immediate), portfolio-wide classification (forward) |

---

## 1. Context & Problem Statement

Cetana Labs (`LAB-000`) has, to date, been developed locally using **IntelliJ IDEA + Antigravity IDE**. The maintainer concurrently develops a second, **fullstack** initiative on the same physical machine, which legitimately requires local resources (database, application servers, hot-reload dev loop).

Running two IntelliJ IDEA + Antigravity instances simultaneously has produced **material local machine performance degradation**. This is a resource-contention problem, not a tooling defect.

The key observation: **`LAB-000` in its current form has no local runtime dependency.** It is a documentation and Python-scripting control plane whose execution environment is already GitHub Actions (morning cron broadcast + Pages deployment). The local machine functions only as a text editor and git client.

## 2. Decision

1. **`LAB-000` migrates to cloud-based development**, freeing the local machine exclusively for the stateful fullstack initiative that genuinely requires it.
2. **Primary cloud environment: Kiro Web** (browser-based, agent-native, zero local footprint).
3. **Secondary / fallback environment: GitHub Codespaces**, reserved for when long-running services (db + server) and port-forwarding become necessary (see §5, Forward Compatibility).
4. A reusable **Environment Classification heuristic** (§4) is adopted portfolio-wide to decide, for any initiative, whether it is *cloud-eligible* or *local-required*.
5. Each project's development environment is **tracked as first-class metadata** in the `STATUS.md` protocol and the master registry (implemented alongside this RFC).

## 3. Rationale — Why Kiro Web (Primary)

| Factor | Kiro Web | GitHub Codespaces | Local (status quo) |
| :--- | :---: | :---: | :---: |
| Local machine footprint | **None** ✅ | None ✅ | Heavy ❌ |
| Agent-native workflow | **Yes** ✅ | Partial | Yes (Antigravity) |
| Trunk-based direct commit | **Yes** ✅ | Yes ✅ | Yes ✅ |
| Suited to docs + scripting | **Ideal** ✅ | Ideal ✅ | Overkill |
| Long-running services (db+server) | Not yet | **Yes** ✅ | Yes ✅ |
| Setup overhead | **Minimal** ✅ | Low | N/A |

For the **current** control-plane workload (Markdown + zero-dependency Python + CI-executed automation), Kiro Web is the best fit: it eliminates the local footprint that is the root cause of the performance problem, while preserving the AI-driven, trunk-based workflow already codified in `AGENTS.md`.

## 4. Environment Classification Heuristic (Reusable Rule)

For any Cetana Labs initiative, classify as **☁️ Cloud** unless it trips a **local-required** trigger:

An initiative is **💻 Local-Required** if **any** of the following hold:
- It runs a **persistent local service** during development (database, message broker, backend server with hot-reload).
- It requires **hardware access** unavailable in the cloud (GPU, camera/CV capture, USB/serial, edge device).
- It has **strict data-residency / air-gap** constraints preventing cloud checkout.
- It depends on a **local emulator or heavyweight native toolchain** impractical to containerize.

Otherwise it is **☁️ Cloud-Eligible** (default). Docs, research spikes, static generators, and CI-executed automation are cloud-eligible by definition.

> **Applied to the current portfolio:** `LAB-000` → ☁️ Cloud. The maintainer's fullstack initiative → 💻 Local. `LAB-001` (AAMAS, CV edge) → 💻 Local (hardware). Others classified as leads onboard.

## 5. Forward Compatibility — Evolution to a Full Web App (db + server) & RBAC

`LAB-000` is planned to evolve from a static control plane into a **full web application (database + server)**, with **RBAC-based features** already on the backlog (`BK-007`: on-demand git audit trail with role-gated history/access).

This RFC anticipates that trajectory:
- **A devcontainer (`.devcontainer/devcontainer.json`) is introduced now** so the environment is reproducible and portable across Kiro Web and Codespaces from day one. As services are added, they are declared in the devcontainer rather than the local machine.
- **When persistent services (db + server) land**, `LAB-000`'s classification is expected to shift toward Codespaces (or equivalent) as primary, per the §4 heuristic — but development stays cloud-based; it does **not** return to the local machine.
- **RBAC (`BK-007`) is explicitly noted** as the driver that will introduce the server + auth layer. The classification rule and devcontainer are designed to absorb that change without re-litigating the cloud-vs-local decision.

## 6. Migration Plan

1. **Ratify** this RFC (this document). ✅
2. **Add environment metadata** to the `STATUS.md` protocol and master registry.
3. **Publish** a cloud dev onboarding runbook (`docs/cloud-dev-guide.md`).
4. **Add** `.devcontainer/devcontainer.json` for reproducibility and forward compatibility.
5. **Register** the migration in `BACKLOG.md`, bump `CHANGELOG.md` (Unreleased), and log a `LAB-000` journal milestone.
6. **Decommission** the local IntelliJ + Antigravity instance for `LAB-000` (maintainer action, outside repo).

## 7. Verification Checklist (Definition of Done)

- [ ] Full edit → validate → commit → push loop completes entirely in Kiro Web.
- [ ] `python3 scripts/validate_portfolio.py` passes (6/6).
- [ ] `python3 scripts/project_validate.py` pre-flight gate passes.
- [ ] Dashboard renders: `python3 scripts/generate_dashboard.py` produces valid `docs/index.html`.
- [ ] GitHub Pages deploy + morning cron workflows unaffected (they already run in CI).
- [ ] `README.md` registry, `BACKLOG.md`, `CHANGELOG.md`, and journal remain in lockstep.

## 8. Risks & Mitigations

| Risk | Mitigation |
| :--- | :--- |
| Loss of local Antigravity agent for this repo | Kiro Web is agent-native; parity for docs/scripting work. |
| Dashboard visual regressions unseen locally | Verify via `generate_dashboard.py` preview or the live Pages URL. |
| Future db+server outgrows browser env | Devcontainer + Codespaces fallback already provisioned (§5). |
| Cloud environment drift between contributors | `.devcontainer` pins the toolchain reproducibly. |
