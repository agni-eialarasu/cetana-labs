---
name: verification-done
description: >-
  Closes the human functional-verification loop for a Kiro Spec in Cetana Labs (RFC-LAB-000-009 — the verify phase, Kiro IDE). After you (the human) exercise the feature per the Spec's Human Verification Plan and any minor corrections are pushed to the SAME PR (Single-PR rule), this appends the verification record — steps run, findings, corrections, verdict — to .kiro/specs/<id>/REPORT.md, commits it to the same PR, and transitions the lifecycle IN_VERIFICATION → IN_REVIEW so the downstream gate (/review-pr) has the evidence. Use when the user runs /verification-done after functional verification passes.
---

# Skill: Verification Done (close the human-verify loop)

## Objective
Capture the outcome of **human functional verification** — the phase where *you* run/click/exercise the feature against the Spec's **Human Verification Plan**, and the IDE agent fixes any minor issues on the **same open PR** until it passes. This skill **records that loop** into a durable, in-repo artifact (`.kiro/specs/<id>/REPORT.md`) and **transitions the state** so the next agent in the pipeline (the KiroCrew Operator `/review-pr`, then `/sprint-done`) inherits the evidence instead of it evaporating in IDE chat.

Runs on **Kiro IDE** (that's where verification + fixes happen). It is the `-done` bookend of the verify phase; there is no `/verification-start` — the loop is *opened* when `/spec-run` emits the Human Verification Plan at its hand-off STOP (`RFC-LAB-000-009` §3.1 / naming convention `[phase]-[start|done]`).

### Where it sits in the loop
```
/spec-run  → opens PR + emits the Human Verification Plan → STOP
   │
   ▼
IN_VERIFICATION  ⇄  human runs the plan; reports findings; IDE fixes on the SAME PR
   │                 (Single-PR rule — never a new branch, never merge-then-hotfix)
   ▼
/verification-done → append Verification Log to REPORT.md (same PR); IN_VERIFICATION → IN_REVIEW
   ▼
/review-pr (Web) → gate reads the verification record as evidence → authorize merge → /sprint-done
```

## Trigger Patterns
- `/verification-done`
- "verification passed, record it", "close the verification loop", "log the verification and hand off to review"

## Steps

### 1. State guard (phase-aware — `RFC-LAB-000-009` state machine)
- **On a feature branch with an open PR, in IN_VERIFICATION ⇒ proceed.**
- **No open PR / not yet built (missing prerequisite) ⇒ ALERT + HOLD:** "Nothing to close — run `/spec-run <id>` first (it opens the PR and emits the verification plan)." *(Missing prerequisite ⇒ HOLD.)*
- **Verification not actually done — plan steps unrun or a step still failing (missing gate) ⇒ ALERT + HOLD:** "Verification hasn't passed yet — steps N, M are unrun/failing. Finish the loop (fix on this PR, re-run) before closing." *(Do not record a pass that didn't happen — the credibility of the record is the point.)*
- **Already IN_REVIEW (verification already recorded) (redundant) ⇒ skip + continue:** "Verification already logged for PR #NN — proceed to `/review-pr`." *(Redundant ⇒ skip.)*

### 2. Gather the loop's outcome (honest, from the actual session)
- Reconstruct, from this verification session: which **Human Verification Plan** steps were run, their pass/fail, any **findings**, the **corrections** pushed to the PR (with the fixup commit SHAs), and the **final verdict**.
- Be faithful — record failures-then-fixes, not a sanitized "all green." A verification log that hides the iteration is worthless to the reviewer.

### 3. Append the Verification Log to the Spec's REPORT.md
- Target `.kiro/specs/<spec-id>/REPORT.md`. If it doesn't exist yet, create it from `docs/templates/REPORT.template.md` and fill the header.
- **Append** (never overwrite prior logs) a Verification Log block:
  ```markdown
  ### Verification Log — <YYYY-MM-DD> (PR #NN)
  | Plan step | Result | Finding / correction |
  | :--- | :---: | :--- |
  | V1 <step> | ✅ / ❌→✅ | <what happened; fixup SHA if corrected> |
  | …         |          | |
  - **Iterations:** <n> (fixups pushed to this PR: <shas>)
  - **Verdict:** PASS — human functional verification complete.
  - **Verified by:** <name> (from git config) · **Surface:** Kiro IDE
  ```

### 4. Commit to the SAME PR (Single-PR rule)
- Commit `REPORT.md` on the current feature branch and push to the open PR — **do not** open a new branch/PR (`RFC-LAB-000-009` Single-PR rule; Nexus Pulse Golden Rule #1).
  ```bash
  git add .kiro/specs/<spec-id>/REPORT.md
  git commit -m "docs(spec): verification log for <spec-id> (human-verify PASS)"
  git push
  ```
- **(Optional) mirror** a one-paragraph summary as a PR comment (`gh api repos/{owner}/{repo}/issues/<PR>/comments`) so the Web `/review-pr` agent surfaces it without a checkout — the `REPORT.md` remains the source of truth.

### 5. Transition + hand off
- State is now **IN_REVIEW**. Report: "Verification recorded in `REPORT.md` (PR #NN). Ready for the gate: `/review-pr <PR>` (the **KiroCrew Operator**)."
- Do **not** merge and do **not** invoke the gate yourself — the human authorizes at `/review-pr`.

## Rules
- **Record honestly** — include findings and corrections (failure→fix), not a scrubbed pass. The record's value to the next agent is its truthfulness.
- **Never record a pass that didn't happen** — unrun/failing plan steps ⇒ HOLD (§1).
- **Single-PR rule** — the Verification Log and all fixes ride the *same* open PR; never merge-then-hotfix.
- **Never merge**, never invoke `/review-pr` for the human — this skill records + transitions; the human gates.
- **Append-only** to `REPORT.md` verification logs (a historical record across iterations).
- **IDE surface**; GitHub via `gh api` (REST).
- **State-guard:** redundant ⇒ skip+continue; missing prerequisite/gate ⇒ alert+HOLD.
