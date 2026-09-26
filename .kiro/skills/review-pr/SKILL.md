---
name: review-pr
description: >-
  The human PR gate for Cetana Labs (RFC-LAB-000-009 Phase 4). Surfaces a pull request for review — CI status, diff scope, the Spec's EARS acceptance criteria (Definition of Done), governance lockstep, and branch/merge hygiene — as a decision checklist, then STOPs and holds for a human approve/iterate call. NEVER merges. Use when the user runs /review-pr or asks to review a PR before merge.
---

# Skill: PR Review Gate (`/review-pr`)

## Objective
Be the **human gate** in the sprint lifecycle (`RFC-LAB-000-009` §3, Phase 4 Review). Gather everything a reviewer needs to decide **merge vs. iterate** for a PR — CI health, what changed, whether the work meets its contract (the Spec's EARS DoD), and governance hygiene — present it as a checklist, and then **STOP-and-hold**. This skill *informs and surfaces*; it never decides and never merges. The human approves; squash-merge happens only after that approval.

This is the AIDLC safety rail: Autonomous mode / a delegated agent opens the PR, this gate ensures nothing reaches `main` unreviewed (`docs/ai-collaboration-model.md` §6).

## Trigger Patterns
- `/review-pr`
- `/review-pr <number>` (specific PR)
- "review this PR before merge", "is this PR ready to merge?", "gate this PR"

## Steps

### 1. Identify the PR
- If a number is given, use it. Else find the open PR for the current branch:
  ```bash
  gh api "repos/agni-eialarasu/cetana-labs/pulls?state=open&per_page=20" \
    --jq '.[] | {number, title, head: .head.ref, base: .base.ref, draft}'
  ```
- Confirm target `base` is `main` and the PR is not a draft. Report title, head→base, author.

### 2. CI status (must be green)
```bash
gh api repos/agni-eialarasu/cetana-labs/commits/<head-sha>/check-runs \
  --jq '.check_runs[] | {name, status, conclusion}'
```
- If any check is failing/pending: surface which one, pull the failing log
  (`gh run list` → `gh run view <id> --log-failed`), and mark the gate **BLOCKED** — do not proceed to a merge recommendation.

### 3. Diff scope & branch hygiene (`RFC-LAB-000-004`)
```bash
gh api repos/agni-eialarasu/cetana-labs/pulls/<n>/files --jq '.[].filename'
```
- Check the change is **focused** (one unit of work) and paths match the branch's stated scope.
- Verify branch naming (`<type>/<scope>-<slug>`) and that no secrets / `.env` / build artifacts are included.
- Confirm the PR is behind `main` by little/nothing (rebase/merge-clean); flag if stale.

### 4. Contract check — the Spec's EARS DoD (the core of the gate)
- If the PR implements a Kiro Spec, open `.kiro/specs/<spec>/requirements.md` and walk **each EARS acceptance criterion (R1, R2, …)**: is it demonstrably satisfied by the diff / PR description / linked verification?
- Cross-check `tasks.md`: are all tasks checked off, or is the remainder explicitly deferred with rationale?
- For lead-paired work with no Spec, check the PR against the backlog row / stated ask (progressive formality — `RFC-LAB-000-009` §5).
- List any **unmet or unverifiable** criterion explicitly. An unverifiable DoD item is a hold, not a pass.

### 5. Governance lockstep (`RFC-LAB-000-004`, Pillar 2)
- Application-code PR: is CHANGELOG / BACKLOG updated in step, and `data/` consistent if touched?
- Confirm `make validate-local` (or CI's mirror) is green (ties to Step 2).

### 6. Present the review + STOP-and-hold
- Emit a checklist table: **CI · Scope/hygiene · EARS DoD (per-criterion) · Governance**, each ✅ / ⚠️ / ❌ with a one-line note.
- Give a clear **reviewer recommendation**: `READY (human approval required to merge)` or `HOLD — <reasons>`.
- **STOP.** Ask the human to explicitly approve or request changes. Do **not** merge, approve via API, or push.

### 7. On explicit human approval only
- If — and only if — the human explicitly says to merge, note that the merge is **squash-merge, delete branch, no force-push** (`RFC-LAB-000-004`), and that lockstep/record (Phase 5: CHANGELOG/BACKLOG/journal, `/brainstorm-save` if decisions, release at `/sprint-done`) follows.
- Absent explicit approval, remain held.

## Rules
- **Never merge and never post an approving review via the API.** This skill surfaces; the human decides.
- **STOP-and-hold is mandatory** — always end at a human decision point.
- A failing/pending check or an unverifiable EARS criterion ⇒ **HOLD**, not a soft pass.
- Read-only against the repo except for reporting; make no commits.
- Reads use `gh api` (REST) — the `gh pr`/GraphQL subcommands are unavailable in this environment.
