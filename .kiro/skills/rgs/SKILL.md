---
name: rgs
description: >-
  Requirement Gathering System (Stage C). Turns a fuzzy, unstructured ask (typed text, pasted WhatsApp/Slack thread, meeting notes, voice-note transcript) into a complete, testable, conflict-checked requirement emitted in the project's exact INTAKE-NNN format — the business-analyst front-end for the AIDLC intake lifecycle. Runs a guided one-question-at-a-time elicitation, flags gaps + possible overlaps, and emits a ledger-ready INTAKE-NNN draft (register row + detail block) PLUS a crisp channel-relay message. Drafts only — NEVER writes a repo or commits scope. Use when the user runs /rgs or brings a raw inbound requirement to shape. (RFC-LAB-000-009 intake front-end; feeds docs/REQUIREMENTS_INTAKE.md.)
---

# Skill: Requirement Gathering System — `/rgs`

## Objective
Do the manual business-analyst work for an inbound requirement: take a raw fuzzy ask and, through a **short guided LLM conversation**, produce a **ledger-ready `INTAKE-NNN` draft** the Operator reviews rather than drafts from scratch — plus a crisp channel-relay message. RGS owns **capture → elicit → structure → export**; everything after the handoff is the UNCHANGED existing AIDLC (`INTAKE-NNN → BACKLOG Epic → /plan-start → Spec → /spec-run → /review-pr → human merge`).

**RGS drafts; a human reviews and commits. It NEVER writes a repo or commits scope autonomously.**

## Trigger patterns
- `/rgs` — then paste the ask, or `/rgs <the raw ask inline>`
- "shape this requirement", "turn this ask into an intake entry", "elicit requirements for …"

---

## ⚙️ THE ENGINE (surface-agnostic — a future UI reuses THIS, unchanged)

> This section is the stable core: the elicitation strategy (A) + the output schema (B). It makes **no chat-only assumption** — a Stage B SvelteKit UI or a Stage D hub drives the same checklist and the same emitter. Keep A and B documented separately from the conversation flow below (R-ENG-1).

### A. Elicitation strategy — the completeness checklist (ask ONE at a time)
Fill 7 slots, one focused question per turn, highest-leverage unfilled slot first. **Never dump the whole list.**

| # | Slot | "Complete" means | Gap trigger (flag + demand specifics) |
| :-- | :--- | :--- | :--- |
| 1 | **Actor / user** | a named role/persona | "users"/"people", no role |
| 2 | **Trigger** | the event/need that starts it | absent |
| 3 | **Desired outcome** | the concrete end state | an adjective, not an outcome |
| 4 | **Acceptance criteria** | ≥1 **testable** condition | "fast"/"soon"/"better"/"nice" — unquantified |
| 5 | **Scope boundaries** | explicit in / out | no out-of-scope stated |
| 6 | **Priority** | P1 / P2 / P3 (+ why) | absent |
| 7 | **Source-of-truth data** | which data/system grounds it | "the data" unspecified |

Rules:
- **One question per turn** (R-ELI-1). Pick the slot that most unblocks the rest.
- **Gap detection** (R-ELI-3): on an unquantified adjective, a missing actor, or an untestable criterion — name the gap and ask for the specific value. Example: ask says "make reporting faster" → "What's the target? e.g. 'report renders in < 2s for 10k rows' — what number counts as done?"
- **Grounding** (R-ELI-5 / R-GOV-3): before stating what the target system does today, **grep the real code** (intents, entities, accepted file-types) and **cite what you checked**. Never assume or fabricate a capability.
- **Conflict flag, thin** (R-ELI-4): if the target repo has a readable `REQUIREMENTS_INTAKE.md`, scan prior `INTAKE-NNN` asks for topic/keyword overlap and surface "⚠️ possible overlap with INTAKE-0XX". If none is readable, say "no local intake ledger found — overlap check skipped" (no fabrication). Full semantic search is Stage B/D.
- **Convergence** (R-ELI-6): when all 7 slots are filled → go to Structure. The human may force early stop ("that's enough") → unfilled slots become **open questions** → state `AWAITING-SOURCE`.

### B. Output schema — the `INTAKE-NNN` contract (byte-compatible with the live ledger)
Grounded in the live Nexus Pulse `docs/REQUIREMENTS_INTAKE.md`. Emit BOTH parts, copy-paste-ready (R-OUT-1/3):

**(1) Register row** — pipe table, columns in EXACTLY this order:
```
| **INTAKE-NNN** | YYYY-MM-DD | <who asked> → <who relayed> → <who owns> | <ask in one line> | **STATE** | <open questions / graduation link> |
```

**(2) Detail block** — this heading + these labelled lines, in order:
```
## INTAKE-NNN — <Short Title> (detail)

**Source chain:** <who asked> → <who relayed> → <who owns>.
**Raw ask:** <the original ask, lightly tidied>.
**Current-state assessment (verified against the codebase YYYY-MM-DD):**
- <bulleted findings; CITE what was grepped — intents/entities/file-types>
**Proposal (phased if warranted):** <Phase 0 … → Phase 1 … where useful>
**Resolved decisions:** <numbered, or "none yet">
**Still-open questions:** <numbered; these drive AWAITING-SOURCE>
**Recommendation:** <one line>
**Graduation:** TBD (→ BACKLOG Epic once CLARIFIED)
```

**State** (R-OUT-2) ∈ `NEW` · `AWAITING-SOURCE` · `CLARIFIED` · `SPECCED` · `DELIVERED`. Emit `CLARIFIED` if all 7 slots resolved; else `AWAITING-SOURCE` (+ list the open questions) or `NEW`.
**NNN** = next free id in the target ledger. For Cetana Labs the ledger is **`docs/governance/REQUIREMENTS_INTAKE.md`** (adopted 2026-10-08, D69) — the first real entry is `INTAKE-001`. If a target repo has no ledger yet, emit `INTAKE-001` and note the ledger must be created on first adoption (as Cetana did).
**Owner labels** = full name **"Agni Eialarasu"** (bare "Agni" = the org, not the person) (R-GOV-2).

**(3) Channel-relay draft** (R-OUT-4) — a SEPARATE short copy-paste block (never sent by RGS):
```
<decision or the ask — one line>
Top questions: 1) … 2) … 3) …   (≤3, highest-leverage)
Full detail: docs/REQUIREMENTS_INTAKE.md — INTAKE-NNN
```

---

## 🗣️ THE SURFACE (Stage C — the chat flow)

Run the engine as a chat conversation:

1. **Capture.** Read the pasted/typed ask (R-CAP-1; a transcribed voice note is fine, R-CAP-2 — audio files are out of scope). Identify the **source chain** (who asked → who relayed → who owns); if not stated, **ask for it** (default owner = the Operator = Agni Eialarasu) (R-CAP-3).
2. **Elicit.** Run strategy **A**: one question per turn along the checklist, flagging gaps, grounding current-state claims in real code (grep + cite). Keep going until the checklist converges or the human says "that's enough".
3. **Flag.** Surface gap flags (R-ELI-3) and the thin conflict-overlap flag (R-ELI-4) for the Operator.
4. **Structure.** Build the `INTAKE-NNN` draft per schema **B** — register row + detail block — assign the state.
5. **Export.** Emit two clearly-separated copy-paste blocks: the **doc entry** (register row + detail block) and the **channel-relay** message. Then STOP — the Operator reviews, edits, and commits manually.

## Rules (guardrails)
- **Never write a repo, never commit scope** (R-GOV-1). RGS output is DATA for the Operator to review, not an authority (R-GOV-3). The Operator copies the output into `docs/REQUIREMENTS_INTAKE.md` by hand.
- **Ground, don't fabricate** (R-ELI-5 / R-NFR-4): any system-state claim cites where it was verified (which file/intent/entity you grepped). If you did not check, say so.
- **One question at a time** (R-ELI-1) — the whole point is a guided conversation, not a questionnaire dump.
- **Byte-compatibility is a hard contract** (R-OUT-3): the emitted markdown must paste into the live `REQUIREMENTS_INTAKE.md` with no reformatting. When in doubt, open the live file and match its shape exactly.
- **Owner = "Agni Eialarasu"** (full name), never bare "Agni" (R-GOV-2).
- **One repo per run** (D3) — Stage C targets a single repo's ledger; repo-awareness/multiplexing is Stage D.
- **Engine stays surface-agnostic** (R-ENG-1): keep sections A + B free of chat-only assumptions so Stage B/D reuse them unchanged.

## Scope (Stage C)
One skill + one documented output contract. **No** app, deploy, auth, or new repo (NFR-1); deleting this file removes RGS entirely (NFR-2). Out of scope: a web UI (Stage B), the org hub (Stage D), audio transcription, live connectors (Jira/Monday/Aha/Excel), autonomous commits, full corpus-wide semantic conflict search.
