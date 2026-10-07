# Requirement Gathering System (RGS) — Stage C — Tasks

| Property | Value |
| :--- | :--- |
| **Spec ID** | `rgs-stage-c` |
| **Branch** | `feat/rgs-stage-c` (skills are project files; `feat/` per `RFC-LAB-000-004`) |
| **Work class** | **Governance tooling → simplified path**: validate-docs → branch/push → **human fast-merge**. NO `/review-pr` scorecard, NO Gate 5. Invariants: human merges, agent never pushes `main`, validate-docs green. |
| **Execution** | **Operator-authored** (this session) — the skill is a procedure, written directly, not `/spec-run`-built. Exercised by invoking `/rgs`. |
| **EARS target** | R-CAP/R-ELI/R-OUT/R-ENG/R-GOV/R-NFR in `requirements.md`; DoD = acceptance #1–#6 + the V1–V8 demo plan. |

---

## T0 — Ground in reality (STOP on failure) → P1, P2
- [x] Read the live `INTAKE-NNN` shape in **Nexus Pulse** `docs/REQUIREMENTS_INTAKE.md` + `docs/runbooks/REQUIREMENTS_INTAKE_PROCESS.md` (register columns, detail block, 5-state machine). *(P1)*
- [x] Confirm **Cetana Labs has no local ledger yet** → RGS degrades gracefully for conflict detection + flags adoption as separate. *(P1 / design §6)*
- [x] Confirm the channel-relay convention (process §5). *(R-OUT-4)*

## T1 — Author the Spec → this directory
- [x] `requirements.md` (EARS DoD + §0 preconditions + V1–V8 plan).
- [x] `design.md` (engine/surface split, elicitation strategy, byte-compatible output schema, grounding note).
- [x] `tasks.md` (this file).

## T2 — Author the skill → `.kiro/skills/rgs/SKILL.md` (R-CAP/R-ELI/R-OUT/R-ENG/R-GOV)
- [ ] Frontmatter (`name: rgs`, description) matching the repo's skill convention.
- [ ] **Capture** phase: accept free-text/pasted ask; prompt for the source chain if absent (default owner = Operator). *(R-CAP-1/2/3)*
- [ ] **Elicit** phase: the 7-slot checklist, one question per turn, gap triggers, grounding rule, convergence + "that's enough" early-stop. *(R-ELI-1/2/3/5/6)*
- [ ] **Flag** phase: thin conflict-overlap scan when a ledger is readable; graceful skip + say-so when not. *(R-ELI-4)*
- [ ] **Structure/Export** phase: the byte-compatible `INTAKE-NNN` emitter (register row + detail block) + state assignment + the channel-relay draft. *(R-OUT-1/2/3/4)*
- [ ] **Engine/surface separation:** document the elicitation strategy and the output schema in sections DISTINCT from the chat flow (so Stage B can reuse). *(R-ENG-1)*
- [ ] **Guardrails:** never writes a repo / commits scope; output is DATA; cite grounding; full-name owner labels. *(R-GOV-1/2/3)*

## T3 — Demo (prove acceptance #1–#4)
- [ ] Run `/rgs` on one deliberately-fuzzy sample ask; show the guided Q&A, ≥1 gap flag, the emitted `INTAKE-NNN` draft (register row + detail block), and the channel-relay block. *(V1–V6)*

## T4 — Governance (simplified path) + lockstep
- [ ] `validate-docs` / portfolio validator green. *(invariant)*
- [ ] Lockstep: `BACKLOG.md` `BK-026` row + `SPRINT_TRACKER.md` `TSK-067` row (owner **Agni Eialarasu**); CHANGELOG `[Unreleased]` entry.
- [ ] **No PR scorecard, no Gate 5** (governance tooling). Create `feat/rgs-stage-c`, commit, **print the `git push` + the push-to-main instruction for the human** — agent never pushes `main`.

## Post
- Human fast-merges the branch (simplified path). RGS is then live as `/rgs`.
- Related-but-separate (NOT this Spec): Cetana adopting its OWN `docs/REQUIREMENTS_INTAKE.md` + process doc — tied to the cross-repo structure decision; RGS does not force it.
