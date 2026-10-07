# Requirement Gathering System (RGS) — Stage C — Requirements

| Property | Value |
| :--- | :--- |
| **Spec ID** | `rgs-stage-c` |
| **Feature** | A KiroCrew skill + LLM elicitation engine that turns a fuzzy, unstructured ask into a complete, testable, conflict-checked requirement emitted in the project's exact `INTAKE-NNN` format — the business-analyst front-end for the existing AIDLC intake lifecycle. |
| **Backlog** | `BK-026` (`TSK-067`, SPRINT-12) |
| **Work class** | **Governance tooling** (a skill, not business functionality a user exercises) → **simplified path**: validate-docs → branch/push → human fast-merge. **No `/review-pr` scorecard, no Gate 5 recording.** (Three invariants hold: human holds the merge gate, agent never pushes `main`, validate-docs stays green.) |
| **RFCs / process** | `RFC-LAB-000-009` (AIDLC lifecycle — RGS feeds its intake front-end), Nexus Pulse `docs/runbooks/REQUIREMENTS_INTAKE_PROCESS.md` (the live intake process + `INTAKE-NNN` convention RGS emits to) |
| **Executor role** | **Operator-authored** (this session). The skill is a procedure, not an app build — no `/spec-run` executor needed to *write* it; it is exercised by invoking `/rgs`. |
| **Source** | Cross-repo kickoff brief (Stage C), 2026-10-07; Director accepted all defaults (D1–D3). |

---

## 1. Introduction

Inbound requirements arrive as discussion (client → architect → Operator) and the Operator hand-shapes them into `INTAKE-NNN` ledger entries today — manual business-analyst work. **RGS Stage C** makes the LLM do that elicitation: it takes a raw fuzzy ask, runs a short guided Q&A to completeness, detects gaps/vagueness/overlap, and emits a **ledger-ready** `INTAKE-NNN` draft (register row + detail block) plus a crisp channel-relay message. The Operator then *reviews* rather than *drafts from scratch*. RGS owns **capture → elicit → structure → export**; everything after the handoff is the unchanged existing AIDLC.

**This is governance tooling** — one skill + one documented output contract. It adds no app, no deploy, no new repo (NFR-1), and deleting the skill removes RGS entirely (NFR-2).

### The one architectural commitment: SEPARATE THE ENGINE FROM THE SURFACE
The elicitation question-strategy and the `INTAKE-NNN` emitter are the stable **engine** (the skill body + a documented output schema); each later stage adds a **surface** without rewriting the engine — Stage B (a SvelteKit UI module in Cetana) and Stage D (an org-level cross-repo hub) both call the same core. Stage C must therefore keep the engine surface-agnostic (R-ENG-1).

## 0. Preconditions (preflight — verify BEFORE asserting anything)
- **P1 — Ground the output shape in the REAL ledger (hard):** before emitting any `INTAKE-NNN`, read the live `INTAKE-NNN` convention. The authoritative live example is **Nexus Pulse** `docs/REQUIREMENTS_INTAKE.md` + `docs/runbooks/REQUIREMENTS_INTAKE_PROCESS.md`. Cetana Labs has **no** ledger of its own yet (the process is 🟡 Proposed for Cetana adoption), so the shape is defined by the Nexus live file. The emitter must be byte-compatible with it.
- **P2 — Ground current-state claims in real code (hard):** any assertion about what a target system does SHALL be verified against that repo's actual code (grep real intents/entities/accepted file-types), never assumed (R-ELI-5 / NFR-4).
- **P3 — No autonomous writes:** RGS drafts into chat; it SHALL NOT write to any product repo or commit scope on anyone's behalf (R-GOV-1).

## 2. Current-state facts (verified 2026-10-07)
- The live `INTAKE-NNN` convention exists in **Nexus Pulse** only: register columns `| ID | Date | Source chain | Ask (one line) | State | Open questions / graduation |`; a per-item detail block (Source chain · Raw ask · Current-state assessment · Proposal (phased if warranted) · Resolved decisions · Still-open questions · Recommendation · Graduation); 5-state machine **NEW → AWAITING-SOURCE → CLARIFIED → SPECCED → DELIVERED**.
- **Cetana Labs has no `docs/REQUIREMENTS_INTAKE.md` and no `docs/runbooks/`** yet — the intake process doc marks itself "🟡 Proposed for adoption into Cetana Labs AIDLC". ⟹ RGS's conflict-detection (R-ELI-4) must degrade gracefully when no local ledger is readable, and RGS must not assume a Cetana ledger exists.
- Channel-relay convention (process §5): short message = decision/ask first + 1–3 top questions + repo-doc pointer; never the full assessment.

## 3. Requirements (EARS acceptance criteria = Definition of Done)

### R-CAP — Capture
- **R-CAP-1** RGS SHALL accept an unstructured ask as free text in one message (typed or pasted thread), with no required structure.
- **R-CAP-2** RGS SHALL accept an already-transcribed voice note as text. Audio-file transcription is OUT of scope.
- **R-CAP-3** RGS SHALL capture the **source chain** (who asked → who relayed → who owns) at intake; default owner = the Operator; WHEN the chain is not stated, RGS SHALL prompt for it.

### R-ELI — Elicitation (the AI value)
- **R-ELI-1** RGS SHALL run a guided conversation asking **ONE focused question at a time** (never a wall of questions).
- **R-ELI-2** RGS SHALL drive toward completeness along a fixed checklist: actor/user · trigger · desired outcome · testable acceptance criteria · scope boundaries (in/out) · priority · source-of-truth data.
- **R-ELI-3 (gap detection)** RGS SHALL flag vagueness and demand specifics — unquantified adjectives ("fast"/"soon"/"better"), missing actors, untestable success criteria. (Acceptance #3: on a deliberately under-specified ask, RGS flags ≥ 1 gap.)
- **R-ELI-4 (conflict detection, thin v1)** WHEN a `REQUIREMENTS_INTAKE.md` is readable for the target repo, RGS SHALL surface POSSIBLE overlaps/clashes with prior `INTAKE-NNN` items as a flag for the Operator. WHEN none is readable, RGS SHALL say so and skip (no fabrication). Full corpus-wide semantic conflict search is B/D. *(D2: include this thin flag.)*
- **R-ELI-5 (grounding)** RGS SHALL ground current-state claims in real code before asserting what a system does (grep real intents/entities/file-types); it SHALL NOT fabricate capabilities.
- **R-ELI-6 (converge)** WHEN the checklist is satisfied RGS SHALL stop asking and move to structure; the human MAY say "that's enough" to force early convergence — unresolved items THEN become open questions → state `AWAITING-SOURCE`.

### R-OUT — Structure & export (the output contract)
- **R-OUT-1** RGS SHALL emit a draft `INTAKE-NNN` entry matching the real convention, BOTH parts: (1) the **register row** (`| ID | Date | Source chain | Ask (one line) | State | Open questions / graduation |`); (2) the **detail block** (Source chain · Raw ask · Current-state assessment · Proposal (phased if warranted) · Resolved decisions · Still-open questions · Recommendation · Graduation (TBD)).
- **R-OUT-2** RGS SHALL assign the initial state per the state machine: `CLARIFIED` if fully resolved, else `AWAITING-SOURCE` (listing open questions) or `NEW`.
- **R-OUT-3** The output SHALL be copy-paste / commit-ready markdown that drops into `docs/REQUIREMENTS_INTAKE.md` with **no translation**. (Acceptance #2: byte-compatible with the live file's shape — a hard test.)
- **R-OUT-4** RGS SHALL ALSO produce the **crisp channel-relay draft** (short WhatsApp/Slack message: decision + 1–3 top questions + doc pointer) as a copy-paste block for the Director to send. RGS SHALL NOT send it.

### R-ENG — Engine/surface separation
- **R-ENG-1** The elicitation question-strategy and the `INTAKE-NNN` emitter SHALL be a self-contained, **surface-agnostic** procedure (skill body + a documented output schema), so a future UI (Stage B) can call the same logic without reimplementing it. Acceptance: no chat-only assumptions in the core steps; the **output schema is documented separately** from the conversation flow.

### R-GOV — Governance / guardrails
- **R-GOV-1** RGS SHALL NEVER commit scope on the client's behalf and SHALL NEVER write to any product repo autonomously. It drafts; a human reviews and commits. (Acceptance #5.)
- **R-GOV-2** Owner labels SHALL use the full name **"Agni Eialarasu"**; bare "Agni" means the org.
- **R-GOV-3** RGS output is DATA for the Operator to review, not an authority; any system-state claim SHALL cite where it was verified.

### R-NFR — Non-functional
- **R-NFR-1** Stage C SHALL add no app, no deploy, no auth, no new repo — one skill + one documented output contract.
- **R-NFR-2** RGS SHALL be reversible — deleting the skill removes RGS entirely.
- **R-NFR-3** The engine SHALL be portable — the output schema documented so B/D reuse is additive.
- **R-NFR-4** RGS SHALL be grounded — no fabricated capabilities; current-state claims code-verified.

## 4. Out of scope (scope honesty)
A web UI (Stage B); the org-level hub (Stage D); audio-file transcription; live connectors (Jira/Monday/Aha/Excel); autonomous repo commits; full semantic conflict search across the corpus.

## 5. Resolved decisions (Director accepted all defaults, 2026-10-07)
- **D1 — Skill home:** committed `.kiro/skills/rgs/SKILL.md` in **Cetana Labs** `.kiro/skills/` (control plane; eventual B/D home).
- **D2 — Conflict detection:** INCLUDE the thin overlap-flag (R-ELI-4) in Stage C.
- **D3 — Multi-project output:** ONE repo per run in Stage C; repo-awareness is a Stage D concern.

## 5b. Acceptance test (how we know Stage C works)
1. Given a one-paragraph fuzzy ask, RGS runs a guided Q&A and produces a draft `INTAKE-NNN` (register row + detail block) a human judges complete and testable.
2. The emitted markdown pastes into `docs/REQUIREMENTS_INTAKE.md` with NO reformatting (byte-compatible shape).
3. RGS flags ≥ 1 vagueness/gap on a deliberately under-specified ask.
4. RGS produces the crisp channel-relay draft alongside the doc.
5. RGS makes no repo writes and commits no scope autonomously.
6. The elicitation strategy + output schema are documented separately enough that a Stage B UI could call the same engine.

## 5c. Human Verification Plan (demo-based — this Spec is exercised, not `/spec-run` built)
- **V1 — capture + chain:** feed a fuzzy one-paragraph ask with no stated chain; RGS prompts for the source chain (R-CAP-3).
- **V2 — one-at-a-time elicitation:** RGS asks a single focused question per turn along the checklist (R-ELI-1/2).
- **V3 — gap flag:** on a deliberately vague ask ("make reporting better, soon"), RGS flags the unquantified adjective + untestable criterion (R-ELI-3).
- **V4 — INTAKE-NNN emit + byte-compatibility:** the draft register row + detail block paste into a copy of the live `REQUIREMENTS_INTAKE.md` with no reformatting (R-OUT-1/3).
- **V5 — state assignment:** an ask with open questions emits `AWAITING-SOURCE` + the questions; a fully-resolved one emits `CLARIFIED` (R-OUT-2).
- **V6 — channel relay:** RGS emits the short WhatsApp/Slack draft (decision + 1–3 questions + doc pointer) (R-OUT-4).
- **V7 — no autonomous write:** RGS performs zero repo writes across the demo; the Operator copies the output manually (R-GOV-1).
- **V8 — engine/surface separation:** the SKILL.md documents the output schema in a section distinct from the conversation flow (R-ENG-1).
