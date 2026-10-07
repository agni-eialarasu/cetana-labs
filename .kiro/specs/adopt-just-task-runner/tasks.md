# Adopt `just` Task-Runner — Tasks

| Property | Value |
| :--- | :--- |
| **Spec ID** | `adopt-just-task-runner` |
| **Branch** | `chore/adopt-just-task-runner` (self-created by the build; off up-to-date `main`) |
| **Execution** | **Antigravity Executor** (clone `cetana-labs-antigravity/`) — routine/mechanical, cost-first default per `RFC-LAB-000-014`. Escalate to Kiro IDE only if the contract can't be honored (record why). |

---

## T0 — Preflight + baseline (STOP on failure)  → P1–P4
- [ ] Surface = an Executor clone; `git`, `just`, Python 3, Node/pnpm on PATH. *(P1)*
- [ ] This Spec is merged to `main` (merge-first). *(P3)*
- [ ] Create `chore/adopt-just-task-runner` off up-to-date `main`; clean tree; not `main`. *(P2)*
- [ ] **Capture the parity baseline (P4):** on the clean checkout, run `make validate-local` and `make validate-staging`; record the outcome (pass/fail + checks run) in `REPORT.md`. This is the oracle T4 reproduces.

## T1 — Author the `justfile` core + extras  → R1, R2
- [ ] Create `justfile` with the Nexus header convention (`set shell`, resolved `PYTHON`/`PB`/`CONTAINER`, `default: @just --list`). *(R2.3)*
- [ ] Define the **7 shared-core recipes** with exact Nexus names, bodies porting the Makefile targets 1:1: `start-local`, `stop-local`, `status-local`, `validate-local`, `validate-staging`, `clean-data`, `help` (→ `@just --list`). **Do NOT rename.** *(R1.1–R1.3)*
- [ ] Define the Cetana extras below the core (`setup`, `provision`, `seed`, `web-dev`, `web-build`, `verify-bundle`, `verify-live-frontend`, `deploy-staging`, `deploy-adhoc`, `pb-serve`, `pb-image`, `env-doctor`), preserving behavior + the `usage:`/`exit 2` guards on parameterized recipes. *(R2.1, R2.2)*
- [ ] Preserve the nvm-source guard inside node recipes + the `clean-data` `sleep 3` abort window.

## T2 — Reduce `Makefile` to a forwarding shim  → R4
- [ ] Replace the Makefile body with the shim: `.DEFAULT_GOAL := help`, DEPRECATED header, `help: @just --list`, catch-all `%: @just $@`, `.PHONY: help`. No task logic retained. *(R4.1)*
- [ ] Confirm `make validate-local` forwards to `just validate-local` with the same outcome. *(R4.2)*

## T3 — Repoint every `make` caller  → R5
- [ ] `.kiro/skills/deploy-adhoc/SKILL.md` — rewrite the 6 `make deploy-adhoc …` refs to `just deploy-adhoc …` (preserve `ENV=`/`WHAT=` arg style). *(R5.1)*
- [ ] `.kiro/skills/spec-run/SKILL.md:62` + `.kiro/skills/review-pr/SKILL.md:94` — `make validate-local` → `just validate-local`. *(R5.1)*
- [ ] Re-grep `.github/` for `make `; repoint any workflow caller + keep CI green (none at authoring time). *(R5.2)*
- [ ] Docs: `AGENTS.md` (§Toolchain + §Key commands), `.kiro/steering/tech.md` (§Key commands), `docs/guides/developer-guide.md` — document `just` + `just --list`, the one-sprint `make` shim, and the shared-core cross-repo rationale. *(R5.3)*

## T4 — Parity + scope self-validate  → R3, R6
- [ ] **Parity oracle:** `just validate-local` reproduces the P4 `make validate-local` outcome **exactly**; `just validate-staging` likewise. Record both in `REPORT.md`. *(R3.1, R3.2)*
- [ ] `just --list` lists all recipes without error; spot-check `status-local` + the safe semantics of `start-local`/`stop-local`/`clean-data`. *(R3.3, R3.4)*
- [ ] Diff the 7 core recipe **names** against Nexus's justfile — identical, zero renames. *(R1.1)*
- [ ] Confirm scope: PR diff = runner files + 3 skills + enumerated docs only; no app/`data`/`scripts/*`-logic changes. *(R6.1)*
- [ ] Walk R1–R7 against the diff; note any gaps in `REPORT.md`.

## T5 — Cross-repo tracking lockstep  → R7
- [ ] `CHANGELOG.md` `[Unreleased]`: record the `just` adoption; note the Agni `just` standard is now complete across repos (Nexus ✅ + Cetana ✅). *(R7.1)*
- [ ] Update `SPRINT_TRACKER.md` `TSK-066` + `BACKLOG.md` `BK-025` toward Done/Delivered. *(R7.2)*
- [ ] Do **not** build the convergence ledger (R7.3 — separate follow-up).

## T6 — Open PR (STOP-and-hold; never merge)
- [ ] Push `chore/adopt-just-task-runner`; open the PR via `gh api` (REST, per AGENTS.md). STOP for human verification (`/verification-done`) → `/review-pr` → the human gate. Never merge.
