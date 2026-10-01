# Push-Changes Skills — Requirements

| Property | Value |
| :--- | :--- |
| **Spec ID** | `push-changes-skills` |
| **Feature** | Two new project skills — `/push-changes` and `/commit-and-push-changes` — that extend `/commit-changes` with a **branch-aware** push, honoring the hybrid path-scoped branching model |
| **Backlog** | `BK-` (process tooling / DX) — SPRINT-TBD |
| **Status** | 🟡 Proposed (contract authored on KiroCrew Operator; execution on Kiro IDE Executor) |
| **RFCs** | `RFC-LAB-000-004` (branching model — the governing constraint), `RFC-LAB-000-007` (surface roles), `RFC-LAB-000-009` (sprint lifecycle) |
| **Executor role** | Delegated-agent / onboarded-dev |

---

## 1. Introduction

`/commit-changes` today stops at `git commit` — its documented step 3 names a `git push origin main`, but the skill as written leaves pushing to the operator. This Spec adds two companion skills that **own the push step explicitly**, while refusing to let a one-liner violate the branching model (`RFC-LAB-000-004`):

- **`/push-changes`** — push already-committed work on the **current branch** to its remote.
- **`/commit-and-push-changes`** — commit (reusing `/commit-changes` prefix rules) **then** push, in one invocation.

**This is DX plumbing, not a product feature** — it adds two `.kiro/skills/*/SKILL.md` procedures and touches no application code, `data/`, or migrations.

## 0. Preconditions (preflight — verify BEFORE any change; enforced by `tasks.md` T0)

- **P1 — Surface:** Kiro **IDE / local** (Executor). `/env-doctor` IDE-ready (git configured, remote reachable).
- **P2 — Branch:** `feat/push-changes-skills` off up-to-date `main`; clean tree; not `main`/`master`.
- **P3 — Merge-first:** this Spec merged to `main` before `/spec-run`.
- **P4 — Baseline green:** `/validate-local` passes before changes (no pre-existing drift attributed to this Spec).

## 2. Current-state facts (of record — verified)

- **`/commit-changes`** (`.kiro/skills/commit-changes/SKILL.md`) stages, selects a standardized prefix (`feat(lab-XXX)` / `log` / `status` / `chore` / `docs:`), commits, and lists `git push origin main` as step 3 — but the agent treats the push as a separate, human-gated action.
- **Branching model (`RFC-LAB-000-004`, hybrid path-scoped):** application code / `data/` / migrations MUST land via **PR + green CI + squash-merge** on a `feat/|fix/|chore/|refactor/` branch; **governance / docs** (`STATUS.md`, journals, `SPRINT_TRACKER.md`, `BACKLOG.md`, `CHANGELOG.md`, `README.md`, `docs/**`) MAY fast-path directly to `main`. **Never force-push `main`.**
- **Runtime guard:** the KiroCrew runtime blocks `git push` to protected branches (`main`/`master`) and bare/`HEAD`/`--all`/`--mirror`/force-push forms; a feature-branch push must name the branch explicitly (`git push origin <feature-branch>`).
- **No existing `/push-changes` or `/commit-and-push-changes`** skill (verified: 26 skills on disk, neither present).

## 3. Requirements (EARS acceptance criteria = Definition of Done)

### R1 — `/push-changes` skill (push the current branch)
- **R1.1** The system SHALL add `.kiro/skills/push-changes/SKILL.md` with YAML frontmatter (`name`, `description`) matching the repo's skill convention.
- **R1.2** The skill SHALL determine the **current branch** and push it to its remote by **explicit name** (`git push origin <current-branch>`, with `-u` when no upstream is set) — never a bare `git push`.
- **R1.3** WHEN the current branch is a protected branch (`main`/`master`), the skill SHALL proceed ONLY after confirming the staged/committed paths are **governance/docs** (fast-path eligible per `RFC-LAB-000-004`), AND SHALL require explicit operator confirmation before the push; IF the paths include application code / `data/` / migrations, it SHALL REFUSE and instruct moving the work to a `feat/` branch + PR.
- **R1.4** The skill SHALL NEVER force-push, and SHALL NEVER push `--all`/`--mirror` or a `HEAD`/`@` target.
- **R1.5** IF there is nothing to push (branch up to date with remote), the skill SHALL report that and exit cleanly (no error).

### R2 — `/commit-and-push-changes` skill (commit then push)
- **R2.1** The system SHALL add `.kiro/skills/commit-and-push-changes/SKILL.md` with conforming frontmatter.
- **R2.2** The skill SHALL perform the full `/commit-changes` procedure first (inspect status, verify no secrets/`.env`/`.idea/` staged, select the standardized commit prefix, commit) and THEN invoke the `/push-changes` logic (R1).
- **R2.3** It SHALL inherit **all** of R1's branch-awareness and refusal rules — a code change on `main` is refused at the push step even though the commit succeeded locally.
- **R2.4** The skill SHALL cross-reference `/commit-changes` and `/push-changes` rather than duplicating their rules verbatim (single source of behavior).

### R3 — Secrets & hygiene discipline (inherited)
- **R3.1** Neither skill SHALL stage or push secrets, `.env*`, or `.idea/`; both SHALL echo the staged file list for operator inspection before committing (per `/commit-changes` step 1).
- **R3.2** Both skills SHALL preserve git hooks (no `--no-verify`) unless the operator explicitly asks to skip them.

### R4 — Documentation lockstep
- **R4.1** `AGENTS.md §4` (skills suite) SHALL list the two new skills under the lifecycle/governance tooling.
- **R4.2** The living working-model diagram (artifact `fd26dcf5ca990145`) SHALL be updated to show the two skills on the Operator surface. *(Operator-side follow-up; not a `/spec-run` task — noted here for lockstep.)*

### R5 — No regression
- **R5.1** `/commit-changes` SHALL remain unchanged in behavior (the new skills compose with it, do not rewrite it).
- **R5.2** `/validate-local` SHALL pass unchanged after the skills are added (skills are markdown; no validator pillar regresses).

## 4. Out of scope

- Any change to `/commit-changes` itself (it stays commit-only).
- PR creation/automation (that remains the Executor's `/spec-run` + the human gate).
- Branch-protection enforcement on the remote (deferred until the repo transfers to the org account, per `RFC-LAB-000-004`).

## 5. Human Verification Plan

1. On a `feat/` branch with a committed change, run `/push-changes` → confirm it pushes the named branch and sets upstream.
2. On `main` with a **docs-only** commit, run `/push-changes` → confirm it asks for confirmation, then pushes.
3. On `main` with a **code** change staged, run `/commit-and-push-changes` → confirm it commits but **refuses** the push with the `feat/`+PR instruction.
4. Confirm `/commit-changes` behavior is unchanged.
