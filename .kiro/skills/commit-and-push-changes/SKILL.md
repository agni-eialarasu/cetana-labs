---
name: commit-and-push-changes
description: Commits changed files (reusing /commit-changes prefix + secret-hygiene rules) and THEN pushes via the /push-changes branch-aware gate — in one invocation. Inherits all branch-awareness: a code change on main is refused at the push step even after the local commit succeeds.
---

# Skill: Commit and Push Changes (`/commit-and-push-changes`)

## Objective
Do a commit **and** a push in one invocation: run the full `/commit-changes` procedure, then route the result through the `/push-changes` branch-aware gate. This composes the two parent skills — it does **not** restate their rules.

**This is DX plumbing, not a product feature.** No application code, `data/`, or migrations are touched.

---

## Trigger Patterns
- `/commit-and-push-changes`
- "commit and push", "commit then push my changes"

---

## Procedure (compose, don't duplicate)

1. **Commit half → run [`/commit-changes`](../commit-changes/SKILL.md)** exactly as documented:
   - Inspect `git status`; verify **no secrets, `.env*`, or `.idea/`** are staged (echo the staged file list for operator inspection).
   - Select the standardized commit prefix (`feat(lab-XXX)` / `log(lab-XXX)` / `status(lab-XXX)` / `chore(lab-XXX)` / `docs:` / `feat(governance)` …).
   - Commit. **Preserve hooks** (no `--no-verify`) unless the operator explicitly asks to skip them.

2. **Push half → run [`/push-changes`](../push-changes/SKILL.md)** — route through its **branch-aware push gate** (the single source of push behavior). This is where branch-awareness is enforced: a successful local commit does **not** guarantee a push.

> **Single source of behavior:** the commit rules live in `/commit-changes`; the push gate (fast-path set, refusals, force-push ban, nothing-to-push) lives in `/push-changes`. This skill only sequences them (R2.4). Do not copy their rules here — follow the linked skills.

---

## Worked examples (one per gate path)

### A. `feat/` branch — commit + push directly
```text
On feat/add-widget with a code change staged:
  1. /commit-changes → commit "feat(lab-003): add widget export button"
  2. /push-changes   → git push -u origin feat/add-widget   (no confirmation needed)
Result: committed and pushed; open a PR for the code change (RFC-004).
```

### B. Docs on `main` — commit, then hand the push to the human
```text
On main with a docs-only change (e.g. updated docs/guides/developer-guide.md):
  1. /commit-changes → commit "docs: clarify local setup steps"
  2. /push-changes   → gate finds the paths are fast-path-eligible (RFC-004),
                       BUT the agent cannot push main (protected-branch floor).
                       It PRINTS:  git push origin main   ← human runs this.
Result: committed locally; the operator runs the printed command to publish.
```

### C. Code on `main` — commit succeeds, push is REFUSED
```text
On main with application code / data/ / a migration staged:
  1. /commit-changes → commit succeeds locally
  2. /push-changes   → gate REFUSES: code/data/migrations may not land on main.
                       Instruction: move to a feat/ branch + PR —
                         git switch -c feat/<slug>
                         git push -u origin feat/<slug>   then open a PR.
Result: local commit exists, but it is NOT pushed to main (R2.3). The operator
        rebases/moves it onto a feat/ branch and opens a PR.
```

---

## Rules
- **Inherit everything from the parents** (R2.3): all of `/commit-changes`'s secret/hygiene + prefix rules and all of `/push-changes`'s branch-awareness, refusals, and force-push ban apply here unchanged.
- **Commit-then-push ordering:** the commit always runs first; the push is gated independently — a code change on `main` is **refused at the push step even though the commit succeeded** (R2.3).
- **Cross-reference, never duplicate** (R2.4): the authoritative rules are in [`/commit-changes`](../commit-changes/SKILL.md) and [`/push-changes`](../push-changes/SKILL.md).
- **Preserve hooks** (no `--no-verify`) unless explicitly asked.
- Does not open PRs — that is the Executor's `/spec-run` + the human gate (`/review-pr`).
