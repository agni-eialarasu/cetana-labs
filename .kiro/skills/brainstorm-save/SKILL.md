---
name: brainstorm-save
description: >-
  Captures the current brainstorming/planning session's KEY DECISIONS as a curated entry appended to docs/DECISION-JOURNAL.md — the reasoning/rationale showcase (problem → options → decision → outcome), attributed to the contributor. Use when the user runs /brainstorm-save or asks to capture/record the session's decisions or thinking.
---

# Skill: Brainstorm Save (Curated Decision Capture)

## Objective
Distil a brainstorming/planning session into a **curated decision narrative** and append it to
[`docs/DECISION-JOURNAL.md`](../../docs/DECISION-JOURNAL.md). This is the "how we reasoned to
decisions" showcase for engineering leadership (and any co-reviewer). It is **signal, not a
transcript** — only genuine decisions, with honest trade-offs.

> **Placement rationale:** the Decision Journal is a **project governance/showcase artifact**
> (it references repo RFCs/PRs and is meant to be read in-repo alongside them), so this is a
> **project** skill and entries are committed to the repo — not a personal scratch note.

## Trigger Patterns
- `/brainstorm-save`
- "capture this session's decisions", "record our thinking", "save the brainstorm"

## Steps

### 1. Identify what's journal-worthy (curate, don't pad)
- Scan the session for **real decisions**: a choice was made between options, a direction set, a trade-off resolved, or a course-correction taken.
- **Exclude** pure execution with no decision (routine fixes, builds, mechanical edits). If the session had **no** meaningful decisions, say so and do **not** write an entry (protects the journal's credibility).

### 2. Determine the entry number & contributor
- Read the last `## Entry NNN` in `DECISION-JOURNAL.md`; the new entry is `NNN+1` (zero-padded to 3).
- Determine the contributor from `git config user.email` / `user.name` (e.g. Agni Eialarasu). Attribute each decision to who made the call; support multiple contributors per entry.

### 3. Write the entry (append; never rewrite prior entries)
Append using this format:

```markdown
---

## Entry NNN — <short session title>

**Date:** YYYY-MM-DD · **Contributor(s):** <name(s)> · **Mode:** <Kiro Web / IDE> · **Outcome:** <RFCs / PRs / releases>

### D<n> — <decision title>
- **Trigger:** <what surfaced this>
- **Options:** <options weighed>
- **Decision & rationale:** <the call + WHY, in the contributor's reasoning>  _(Contributor: <name>)_
- **Outcome:** <RFC / PR / skill / artifact>
```
- One `D<n>` block per decision. Reference concrete artifacts (`RFC-LAB-000-00X`, `PR #N`, `TSK-0XX`).
- Optionally close with a short **Session meta** (division of labor, throughput, course-corrections, honest failures/recovery).

### 4. Governance & commit
- Keep it faithful and credible — include course-corrections and honest misses; never inflate.
- Governance/docs → may fast-path to `main` (RFC-LAB-000-004), or land via PR if bundled with code.
- Sync `CHANGELOG.md` / journal only if the entry corresponds to a tracked task; otherwise the journal update alone is fine.

## Relationship to other commands
- **`/sign-off`** (personal, end-of-session) should **prompt** — not auto-run — `/brainstorm-save` when the session contained decisions. Curation stays human-controlled (auto-running every session would pollute the journal).
- **`/session-save`** (personal, context handoff) is orthogonal — it carries context to a new chat; it does not archive decisions.

## Rules
- **Curate ruthlessly** — a padded journal loses its value to a CTO/architect.
- **Attribute honestly** — human-directed / AI-assisted; name who made each call.
- **Append-only** — never edit or delete prior entries (it's a historical record).
