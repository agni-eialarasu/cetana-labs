# Adopt `just` Task-Runner — Requirements

| Property | Value |
| :--- | :--- |
| **Spec ID** | `adopt-just-task-runner` |
| **Feature** | Replace Cetana Labs' `make` with a `justfile`, leading with the Agni shared cross-repo **core** (7 recipes, identical names to Nexus Pulse); keep `make` as a thin forwarding shim for one sprint |
| **Backlog** | `BK-025` (cross-repo DX / toolchain standard) — `TSK-066` |
| **Status** | 🟡 Proposed (authored on KiroCrew Operator; execution on an Executor) |
| **RFCs** | `RFC-LAB-000-007` (work environment / toolchain), `RFC-LAB-000-004` (branching), `RFC-LAB-000-014` (multi-executor routing) |
| **Executor role** | **Antigravity (free executor)** — routine/mechanical runner migration, the default class per `RFC-LAB-000-014` cost-first routing. (Kiro IDE is the escalation path only if Antigravity cannot honor the Spec contract.) |
| **Source** | Nexus Pulse Sprint 14 R8 (`COMMAND_SUITE_CONVERGENCE_PLAN.md §8`); Nexus already migrated (PR #64, `69bd5bf`). Cetana owns execution + its own gate. Nothing touches Nexus. |

---

## 1. Introduction

Agni Technologies standardized on **`just`** as the common task runner across repos (Director decision: one shared command vocabulary so a developer jumping between repos types the same `just <recipe>` everywhere; `just` is a purpose-built command runner vs `make` misused as one). **Nexus Pulse already migrated** (Sprint 14: `make` → `just`, 73 recipes, `make` kept as a thin forwarding shim, CI + skills on `just`).

This Spec is the **matching Cetana Labs adoption**: replace Cetana's `Makefile` with a `justfile`, **leading with the shared cross-repo core** (identical recipe names in both repos), append Cetana's repo-specific recipes below the core, and reduce `make` to a pure forwarding shim for one sprint (reversible via `git revert`).

**This is DX/toolchain plumbing** — it touches the runner files, the skills/CI that *call* the runner, and the docs that *document* it. **No application code, no `data/`, no migrations.**

## 0. Preconditions (preflight — enforced by `tasks.md` T0)
- **P1 — Surface:** an Executor clone (default **Antigravity** `cetana-labs-antigravity/`; escalation Kiro IDE `cetana-labs-kiro-ide/`); `git`, `just` (≥ 1.x), Python 3, Node/pnpm on PATH.
- **P2 — Branch:** `chore/adopt-just-task-runner` off up-to-date `main`; clean tree; not `main`. *(Branch type `chore/` per `RFC-LAB-000-004` — a toolchain change, not a feature.)*
- **P3 — Merge-first:** this Spec merged to `main` before the build runs.
- **P4 — Baseline captured:** BEFORE editing, record the outcome of every existing `make` target that will be parity-checked (at minimum `make validate-local`, `make validate-staging`) — this is the **parity oracle** the build must reproduce.

## 2. Current-state facts (verified 2026-10-05 on `main`)
- `Makefile` exists with **20 targets**: the 7 shared-core (`start-local`, `stop-local`, `status-local`, `validate-local`, `validate-staging`, `clean-data`, `help`) + 13 Cetana extras (`setup`, `provision`, `seed`, `web-dev`, `web-build`, `verify-bundle`, `verify-live-frontend`, `deploy-staging`, `deploy-adhoc`, `pb-serve`, `pb-image`, `env-doctor`).
- Every target **delegates to a script or inline command** (`scripts/*.sh`, `scripts/*.py`, `pnpm …`) — the runner is a thin command layer, so recipe bodies port 1:1.
- `make help` greps `## ` docstrings into a cheat-sheet; the `just` equivalent is `just --list` (different format — acceptable, the DoD is "`help` → `@just --list`", not identical output text).
- **No CI workflow invokes `make`** (grep of `.github/` is empty) — so there is **no CI parity gate**; parity is a *local* concern only.
- **3 skills reference `make`** and must be updated to `just`:
  - `.kiro/skills/deploy-adhoc/SKILL.md` — 6 refs (`make deploy-adhoc ENV=… WHAT=…` command examples + prose).
  - `.kiro/skills/spec-run/SKILL.md:62` — `make validate-local`.
  - `.kiro/skills/review-pr/SKILL.md:94` — `make validate-local`.
- `just 1.58.0` is installed (Homebrew) on the work machine; toolchain is Homebrew-managed (`RFC-LAB-000-007`).
- Nexus header convention to mirror: `set shell := ["/bin/bash", "-c"]`, `PYTHON := env_var_or_default(...)`, `default: @just --list`.

## 3. Requirements (EARS acceptance criteria = DoD)

### R1 — The shared cross-repo core (identical names, do NOT rename)
- **R1.1** The `justfile` SHALL define these **7 core recipes with these exact names** (identical to Nexus): `start-local`, `stop-local`, `status-local`, `validate-local`, `validate-staging`, `clean-data`, `help`.
- **R1.2** `help` SHALL be (or alias) `@just --list`; the `justfile` `default:` recipe SHALL also be `@just --list` (so a bare `just` lists recipes).
- **R1.3** The 7 core recipe **bodies** SHALL reproduce the behavior of the current `make` targets of the same name (same scripts/commands, same effect).

### R2 — Cetana's repo-specific recipes (appended below the core)
- **R2.1** The `justfile` SHALL also define Cetana's existing extras below the core block, preserving behavior: `setup`, `provision`, `seed`, `web-dev`, `web-build`, `verify-bundle`, `verify-live-frontend`, `deploy-staging`, `deploy-adhoc`, `pb-serve`, `pb-image`, `env-doctor`.
- **R2.2** Parameterized recipes (`verify-bundle EXPECTED=…`, `verify-live-frontend URL=…`, `deploy-adhoc ENV=… WHAT=…`) SHALL accept their arguments via `just`'s native argument syntax and preserve the same usage/validation semantics (the "usage:" guard on missing required args).
- **R2.3** The `justfile` header SHALL mirror the Nexus convention: `set shell := ["/bin/bash", "-c"]`, a resolved `PYTHON`/`PB`/`CONTAINER` variable layer equivalent to the Makefile's (Homebrew-first with the sandbox-nvm/pocketbase/podman fallbacks preserved), and `default: @just --list`.

### R3 — Parity oracle (the correctness gate)
- **R3.1** `just validate-local` SHALL reproduce the **outcome** of the pre-migration `make validate-local` **exactly** (same checks run, same pass/fail result on the same tree) — verified against the P4 baseline.
- **R3.2** `just validate-staging` SHALL reproduce the pre-migration `make validate-staging` outcome exactly.
- **R3.3** `just --list` SHALL run and list all recipes (core + extras) without error.
- **R3.4** A spot-check of the remaining core recipes (`status-local`, and a dry/safe check of `start-local`/`stop-local`/`clean-data` semantics) SHALL confirm no behavioral regression vs the Makefile targets.

### R4 — `make` reduced to a pure forwarding shim
- **R4.1** The `Makefile` SHALL be reduced to a thin shim that forwards any target to `just`: a catch-all `%:` rule running `@just $@`, `help: @just --list`, `.DEFAULT_GOAL := help`, and a `# DEPRECATED: task logic moved to justfile; forwarding shim for one sprint.` header. *(Mirror the Nexus shim.)*
- **R4.2** After the shim, `make validate-local` SHALL still work by forwarding to `just validate-local` (same outcome). The shim SHALL contain **no task logic** of its own.
- **R4.3** The change SHALL be reversible via `git revert` (the shim is removed, the full Makefile restored, in one revert).

### R5 — Update every `make` reference (skills + CI + docs)
- **R5.1** `.kiro/skills/deploy-adhoc/SKILL.md`, `.kiro/skills/spec-run/SKILL.md`, `.kiro/skills/review-pr/SKILL.md` SHALL have their `make <target>` references rewritten to `just <recipe>` (preserving argument syntax — `just deploy-adhoc ENV=… WHAT=…`, `just validate-local`).
- **R5.2** IF any `.github/` workflow invokes `make` (none found at authoring time — re-confirm at build), it SHALL be updated to `just` and CI SHALL remain green.
- **R5.3** `AGENTS.md` (toolchain/§Key commands) and `.kiro/steering/tech.md` (Key commands) and `docs/guides/developer-guide.md` SHALL document `just` + `just --list` as the task runner (noting the one-sprint `make` shim and the cross-repo shared-core rationale).

### R6 — Scope floor (no overreach)
- **R6.1** The build SHALL touch **only** runner files (`justfile`, `Makefile`), the 3 named skills (+ any CI/doc files enumerated in R5), and the Spec's own `REPORT.md`. **No app code, no `data/`, no migrations, no `scripts/*` logic changes** (recipes call the *same* scripts unchanged).

### R7 — Cross-repo tracking
- **R7.1** On merge, `CHANGELOG.md` `[Unreleased]` SHALL record the `just` adoption and note the Agni `just` standard is now complete across repos (Nexus ✅ + Cetana ✅).
- **R7.2** The sprint tracker row (`TSK-066`) and backlog (`BK-025`) SHALL be updated to Done/Delivered.
- **R7.3** *(Note, not a build task)* A dedicated cross-repo **convergence ledger** (`docs/governance/CONVERGENCE-LEDGER.md`) does **not** yet exist in Cetana. Adoption is tracked via CHANGELOG + tracker for now; building the ledger is a separate, Director-approved follow-up (see Decision Journal) — out of this Spec's scope.

## 4. Out of scope
- Any change to `scripts/*` behavior (recipes call the same scripts).
- Deleting the `Makefile` (it stays as a shim for one sprint; removal is a later cleanup).
- Building the cross-repo convergence ledger (separate follow-up, R7.3).
- Any Nexus Pulse change (that repo already migrated).
- Renaming the 7 core recipes (the whole point is identical names — forbidden).

## 5. Human Verification Plan
1. **`just --list`** runs and shows all recipes (7 core at the top, then Cetana extras) — R1, R2, R3.3.
2. **Parity:** on a clean tree, `just validate-local` produces the **same outcome** as the baseline `make validate-local` captured in P4 (both pass, same checks) — R3.1. Same for `just validate-staging` — R3.2.
3. **Core names match Nexus:** diff the 7 core recipe names against Nexus's justfile — identical, no renames — R1.1.
4. **Shim works + is pure:** `make validate-local` still works (forwards to `just`); the Makefile contains only the catch-all forward + help, no task logic — R4.1, R4.2.
5. **References updated:** grep the repo for `make ` in skills/CI/docs — only intended/historical mentions remain; the 3 named skills now say `just` — R5.1.
6. **Reversible:** confirm `git revert <merge>` cleanly restores the full Makefile and removes the shim — R4.3.
7. **Scope:** the PR diff is runner files + 3 skills (+ enumerated docs) only — no app/`data`/scripts-logic changes — R6.1.
