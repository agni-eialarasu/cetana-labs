---
name: push-changes
description: Pushes already-committed work on the CURRENT branch to its remote by explicit branch name, enforcing the hybrid path-scoped branching model (RFC-LAB-000-004) — refuses code/data/migration pushes to main, validates docs fast-path, never force-pushes.
---

# Skill: Push Changes (`/push-changes`)

## Objective
Push **already-committed** work on the **current branch** to its remote, honoring the hybrid path-scoped branching model (`RFC-LAB-000-004`). This skill owns the push step that `/commit-changes` deliberately leaves out, and it makes the runtime's protected-branch guard **predictable** — it explains *before* it refuses, rather than letting the operator hit a raw policy block.

**This is DX plumbing, not a product feature.** It runs `git push` with a decision gate; it touches no application code, `data/`, or migrations.

---

## Trigger Patterns
- `/push-changes`
- "push the current branch", "push my commits", "push this work"

---

## The branch-aware push gate (single source of behavior)

This gate is the authority both `/push-changes` and `/commit-and-push-changes` route through before any `git push`.

```text
current = git rev-parse --abbrev-ref HEAD

IF current in {main, master}:
    changed = paths in the commits not yet on origin/<current>  (git diff --name-only origin/<current>..HEAD)
    IF changed ⊆ {governance/docs}:
        → fast-path eligible (RFC-004), BUT the agent CANNOT push to main.
          Validate eligibility, then PRINT the exact `git push origin main`
          command for the HUMAN to run. Do not attempt it.
    ELSE (code / data/ / migrations present):
        → REFUSE. Instruct: move the work to a feat/ branch + PR. Do NOT push.
ELSE (feat/|fix/|chore/|refactor/ branch):
    → git push origin <current>  (add -u if no upstream). No confirmation needed.

NEVER: --force / --force-with-lease to a protected branch, --all, --mirror,
       bare `git push`, or a HEAD/@ target.
IF up-to-date with remote: report "nothing to push" and exit cleanly (no error).
```

### Governance/docs fast-path set (per `RFC-LAB-000-004`)
`STATUS.md` · `journal.md` · `SPRINT_TRACKER.md` · `BACKLOG.md` · `CHANGELOG.md` · `README.md` · `docs/**` · other governance `*.md`.
Anything under application code, `data/` (relational masters/schemas), or `pb_migrations/` is **NOT** fast-path eligible and MUST go via a `feat/` branch + PR.

### Why the agent prints the `main` command instead of pushing it
The KiroCrew runtime enforces an **absolute** protected-branch floor (`git-publish-push-protected-branch-name`) that no operator confirmation in chat can lift. So even for a legitimately fast-path-eligible docs commit on `main`, the agent **validates eligibility and hands the human the exact command** to run (terminal, GitHub Desktop, or an IDE Executor session). On a `feat/` branch there is no such floor — the agent pushes directly.

---

## Step-by-Step Procedure

1. **Determine the current branch and what would push**:
   ```bash
   current=$(git rev-parse --abbrev-ref HEAD)
   git status --short --branch
   git log --oneline origin/"$current".."$current" 2>/dev/null || git log --oneline -5
   git diff --name-only origin/"$current"..HEAD 2>/dev/null
   ```
   - If the branch is up to date with its remote (nothing in `origin/<branch>..HEAD`): **report "nothing to push" and exit cleanly** (R1.5). Do not error.
   - If there is no upstream yet, the full local history is "to push" — that is expected for a new `feat/` branch.

2. **Run the branch-aware push gate (above)**:
   - **On a `feat/`|`fix/`|`chore/`|`refactor/` branch** → go to step 3 (push directly, no confirmation).
   - **On `main`/`master` with ONLY governance/docs paths** → the commit is fast-path-legal, but the agent cannot push to `main`. **Print the exact command for the human** and STOP:
     ```bash
     git push origin main
     ```
     Tell the operator: "This docs/governance commit is fast-path-eligible (RFC-004). I can't push to `main` myself (protected-branch floor) — run the command above in your terminal / GitHub Desktop / an IDE session."
   - **On `main`/`master` with ANY code / `data/` / migration path** → **REFUSE** and instruct:
     > "This change includes application code / `data/` / migrations, which must land via a `feat/` branch + PR with green CI (RFC-LAB-000-004). I won't push it to `main`. Move it to a branch:
     > `git switch -c feat/<slug>` then `git push -u origin feat/<slug>`, and open a PR."

3. **Push by explicit branch name** (feature branches only):
   ```bash
   # if no upstream is set yet:
   git push -u origin "$current"
   # if an upstream already exists:
   git push origin "$current"
   ```
   - **NEVER** `git push --force` / `--force-with-lease` to a protected branch, **never** `--all`/`--mirror`, **never** a bare `git push`, and **never** a `HEAD`/`@` target (R1.4).
   - Preserve git hooks — **no `--no-verify`** unless the operator explicitly asks to skip them.

4. **Report the result**:
   - Confirm the pushed ref and the remote URL (`git remote get-url origin`), and surface the branch's PR-open hint if this is a `feat/` branch (open the PR via `gh api` per `/spec-run` / the human gate — this skill does not open PRs).

---

## Rules
- **Push the current branch by explicit name** — never a bare `git push`, never `--all`/`--mirror`/`HEAD` (R1.2, R1.4).
- **Never force-push**, and never force-push a protected branch under any circumstance (R1.4).
- **`main`/`master` guard (R1.3):** code / `data/` / migrations ⇒ **refuse** with the `feat/`+PR instruction; governance/docs ⇒ validate fast-path eligibility and **print the `git push origin main` command for the human** (the agent cannot push `main`).
- **Nothing to push ⇒ clean exit** (R1.5), not an error.
- **Secrets & hygiene:** never push a branch whose commits stage secrets, `.env*`, or `.idea/`; this is inherited from `/commit-changes` (see that skill's step 1).
- **Preserve hooks** (no `--no-verify`) unless explicitly asked.
- This skill **pushes only** — it does not commit (use `/commit-changes` or `/commit-and-push-changes`) and does not open PRs.
