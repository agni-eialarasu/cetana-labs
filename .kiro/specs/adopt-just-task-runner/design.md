# Adopt `just` Task-Runner — Design

| Property | Value |
| :--- | :--- |
| **Spec ID** | `adopt-just-task-runner` |
| **Approach** | Port the Makefile's 20 targets to a `justfile` (core-first), reduce Makefile to a forwarding shim, repoint callers (skills/CI/docs). Behavior-preserving — recipes call the same scripts. |

---

## 1. Why `just`, why core-first

- **Decision (Director):** one shared command vocabulary across all Agni repos so developers don't relearn commands per repo. `just` is a purpose-built runner (clean recipes, real args, auto `just --list`) vs `make` misused as a task runner. Nexus Pulse already migrated (Sprint 14).
- **Core-first** so the 7 recipes a developer uses most (`start-local`, `validate-local`, …) are **byte-identical in name** across Nexus + Cetana. Repo-specific extras live below the core and may differ per repo — that's fine; the *core* is the contract.

## 2. The `justfile` structure (mirror Nexus header convention)

```just
# Cetana Labs — just task runner (RFC-LAB-000-007). Shared Agni core first; Cetana extras below.
set shell := ["/bin/bash", "-c"]

# --- resolved toolchain vars (mirror the Makefile's; Homebrew-first with sandbox fallbacks) ---
PYTHON := env_var_or_default("PYTHON", "python3")
# PB: prefer a system binary (brew pocketbase/pb) else the fetched local one
# CONTAINER: podman-first, docker fallback (RFC-LAB-000-007 §2.3)
# NVM shim: in cloud sandboxes where node lives under nvm, source it inside the recipe (preserve the Makefile's $(NVM) guard)

default:
    @just --list

# ============================================================
# SHARED AGNI CORE — identical recipe names across all repos. DO NOT RENAME.
# ============================================================
help:
    @just --list

start-local:    # /start-local — PocketBase :8090 + SvelteKit :5173
    ...

stop-local:     ...
status-local:   ...
validate-local: ...
validate-staging: ...
clean-data:     ...

# ============================================================
# CETANA-SPECIFIC RECIPES (below the core; may differ per repo)
# ============================================================
setup: ...
provision: ...
seed: ...
web-dev: ...
web-build: ...
verify-bundle EXPECTED FORBIDDEN="": ...
verify-live-frontend URL EXPECTED="": ...
deploy-staging: ...
deploy-adhoc ENV WHAT="all": ...
pb-serve: ...
pb-image: ...
env-doctor: ...
```

### Porting notes (the few non-trivial 1:1 translations)
- **Toolchain vars:** the Makefile uses `$(shell …)` for `PB`/`CONTAINER` and a `$(NVM)` inline guard. In `just`, resolve `PB`/`CONTAINER` with backtick command-substitution assignments or inside the recipe body; keep the nvm-source guard **inside** the recipes that need node (`start-local`, `web-dev`, `web-build`, `env-doctor`) exactly as the Makefile does — do not drop the sandbox fallback.
- **Parameterized recipes:** Makefile `make verify-bundle EXPECTED=<url>` → just `verify-bundle EXPECTED FORBIDDEN=""` called as `just verify-bundle <url> [forbidden]` **or** keep `EXPECTED=`-style via a positional+default. Preserve the `usage:`/`exit 2` guard on a missing required arg (R2.2).
- **`help` format:** `just --list` replaces the Makefile's hand-rolled `grep … awk` cheat-sheet. Different layout, same intent — acceptable (R1.2). Keep a one-line recipe doc-comment (`# …`) on each recipe so `just --list` shows a useful description.
- **`clean-data` safety:** preserve the `sleep 3` abort window + the "removes pb_data" warning.

## 3. The Makefile shim (after porting)

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
Any `make <target>` now forwards to `just <target>` — zero task logic retained (R4.1/R4.2). Reversible: `git revert` of the merge restores the full Makefile (R4.3).

## 4. Caller repointing (R5)
- **Skills:** `deploy-adhoc` (6 refs → `just deploy-adhoc ENV=… WHAT=…`), `spec-run:62` + `review-pr:94` (`make validate-local` → `just validate-local`). Keep argument style working under `just`.
- **CI:** none invoke `make` today — re-grep `.github/` at build; if a workflow is added before build that calls `make`, repoint + keep CI green (R5.2). (The Makefile shim means even a missed CI caller still works — but repoint for clarity.)
- **Docs:** `AGENTS.md` §Toolchain + §Key commands, `.kiro/steering/tech.md` §Key commands, `docs/guides/developer-guide.md` — document `just` + `just --list`, note the one-sprint `make` shim and the shared-core cross-repo rationale.

## 5. The parity oracle (R3 — the real correctness mechanism)
Before any edit (T0/P4), capture the baseline: run `make validate-local` and `make validate-staging` on the clean checkout and record pass/fail + which checks ran. After porting, `just validate-local`/`just validate-staging` MUST reproduce that outcome **exactly**. This is the single most important check — a runner migration is correct iff the gated outcomes are unchanged. The Makefile shim is a safety net (old callers still work during the transition), not a substitute for parity.

## 6. Risks & mitigations
- **Risk: `just` arg syntax differs from `make`'s `VAR=val`.** → `just` supports both positional args and `just recipe VAR=val` assignment; pick whichever keeps the skill call sites readable, and update the skills to match. Mitigation: the `usage:` guard (R2.2) fails loudly if an arg is missing.
- **Risk: nvm/PATH differences between the Antigravity sandbox and the work Mac.** → preserve the Makefile's nvm-source guard verbatim inside node recipes; the baseline is captured on the build surface so parity is judged there.
- **Risk: Antigravity can't honor the Spec contract (branch/PR/REPORT, reads `.kiro/`).** → escalate to Kiro IDE (RFC-014 escalation path); record the reason. The Spec is executor-agnostic by design.
