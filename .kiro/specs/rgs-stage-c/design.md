# Requirement Gathering System (RGS) — Stage C — Design

| Property | Value |
| :--- | :--- |
| **Spec ID** | `rgs-stage-c` |
| **Deliverable** | `.kiro/skills/rgs/SKILL.md` (the engine) + this Spec |

---

## 1. Architecture — engine vs surface (the load-bearing decision)

```
         ┌─────────────────────── RGS ENGINE (stable core) ───────────────────────┐
RAW ASK ─►│  CAPTURE → ELICIT (1 Q/turn, checklist) → GAP/CONFLICT FLAG → STRUCTURE │─► INTAKE-NNN draft
         │                 (documented question strategy)      (documented schema) │   + channel relay
         └────────────────────────────────────────────────────────────────────────┘
              ▲ Stage C surface = the chat skill (/rgs)
              ▲ Stage B surface = SvelteKit UI  ─┐  both call the SAME engine
              ▲ Stage D surface = org hub       ─┘  (no engine rewrite)
                                   │
                 handoff ──────────┘──► EXISTING AIDLC (unchanged):
                 INTAKE-NNN → BACKLOG Epic → /plan-start → Spec → /spec-run → /review-pr → human merge
```

- The **engine** = two documented, surface-agnostic artifacts inside `SKILL.md`: (a) the **elicitation strategy** (the checklist + the one-question-at-a-time loop + gap/convergence rules), (b) the **output schema** (the exact `INTAKE-NNN` register-row + detail-block shape). Documented in sections **distinct** from each other and from any chat phrasing — so Stage B's UI can drive the same checklist and reuse the same emitter (R-ENG-1).
- The **surface** (Stage C) = a KiroCrew skill invoked `/rgs` that runs the loop in chat. No chat-only assumption leaks into the engine steps.

## 2. The elicitation strategy (engine part A — documented)

A fixed completeness checklist (R-ELI-2), driven one question at a time (R-ELI-1):

| # | Slot | What "complete" means | Gap triggers (R-ELI-3) |
| :-- | :--- | :--- | :--- |
| 1 | **Actor / user** | A named role/persona who benefits | "users"/"people" with no role |
| 2 | **Trigger** | What event/need starts it | absent |
| 3 | **Desired outcome** | The concrete end state | an adjective, not an outcome ("better") |
| 4 | **Acceptance criteria** | ≥1 **testable** condition | "fast"/"soon"/"nice" — unquantified |
| 5 | **Scope boundaries** | explicit in / out | no out-of-scope stated |
| 6 | **Priority** | P1–P3 (+ why) | absent |
| 7 | **Source-of-truth data** | which data/system grounds it | "the data" unspecified |

- **One question per turn**, picking the highest-leverage unfilled slot; never dump the list.
- **Gap flag:** when an answer contains an unquantified adjective, a missing actor, or an untestable success criterion, name it and ask for the specific value.
- **Grounding (R-ELI-5):** before asserting what the target system does today, grep that repo's real intents/entities/accepted file-types; cite what was checked (R-GOV-3). Never assume.
- **Conflict flag (R-ELI-4, thin):** if the target repo has a readable `REQUIREMENTS_INTAKE.md`, scan prior `INTAKE-NNN` asks for keyword/topic overlap and surface "possible overlap with INTAKE-0XX" as a flag. If none readable (e.g. Cetana has none yet), say so and skip — no fabrication.
- **Convergence (R-ELI-6):** when all 7 slots are filled → structure. The human may force early stop ("that's enough") → remaining slots become open questions → state `AWAITING-SOURCE`.

## 3. The output schema (engine part B — documented, byte-compatible)

Grounded in the **live** Nexus Pulse `REQUIREMENTS_INTAKE.md` (verified 2026-10-07). Two parts, emitted verbatim-compatible:

**(1) Register row** — pipe table, columns in this exact order:
```
| **INTAKE-NNN** | YYYY-MM-DD | <who asked> → <who relayed> → <who owns> | <ask in one line> | **STATE** | <open questions / graduation link> |
```

**(2) Detail block** — heading `## INTAKE-NNN — <Short Title> (detail)` then these labelled lines, in order:
```
**Source chain:** …
**Raw ask:** …
**Current-state assessment (verified against the codebase YYYY-MM-DD):** … (bulleted; cite what was grepped — R-GOV-3)
**Proposal (phased if warranted):** …
**Resolved decisions:** … (numbered; or "none yet")
**Still-open questions:** … (numbered; drives AWAITING-SOURCE)
**Recommendation:** …
**Graduation:** TBD (→ BACKLOG Epic once CLARIFIED)
```

- **State values** (R-OUT-2): `NEW` | `AWAITING-SOURCE` | `CLARIFIED` | `SPECCED` | `DELIVERED` — emit `CLARIFIED` if all slots resolved, else `AWAITING-SOURCE` (+ open questions) or `NEW`.
- **NNN** = next free id in the target ledger; if no ledger exists (Cetana today), emit `INTAKE-001` and note the ledger must be created on first adoption.
- **Owner label** = full name "Agni Eialarasu" (R-GOV-2).

## 4. The channel-relay draft (R-OUT-4)

A second copy-paste block, per the live process §5 convention:
```
<decision or the ask, one line>
Top questions: 1) … 2) … 3) …   (≤3)
Full detail: docs/REQUIREMENTS_INTAKE.md — INTAKE-NNN
```
Short, decision-first, doc-pointer at the end. RGS never sends it (R-GOV-1).

## 5. The skill surface (Stage C)

`.kiro/skills/rgs/SKILL.md`, invoked `/rgs <raw ask>` (or `/rgs` then paste). Phases: **Capture** (chain prompt) → **Elicit** (the §2 loop) → **Flag** (gap + conflict) → **Structure** (the §3 emitter) → **Export** (doc block + channel block). Pure drafting; zero repo writes (R-GOV-1). Deleting the file removes RGS (NFR-2).

## 6. Grounding note — Cetana has no ledger yet
The live `INTAKE-NNN` shape is defined by **Nexus Pulse**; Cetana Labs has no `docs/REQUIREMENTS_INTAKE.md` and the process is 🟡 Proposed for Cetana. RGS Stage C therefore:
- emits byte-compatible with the Nexus shape (the standard), and
- for Cetana runs, flags that the local ledger does not exist yet (so adoption — creating `docs/REQUIREMENTS_INTAKE.md` + the process doc — is a separate, human-decided step tied to the cross-repo structure decision, NOT something RGS does autonomously).

## 7. Risks & mitigations
| Risk | Mitigation |
| :--- | :--- |
| Emitter drifts from the live ledger shape | Schema (§3) is copied from the verified live file; V4 byte-compatibility is a hard acceptance test. |
| RGS fabricates current-state | R-ELI-5 grounding + R-GOV-3 citation; demo V-plan checks a cited assessment. |
| Chat assumptions leak into the engine | §2/§3 documented surface-agnostic; V8 checks schema is a separate section. |
| Scope creep toward a UI/connectors | §4 out-of-scope + NFR-1; Stage C is one skill only. |
