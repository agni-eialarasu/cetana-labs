---
name: plan-start
description: >-
  Opens a planning/brainstorm session within the current sprint for Cetana Labs (RFC-LAB-000-009 Phase 1 Scope / the "brainstorm" phase, KiroCrew Operator). Frames a topic for brainstorming, backlog prep, RFC/doc changes, and authoring a Kiro Spec. OPTIONAL and IMPLICIT — any free-form topic is treated as a plan-start; you rarely invoke it explicitly. Nested under a sprint (a sprint contains many plans). Use when the user runs /plan-start or begins brainstorming a feature/topic.
---

# Skill: Plan Start (Brainstorm / Scope opener)

## Objective
Open the **brainstorm / Scope** phase for one feature or topic — where direction is set, options are weighed, the backlog is prepped, RFCs/docs are drafted, and (for delegated work) a **Kiro Spec** is authored. This is the first phase of the lifecycle (`RFC-LAB-000-009` §3). It runs on the **KiroCrew Operator** (stateful plan) and produces **no code** — its output is a merged plan (Spec/RFC/backlog rows).

**Optional & implicit:** you seldom type `/plan-start`. **Any free-form topic you raise is implicitly a plan-start** — the assistant treats "let's think about X" as entering planning. Invoke it explicitly only to *name* a planning session or reset focus.

### Granularity — nested under the sprint (decided: `RFC-LAB-000-009`)
```
/sprint-start  ── opens the SPRINT container (SPRINT-XX, 2-week window, goal)   [once per sprint]
   └── /plan-start …/plan-done   ── a PLANNING session inside it, per feature   [many per sprint]
          └── output: a MERGED Spec (.kiro/specs/<id>/) + backlog rows
                 └── /spec-run <id>  ── executes that Spec (Build)
```
A **sprint contains many plans**; each plan produces one Spec that `/spec-run` later executes. `/plan-start` does **not** open a sprint — that's `/sprint-start`.

## Trigger Patterns
- `/plan-start [topic]`
- **Implicit:** any free-form brainstorming request ("let's design…", "how should we approach…", "I'm thinking about…") — treat as plan-start without requiring the command.

## Steps

### 1. State guard (phase-aware — `RFC-LAB-000-009` state machine)
- Determine the current lifecycle state (inspect: is there an active sprint in `BACKLOG.md`? an in-flight Spec/plan? an open PR?).
- **Already PLANNING (redundant) ⇒ skip + continue:** note "already in a planning session on <topic>" and just fold the new topic in — do not re-open. *(Redundant ⇒ skip, per the guard semantics.)*
- **No active sprint (missing prerequisite) ⇒ ALERT + HOLD (soft):** "No active sprint — planning belongs inside a sprint (option-a nesting). Run `/sprint-start` first, or confirm you want to plan unscoped." Prefer steering to `/sprint-start` over proceeding unscoped. *(Missing prerequisite ⇒ alert, don't silently proceed.)*
- **Mid-Build / IN_REVIEW ⇒ ALERT:** "You're mid-implementation (branch/PR open). Planning a new topic now is fine, but the current Spec's Build isn't done — confirm you're context-switching." Then proceed if confirmed.

### 2. Frame the planning session
- State the topic, the sprint it sits under, and the surface (Web).
- Identify the intended **output artifact(s)**: an RFC (formal decision), backlog rows (`BK-`/`TSK-`), and/or a **Kiro Spec** (delegated/agent work — `RFC-LAB-000-009` §5 progressive formality).
- Brainstorm: surface options and trade-offs; the human sets direction (human-directed, AI-assisted — `docs/ai-collaboration-model.md`).

### 3. Hand off to close
- When decisions are made and artifacts drafted, the session closes with **`/plan-done`** — which finalizes and **merges the Spec/RFC as a doc PR** (the merge-first rule that lets `/spec-run <id>` be a clean one-liner).
- If the session produced genuine decisions, `/plan-done` will prompt `/brainstorm-save` (curation stays human-controlled — Decision Journal D17).

## Rules
- **Web/plan only** — no code, no feature branch, no build. Stateful execution is `/spec-run` (IDE).
- **Optional/implicit** — never block a free-form brainstorm waiting for the command; treat the topic as the plan-start.
- **Nested under a sprint** — steer to `/sprint-start` if none is active; don't open a sprint here.
- **State-guard:** redundant ⇒ skip+continue; missing prerequisite ⇒ alert+HOLD (never silently proceed unscoped).
