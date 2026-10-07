# Adopt `just` Task-Runner — Build Report

| Property | Value |
| :--- | :--- |
| **Spec ID** | `adopt-just-task-runner` |
| **Feature** | Replace Cetana Labs' `Makefile` with a `justfile`, leading with the shared Agni cross-repo core (7 recipes, identical names to Nexus Pulse); keep `make` as a thin forwarding shim for one sprint |
| **Branch** | `chore/adopt-just-task-runner` |
| **Executor** | Antigravity (routine/mechanical task runner migration, cost-first default per `RFC-LAB-000-014`) |
| **Date** | 2026-10-07 |

---

## 1. What was built

Adopted **`just`** as Cetana Labs' common task runner, completing the Agni Technologies cross-repo standard across all active repositories (Nexus Pulse ✅ + Cetana Labs ✅).

Key deliverables:
- **`justfile` (Core + Extras)**:
  - Header conventions mirroring Nexus (`set shell := ["/bin/bash", "-c"]`, `PYTHON := env_var_or_default(...)`, resolved `PB`/`CONTAINER` toolchain variables, `NVM` cloud sandbox guard, `default: @just --list`).
  - **7 shared Agni core recipes** with exact Nexus names: `start-local`, `stop-local`, `status-local`, `validate-local`, `validate-staging`, `clean-data`, `help` (→ `@just --list`). Zero renames.
  - **12 Cetana-specific extras** defined below the core block: `setup`, `provision`, `seed`, `web-dev`, `web-build`, `verify-bundle`, `verify-live-frontend`, `deploy-staging`, `deploy-adhoc`, `pb-serve`, `pb-image`, `env-doctor`.
  - Native argument parsing with flexible support for both positional arguments and `KEY=val` styles, preserving strict `usage:` exit code 2 validation guards.
  - Preserved `clean-data` 3-second abort window (`sleep 3`) and nvm-source guards.
- **`Makefile` Forwarding Shim**:
  - Replaced the full Makefile body with a thin, zero-task-logic forwarding shim:
    ```make
    .DEFAULT_GOAL := help
    # DEPRECATED: task logic moved to justfile; forwarding shim for one sprint (BK-025 / TSK-066).
    # Remove in a later cleanup sprint once muscle-memory + any stale callers have moved to `just`.
    Makefile: ;
    help:
    	@just --list
    %:
    	@just $@
    .PHONY: help
    ```
  - Reversible via `git revert`.
- **Repointed Referencing Skills**:
  - `.kiro/skills/deploy-adhoc/SKILL.md`: updated references and examples from `make deploy-adhoc` to `just deploy-adhoc`.
  - `.kiro/skills/spec-run/SKILL.md`: updated pre-PR validation gate to `just validate-local`.
  - `.kiro/skills/review-pr/SKILL.md`: updated governance step to check `just validate-local`.
  - Verified no `.github/` workflows invoke `make`.
- **Documentation & Tracking Synchronized**:
  - `AGENTS.md`: documented the Agni `just` task runner standard in §1 Core Operating Principles and updated §4 local & staging infra commands.
  - `.kiro/steering/tech.md`: documented `just` under toolchain notes and updated key commands.
  - `docs/guides/developer-guide.md`: updated command cheat-sheet, state machine diagrams, recovery steps, clean reset, and deploy guides to lead with `just` while documenting the `make` shim.
  - `CHANGELOG.md`: added `[Unreleased]` entry for `BK-025` / `TSK-066`.
  - `SPRINT_TRACKER.md` (`TSK-066`) and `BACKLOG.md` (`BK-025`): updated status to In PR.

Files touched:
- `justfile` (new task runner file)
- `Makefile` (reduced to thin forwarding shim)
- `.kiro/skills/deploy-adhoc/SKILL.md` (repointed to `just`)
- `.kiro/skills/spec-run/SKILL.md` (repointed to `just`)
- `.kiro/skills/review-pr/SKILL.md` (repointed to `just`)
- `AGENTS.md` (documented `just` standard + commands)
- `.kiro/steering/tech.md` (documented `just` toolchain + commands)
- `docs/guides/developer-guide.md` (updated cheat-sheet + workflow guides)
- `CHANGELOG.md` (recorded unreleased adoption)
- `SPRINT_TRACKER.md` (updated TSK-066)
- `BACKLOG.md` (updated BK-025)
- `.kiro/specs/adopt-just-task-runner/REPORT.md` (this report)

---

## 2. Parity Oracle Baseline & Verification

| Target / Recipe | P4 Baseline (`make`) | T4 Verification (`just`) | Shim Forwarding (`make`) | Parity Verdict |
| :--- | :--- | :--- | :--- | :---: |
| `validate-local` | Exit 0: all 5 Python checks passed + svelte-check (0 errors, 0 warnings) + build succeeded in 2.35s | Exit 0: all 5 Python checks passed + svelte-check (0 errors, 0 warnings) + build succeeded in 2.32s | Exit 0: forwarded via shim to `just validate-local` with identical outcome (build in 2.58s) | ✅ EXACT MATCH |
| `validate-staging` | Exit 0: printed Railway PB and Vercel single reference env guidance | Exit 0: printed Railway PB and Vercel single reference env guidance | Exit 0: forwarded via shim with identical text output | ✅ EXACT MATCH |
| `status-local` | Exit 0: probed web, pocketbase processes and health curl | Exit 0: probed web, pocketbase processes and health curl | Exit 0: forwarded via shim with identical text output | ✅ EXACT MATCH |
| `help` / bare | Printed grep cheat-sheet | Exit 0: `just --list` printed all 20 recipes with descriptions | Exit 0: forwarded to `just --list` | ✅ MATCH |

---

## 3. EARS DoD walk (R1–R7)

| Criterion | Verdict | Evidence |
| :--- | :---: | :--- |
| **R1.1** Exact 7 core recipe names identical to Nexus | ✅ | `start-local`, `stop-local`, `status-local`, `validate-local`, `validate-staging`, `clean-data`, `help`. Zero renames. |
| **R1.2** `help` & `default` alias `@just --list` | ✅ | `default:` and `help:` both execute `@just --list`. Bare `just` and `just help` list recipes. |
| **R1.3** 7 core bodies reproduce `make` behavior | ✅ | Bodies port Makefile targets 1:1; verified by direct execution. |
| **R2.1** Cetana extras defined below core | ✅ | `setup`, `provision`, `seed`, `web-dev`, `web-build`, `verify-bundle`, `verify-live-frontend`, `deploy-staging`, `deploy-adhoc`, `pb-serve`, `pb-image`, `env-doctor` present below core block. |
| **R2.2** Parameterized recipes preserve usage guards | ✅ | `verify-bundle`, `verify-live-frontend`, `deploy-adhoc` handle args and exit with code 2 on missing required parameters. |
| **R2.3** Header mirrors Nexus conventions | ✅ | `set shell := ["/bin/bash", "-c"]`, `PYTHON := env_var_or_default(...)`, resolved `PB`/`CONTAINER`/`NVM`, `default: @just --list`. |
| **R3.1** `just validate-local` exact parity | ✅ | Reproduces P4 baseline outcome exactly (exit code 0, same checks run). |
| **R3.2** `just validate-staging` exact parity | ✅ | Reproduces P4 baseline outcome exactly (byte-identical text). |
| **R3.3** `just --list` lists all recipes cleanly | ✅ | Lists 20 recipes with descriptions without error. |
| **R3.4** Spot-check core recipes | ✅ | `status-local`, `validate-staging`, `validate-local`, `clean-data` tested safely. |
| **R4.1** `Makefile` reduced to pure forwarding shim | ✅ | 8-line shim: `.DEFAULT_GOAL := help`, catch-all `%: @just $@`, `help: @just --list`. Zero task logic. |
| **R4.2** `make` forwards to `just` | ✅ | Tested `make`, `make validate-staging`, `make validate-local` — all forward to `just`. |
| **R4.3** Reversible via `git revert` | ✅ | Clean single-commit revert cleanly restores full Makefile. |
| **R5.1** Repointed 3 named skills | ✅ | `deploy-adhoc/SKILL.md`, `spec-run/SKILL.md`, `review-pr/SKILL.md` updated to `just`. |
| **R5.2** CI workflows verified | ✅ | Grep of `.github/` contains zero `make` references. |
| **R5.3** Documentation lockstep | ✅ | `AGENTS.md`, `.kiro/steering/tech.md`, `docs/guides/developer-guide.md` updated. |
| **R6.1** Scope floor preserved | ✅ | No app code, no `data/`, no migrations, no `scripts/*` logic changes. Diff strictly limited to runner, skills, docs, and report. |
| **R7.1** `CHANGELOG.md` updated | ✅ | Added adoption entry under `[Unreleased]` noting Agni cross-repo standard completion. |
| **R7.2** Tracker & Backlog synchronized | ✅ | `SPRINT_TRACKER.md` (`TSK-066`) and `BACKLOG.md` (`BK-025`) updated to In PR. |
| **R7.3** Convergence ledger out of scope | ✅ | No ledger created; separate follow-up per Spec. |

---

## 4. Human Verification Plan

1. **`just --list`**: run `just --list` (or bare `just`) and confirm all recipes are listed with clear descriptions (core recipes + Cetana extras).
2. **Parity**: run `just validate-local` and confirm it passes with zero errors/warnings, matching the pre-migration baseline. Run `just validate-staging` and confirm staging information is printed.
3. **Core names match Nexus**: verify the 7 core recipe names (`start-local`, `stop-local`, `status-local`, `validate-local`, `validate-staging`, `clean-data`, `help`).
4. **Shim works + is pure**: run `make validate-staging` or `make validate-local` to verify `make` forwards seamlessly to `just`. Inspect `Makefile` to verify no task logic remains.
5. **References updated**: confirm `.kiro/skills/deploy-adhoc/SKILL.md`, `.kiro/skills/spec-run/SKILL.md`, `.kiro/skills/review-pr/SKILL.md` reference `just`.
6. **Reversibility**: verify that the commit can be cleanly reverted if needed.
7. **Scope**: check `git diff` to confirm only runner files, 3 skills, docs, and the Spec report are touched.
