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

### 0. State guard (phase-aware — `RFC-LAB-000-009` state machine)
`/review-pr` is the **verify** phase — it gates a PR that a Build (`/spec-run`) produced. Confirm the lifecycle state first:
- **An open PR exists (IN_REVIEW) ⇒ proceed.**
- **No open PR yet (missing prerequisite) ⇒ ALERT + HOLD:** "Nothing to review — no open PR. Implement the Spec first: `/spec-run <spec-id>` (which opens the PR), then `/review-pr`." *(Missing prerequisite ⇒ HOLD, never fabricate a review.)*
- **PR already merged/closed (redundant) ⇒ skip + continue:** "PR #NN is already merged — proceed to `/sprint-done` (Record)." Do not re-review. *(Redundant ⇒ skip.)*
- The state-guard is a tripwire, never a bypass: this skill still **never merges or auto-approves** regardless of state (§Rules).

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
- **"Vercel Preview Comments" is NOT a deploy signal.** It appears on the **check-runs** surface above and reports *comment posting*, not build/deploy health. Do **not** treat it as evidence the frontend deployed — the real frontend-deploy signal lives on the **commit-status** API (step 2b). Our GitHub CI runs `pnpm build` directly, so a green CI likewise says nothing about whether Vercel's own build/deploy succeeded. (This is the exact `BK-023` blind spot: three stacked Vercel-build failures all passed this gate + green CI.)

### 2b. Frontend deploy (Vercel's REAL deployment status — `BK-023`)
The genuine Vercel deploy signal is posted to the **commit-status** API (a different surface from the check-runs above), as the **`Vercel`** context (and `Cetana Lab Staging - cetana-labs` when present). Read it **for the PR head SHA**:
```bash
head=$(gh api repos/agni-eialarasu/cetana-labs/pulls/<n> --jq .head.sha)
gh api repos/agni-eialarasu/cetana-labs/commits/$head/status \
  --jq '.statuses[] | select(.context=="Vercel" or .context=="Cetana Lab Staging - cetana-labs")
        | {context, state, target_url, updated_at}'
```
Evaluate the result against the head SHA and encode the state (failure-safe — the default is HOLD, not pass):

| Observed on head SHA | Verdict | Why |
| :--- | :---: | :--- |
| `Vercel` context = **`success`** (and the query was keyed to head, so it IS for head) | ✅ | Vercel built & deployed this commit. |
| `Vercel` context = **`failure`** / **`error`** | ❌ **HOLD** | Vercel's build/deploy for this commit failed. |
| **No `Vercel` status for the head SHA** (empty result) | ⚠️ **HOLD** | Deploy not triggered / in-flight / silently failed — unverified, not a pass. Common: only deploy-triggering commits get a status. |
| A `Vercel` **success exists only on an older SHA**, not head | ⚠️ **HOLD** | The **stale-success trap** from the `BK-023` incident — Vercel keeps serving the last good build while head is broken. Match the status to head; older-SHA success ≠ head is deployed. |

- The guard is **failure-safe**: anything other than a `success` *bound to the head SHA* is a HOLD. (Because the `commits/$head/status` call is keyed to head, a returned `success` is inherently head's — the stale trap only bites if you query a branch/combined endpoint instead; always key to head.)
- Capture the **evidence** for the checklist: the context name, the `state`, and that it matched the head SHA (plus the `target_url` for the human to open).
- This durable enforcement is intended to become a **required status check** on `main` once branch protection lands (see the branch-protection guidance in `developer-guide.md` §9A / `RFC-LAB-000-012`); until then, this gate is the enforcement.

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

### 4b. Human verification record (the evidence the gate consumes — `RFC-LAB-000-009` §3.2)
- For a Spec PR, open `.kiro/specs/<spec>/REPORT.md` and read the **Verification Log**: did the human run the Spec's Human Verification Plan, and is the **verdict PASS**?
- Confirm the corrections it records were pushed to **this** PR (Single-PR rule), not a separate branch.
- **No verification record / verdict not PASS ⇒ HOLD:** "Human functional verification isn't recorded/passed — run `/verification-done` in the IDE after verifying (or finish the loop) before this gate." *(This turns the gate from CI+DoD-on-paper into CI+DoD+**evidence the human exercised it**.)*
- Lead-paired PRs may satisfy this with a lighter note in the PR body; delegated/AIDLC PRs require the `REPORT.md` Verification Log.

### 5. Governance lockstep (`RFC-LAB-000-004`, Pillar 2) — verify FIRSTHAND, do not assert
> **Lesson learned:** this step has twice been marked ✅ on the Verification Log's word while the CHANGELOG entry was actually missing. **Check the repo directly** — never infer lockstep from the PR body or the REPORT.
- **CHANGELOG entry present?** Firsthand grep for the PR's task id in `CHANGELOG.md` (on the PR branch):
  ```bash
  git show <branch>:CHANGELOG.md | grep -c "TSK-0XX"   # expect >= 1
  # or, on the PR files: gh api repos/.../pulls/<n>/files --jq '.[].filename' | grep -x CHANGELOG.md
  ```
- **Tracker status coherent?** The item's `SPRINT_TRACKER.md` status matches its lifecycle state (e.g. not still `📋 Backlog` for a PR in review).
- **`data/` consistent** if touched; `make validate-local` (or CI's mirror) green (ties to Step 2).
- **Timing nuance (don't over-HOLD):** the CHANGELOG entry and the `Done` status are legitimately **Record-phase (post-merge)** steps in some flows — so a *missing* CHANGELOG entry at review time is a **⚠️ reviewer note + an explicit item in the merge instructions** ("add the CHANGELOG entry + flip the tracker in the post-merge tidy"), **not automatically a HOLD**. But it MUST be surfaced firsthand and MUST be closed in the tidy — never silently marked ✅. If the PR *claims* lockstep is already done and it isn't, that discrepancy **is** a HOLD (the record is untrustworthy).

### 6. Present the review + STOP-and-hold
- Emit a checklist table: **CI · Frontend deploy (Vercel status) · Scope/hygiene · EARS DoD (per-criterion) · Human verification record · Governance (CHANGELOG entry firsthand-checked + tracker status)**, each ✅ / ⚠️ / ❌ with a one-line note. For **Frontend deploy**, state the *evidence* — the `Vercel` context, its `state`, and that it matched the head SHA (e.g. "Vercel status: `success` on head `abc1234` ✅" or "⚠️ no `Vercel` status for head `abc1234` — unverified, HOLD"). For Governance, state the *evidence* (e.g. "CHANGELOG grep: 1 hit for TSK-0XX ✅" or "⚠️ no CHANGELOG entry yet — add in post-merge tidy").
- Give a clear **reviewer recommendation**: `READY (human approval required to merge)` or `HOLD — <reasons>`.

### 6b. Record the verdict on the PR (transactional, auditable — `review-record` Spec)
- After emitting the checklist to chat, **post the same checklist + verdict as a PR comment** so the gate leaves a durable, auditable trace on the artifact itself (`ai-collaboration-model.md` §6). The chat output and the PR comment share one rendered body.
- **Comment only — NEVER a GitHub review.** Use the **issue-comment** endpoint (`issues/<n>/comments`); do **not** call `pulls/<n>/reviews` (no `APPROVE` / `REQUEST_CHANGES` / even `COMMENT` event). Posting a review would cast a verdict on GitHub and usurp the human gate — forbidden.
- The body MUST lead with a header stating this is a **recommendation, not an approval — the human still authorizes the merge** (`RFC-LAB-000-009` §4; the Operator never merges), followed by a **dated run line** (`gate run — <ISO date>`) so re-runs are distinguishable, then the per-row evidence table (CI · Frontend deploy (Vercel status) · Scope/hygiene · EARS DoD · Human verification record · Governance lockstep).
- **HOLD is recorded too:** when the verdict is HOLD, still post the comment (leading with **Verdict: HOLD** + the blocking reasons) so a held PR self-documents *why* on the artifact.
  ```bash
  # comment-only — NEVER pulls/<n>/reviews
  gh api repos/agni-eialarasu/cetana-labs/issues/<n>/comments -f body="$VERDICT_MD"
  ```
- **Idempotency (no spam):** the dated run header makes stacked re-runs distinguishable. Optionally (only if it stays simple), find the Operator's prior gate comment by a hidden marker string and update it in place via `gh api --method PATCH repos/agni-eialarasu/cetana-labs/issues/comments/<id> -f body="$VERDICT_MD"` instead of appending a new one.
- If `gh` fails (auth/rate), surface the error in chat but **still STOP-and-hold** — the chat verdict remains the record of last resort.
- **STOP.** Ask the human to explicitly approve or request changes. Do **not** merge, approve via API, or push.

### 7. On explicit human approval only
- If — and only if — the human explicitly says to merge, note that the merge is **squash-merge, delete branch, no force-push** (`RFC-LAB-000-004`), and that lockstep/record (Phase 5: CHANGELOG/BACKLOG/journal, `/brainstorm-save` if decisions, release at `/sprint-done`) follows.
- Absent explicit approval, remain held.

## Rules
- **Never merge and never post a GitHub review via the API.** This skill surfaces; the human decides. It MAY post an **issue comment** recording the verdict (§6b), but MUST NOT call `pulls/<n>/reviews` (no approve / request-changes / `COMMENT` event) — a review would cast a GitHub verdict and usurp the human gate.
- **Record the verdict on the PR (§6b):** post the checklist + verdict as an **issue comment**, explicitly labeled recommendation-not-approval with a dated run header. HOLD verdicts are posted too. This is the only repo-write the skill performs, and it is a *comment*, never an action on the merge.
- **STOP-and-hold is mandatory** — always end at a human decision point.
- A failing/pending check, an unverifiable EARS criterion, or a missing/failed human-verification record ⇒ **HOLD**, not a soft pass.
- **Frontend deploy (`BK-023`):** read Vercel's **real** deploy status from the **commit-status** `Vercel` context for the **head SHA** (step 2b) — never trust "Vercel Preview Comments" (comment posting, not deploy) or green GitHub CI as the frontend-deploy signal. Anything other than a `success` bound to the head SHA (failure/error, missing-for-head, or success only on an older SHA) ⇒ **HOLD**.
- **Verify governance lockstep FIRSTHAND (§5) — never assert it from the PR body or Verification Log.** A missing CHANGELOG entry at review time is a ⚠️ note carried into the post-merge tidy (not auto-HOLD); a *false claim* that lockstep is done **is** a HOLD.
- Read-only against the repo (no commits, no merges); the sole write is the PR gate **comment** (§6b) — not a review, not a push.
- Reads use `gh api` (REST) — the `gh pr`/GraphQL subcommands are unavailable in this environment.
