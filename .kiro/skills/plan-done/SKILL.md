---
name: plan-done
description: >-
  Closes a planning/brainstorm session for Cetana Labs (RFC-LAB-000-009 Phase 1 Scope) by finalizing its artifacts and MERGING the Kiro Spec / RFC / backlog rows to main as a doc PR — the merge-first rule that lets /spec-run <id> be a clean IDE one-liner. Transitions the lifecycle PLANNING -> READY_TO_BUILD. Prompts /brainstorm-save when the session had decisions. Use when the user runs /plan-done or says planning/brainstorming is finished.
---

# Skill: Plan Done (close Scope, merge the Spec)

## Objective
Close the **brainstorm / Scope** phase for a topic by finalizing its artifacts and **getting the Spec (and any RFC / backlog rows) merged to `main` as a doc PR**. This merge is the **merge-first rule**: once the Spec is on `main`, `/spec-run <spec-id>` needs only the id (no branch checkout) — it's what makes the Build one-liner clean (`RFC-LAB-000-009` §9 / state machine). Completing `/plan-done` transitions the lifecycle **PLANNING → READY_TO_BUILD**.

## Trigger Patterns
- `/plan-done`
- "planning is done", "finalize the spec", "we're ready to build this"

## Steps

### 1. State guard (phase-aware)
- **In PLANNING with drafted artifacts ⇒ proceed.**
- **Nothing planned / no artifacts (missing prerequisite) ⇒ ALERT + HOLD:** "Nothing to close — no Spec/RFC/backlog drafted this session. Brainstorm first (`/plan-start` or just raise the topic)." *(Missing prerequisite ⇒ HOLD, not a silent no-op that pretends success.)*
- **Already READY_TO_BUILD (Spec already on `main`) (redundant) ⇒ skip + continue:** "Spec `<id>` is already merged to `main` — ready for `/spec-run <id>`." Do not re-merge. *(Redundant ⇒ skip.)*

### 2. Finalize artifacts
- Ensure the **Spec** is complete and self-describing: `requirements.md` (EARS acceptance criteria = DoD + §0 Preconditions), `design.md`, `tasks.md` (ordered plan + **Execution header**: kickoff `/spec-run <id>`, surface, branch to create, EARS target). A Spec without these is not ready to merge (`/spec-run` requires them).
- Ensure backlog rows (`BK-`/`TSK-`) and any RFC status are consistent (governance lockstep — Pillar 2).

### 3. Merge as a doc PR (the merge-first step)
- Commit the Spec/RFC/backlog on a `docs/<slug>` branch (`RFC-LAB-000-004` naming; docs may fast-path but a PR keeps the trail).
- Open the PR via `gh api` (REST), and — this being a plan/doc change — gate it (`/review-pr`) and merge to `main`. After merge, `.kiro/specs/<id>/` is on `main`.
- Confirm: "Spec `<id>` merged to `main`. Kick off implementation in the IDE: `/spec-run <id>`." (State now READY_TO_BUILD.)

### 4. Capture decisions (human-curated)
- If the session contained **genuine decisions**, **prompt** (never auto-run) `/brainstorm-save` to append a curated Decision Journal entry (D17 — curation stays human-controlled). If it was pure drafting with no decision, skip.

## Rules
- **Web/plan only** — the output is a merged plan, not code.
- **Merge-first is the point** — the Spec must reach `main` here so `/spec-run` stays a clean, id-only one-liner. Do not hand off to `/spec-run` while the Spec is still on an unmerged branch.
- **The Spec must be self-describing before merge** (Execution header + §0 preconditions + EARS DoD) — else `/spec-run` will STOP.
- **State-guard:** nothing-planned ⇒ HOLD; already-merged ⇒ skip+continue.
- **Prompt, don't auto-run** `/brainstorm-save` (D17).
