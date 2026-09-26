# RFC-LAB-000-009: Sprint Lifecycle on Kiro Specs + Autonomous Mode

| Property | Value |
| :--- | :--- |
| **RFC ID** | `RFC-LAB-000-009` |
| **Title** | Sprint Lifecycle & AIDLC — Kiro-native Spec-Driven + Autonomous, Human-Gated |
| **Author** | Eialarasu (LAB-000 Control Hub) |
| **Status** | 🟡 Proposed |
| **Date** | 2026-09-26 |
| **Backlog** | `SPRINT-08` (process standardization; see `RFC-LAB-000-007`) |
| **Builds On** | `RFC-LAB-000-004` (branching & PR review), `RFC-LAB-000-007` (Web+IDE surfaces), `RFC-LAB-000-008` (MVP — first Spec target) |
| **Influenced By** | Nexus Pulse (`LAB-003`) Engineering Sprint Lifecycle — adapted, not copied |
| **Decision Journal** | Entry 002, D12–D15 (rationale of record) |

---

## 1. Context & Problem Statement

Cetana Labs has, over eight sprints, accumulated a **working delivery discipline** — RFCs for formal decisions, a branching/PR model (`RFC-LAB-000-004`), a two-surface work environment (`RFC-LAB-000-007`), governance lockstep (CHANGELOG / BACKLOG / journal), and a Decision Journal for reasoning. What it has **not** yet formalized is the **sprint lifecycle itself**: the repeatable sequence a unit of work travels from intent to merged, and — critically — how an **AI agent** executes a delegated unit of work with a contract crisp enough to stand in for conversational context.

Two forces make this the right moment to standardize:

1. **The AIDLC intent.** The trajectory is solo → MVP → onboarded developers and delegated agents (Decision Journal D14). Delegated/agent execution needs a contract that *is* the brief, because the executor has no shared conversational context. An ad-hoc "here's what I want" prompt does not scale to that.
2. **Don't reinvent (D15).** A homegrown `PROMPT.md` contract was considered and rejected: **Kiro Specs** (`requirements.md` with EARS acceptance criteria + `design.md` + `tasks.md`) already *are* that contract, and **Autonomous mode** (plan → sub-agent execution → PR, human-gated at review) already *is* the delegated executor. Building a parallel system would duplicate native capability and fragment portability.

This RFC defines the sprint lifecycle on **Kiro-native features**, keeps the **human gate** as the non-negotiable safety rail, and adapts the delivery *discipline* of the Nexus Pulse lifecycle without importing its multi-team org apparatus (Decision Journal D12).

## 2. Decision (summary)

Adopt a **five-phase, human-gated sprint lifecycle** whose delegated-execution engine is **Kiro Specs + Autonomous mode**:

1. The **contract** for delegated/agent work is a **Kiro Spec** (`requirements.md` EARS = Definition of Done + `design.md` + `tasks.md`), not a custom `PROMPT.md`.
2. **Contract depth scales with executor autonomy** (progressive formality): lead-paired work stays light; delegated-agent / onboarded-dev work gets a full Spec.
3. **Autonomous mode** is the delegated executor: it plans, executes via sub-agents, and opens a PR — **stopping at the human PR gate**.
4. A **lightweight per-sprint `REPORT.md`** is the one genuine addition (the gap Kiro-native features don't cover) — a human sign-off summary, not ceremony.
5. **Defer** the Nexus Pulse roster / Track-A-B multi-contributor structure until real contributors join; model the process by **executor role**, not named people.

Nothing merges to `main` without a human-approved, CI-gated PR (`RFC-LAB-000-004`). This is the AIDLC safety rail and is not negotiable.

## 3. The Five-Phase Sprint Lifecycle

Adapted from the Nexus Pulse five-verb pipeline; each phase names its **surface** (`RFC-LAB-000-007`) and its **human gate** (if any).

| # | Phase | Surface | What happens | Human gate |
| :---: | :--- | :--- | :--- | :--- |
| 1 | **Scope** | Kiro **Web** | Turn intent into a plan: RFC (if a formal decision), backlog rows (`BK-`/`TSK-` IDs), and — for delegated work — a **Spec** (`requirements.md`/`design.md`/`tasks.md`). | Human approves scope before build starts (`/sprint-start`). |
| 2 | **Build** | Kiro **IDE** | Executor implements on a `feat/` branch. **Delegated-agent** work runs in **Autonomous mode** off the Spec's `tasks.md`; **lead-paired** work is interactive. | — (self-validated) |
| 3 | **Validate** | Kiro **IDE** | `make validate-local` / 5-pillar governance gate + build; agent self-checks against the EARS acceptance criteria (the Spec's DoD). | — (gate is machine-enforced; CI mirrors on PR) |
| 4 | **Review** | Kiro **Web** | Agent opens a PR (`gh api`, per `RFC-LAB-000-004`). Human reviews via `/review-pr` (planned); **STOP-and-hold** on any unresolved concern. CI must be green. | **The gate.** Human approves → squash-merge; else iterate. |
| 5 | **Record** | Kiro **Web** | Governance lockstep (CHANGELOG / BACKLOG / journal / `data/`); Decision Journal entry for decisions (`/brainstorm-save`); `REPORT.md` for sign-off; release tag at `/sprint-done`. | Human curates the journal (never auto-run, per D17). |

```
  Scope (Web)         Build (IDE)            Validate (IDE)     Review (Web)        Record (Web)
  ───────────         ───────────            ──────────────     ───────────         ───────────
  intent → Spec  ─▶  agent/lead on feat/ ─▶  make validate-  ─▶  PR + /review-pr ─▶  CHANGELOG/
  (RFC + tasks)      (Autonomous mode)       local + CI self-   STOP-and-hold        BACKLOG/journal
       ▲                                     check vs EARS      (human gate)         + REPORT + tag
       │                                                             │
       └──────────────────── iterate on rejection ◀─────────────────┘
```

## 4. The Contract: Kiro Specs (not a custom PROMPT.md)

A delegated unit of work is specified as a **Kiro Spec** — the native artifact that carries the full brief for an executor with no conversational context:

| Spec file | Role in the contract | Maps to |
| :--- | :--- | :--- |
| `requirements.md` | **EARS acceptance criteria = Definition of Done.** Testable, unambiguous "when X, the system shall Y". | The *what* / the gate |
| `design.md` | Technical approach, interfaces, data touchpoints, trade-offs. | The *how* |
| `tasks.md` | Ordered, checkable implementation steps. | The *plan* Autonomous mode executes |

**Why Specs over a homegrown `PROMPT.md` (D15):**
- **EARS is a more testable DoD** than freeform prose — acceptance criteria double as the review checklist and the agent's self-validation target.
- **Native + portable:** Specs live in `.kiro/` and travel to both surfaces with the repo, exactly like the standardized skillset (`RFC-LAB-000-007` §2.4) and steering.
- **No parallel system to maintain:** Autonomous mode already consumes `tasks.md`; building a custom contract format would duplicate that and drift from the tool.

> **Honest caveat (of record, D15):** the Kiro docs do not confirm the exact mechanics of running **Autonomous mode over an existing Spec's `tasks.md`** (as opposed to Autonomous authoring its own plan). This chaining is **UNDOCUMENTED** and is resolved by the AIDLC spike in §7 — not assumed here.

## 5. Progressive Formality (right-sized by executor role)

Contract depth scales with executor **autonomy**, not with the person — so the process scales solo → team without a rewrite (Decision Journal D13, D14; consistent with `docs/ai-collaboration-model.md` §4).

| Executor role | Contract | Rationale |
| :--- | :--- | :--- |
| **Lead-paired** (human + AI, live) | **Light** — a backlog row / quick ask | Context is supplied conversationally; a full Spec is overhead. |
| **Delegated agent** (AIDLC) | **Full Kiro Spec** | The agent has no conversational context — **the Spec *is* its brief**. |
| **Onboarded developer** | **Full Kiro Spec** | Cold pickup needs the complete contract + DoD. |

The lifecycle (§3) is the same for all three; only the **Scope-phase artifact weight** changes. This keeps solo-pairing frictionless today while the delegated-agent path is fully specified for the AIDLC experiment and future onboarding.

## 6. Human Gate & Governance Guarantees (why this is trustworthy, not just fast)

The gate is what makes delegating to an autonomous agent safe. Reaffirmed from `docs/ai-collaboration-model.md` §6 and bound to this lifecycle:

- **Human gate on every merge** (Phase 4) — `/review-pr` + STOP-and-hold; nothing reaches `main` unapproved. This is the AIDLC safety rail.
- **CI-gated** — portfolio + 5-pillar + build checks must pass before merge (`RFC-LAB-000-004`).
- **Lockstep** — CHANGELOG / BACKLOG / journal / `data/` stay synchronized (validator-enforced) in Phase 5.
- **Auditable reasoning** — the Decision Journal records *why*, including honest failures; `/brainstorm-save` captures decisions, human-curated (never auto-run — D17).
- **Linear history** — squash-merge, branch deletion, no force-push to `main`.

## 7. First Experiment: MVP Task M1 as a Kiro Spec (the AIDLC spike)

Per Decision Journal D11/D15, the first trial of this lifecycle is **MVP task M1** (`RFC-LAB-000-008` §6): *wire `app/web/src/lib/data.ts` from the static `data/status.json` snapshot to the live PocketBase JS SDK*.

Why M1 is the right first Spec:
- **Highest leverage** — it closes the core "backend live + UI live, but disconnected" gap (`RFC-LAB-000-008` §3).
- **Fully local-testable** — no deploy/org-transfer dependency (M1–M4 are local; only M5 needs the transfer).
- **Well-bounded** — one file's data source flips, with clear read-parity acceptance criteria.

**What the spike must determine (resolving §4's caveat):**
1. Whether Autonomous mode can execute an **existing** Spec's `tasks.md`, or whether it authors its own plan from `requirements.md` — and which produces a cleaner PR.
2. The right **hand-off point** between Scope (Web) and Build (IDE) for a Spec-driven run.
3. Whether the EARS acceptance criteria are **sufficient as the agent's self-validation target** or need supplementing.

**Deliverable of the spike:** an M1 PR produced via the lifecycle, plus a short note (in the M1 `REPORT.md` and/or a Decision Journal entry) recording the chaining mechanics that actually worked — so the process is documented from evidence, not assumption.

## 8. What We Deliberately Do NOT Adopt (scope honesty)

Adapted from Nexus Pulse, **not** copied (Decision Journal D12). Deferred until there are real contributors:

- **Roster & Track-A / Track-B** multi-contributor structure — premature for solo + AI today.
- **Role-based broadcasts** and named-person assignment — the process is defined by **executor role**, not people.
- **Heavy PROMPT/REPORT envelopes** — replaced by native Specs; only a **lightweight `REPORT.md`** for sign-off is kept.

These are captured here so scope stays honest and the team ceremony can be switched on later without a process rewrite.

## 9. Deliverables

- **This RFC.**
- (Follow-on, separate PRs — not this docs RFC) `/review-pr` skill (`.kiro/skills/`, planned in `ai-collaboration-model.md`); a `REPORT.md` template; the M1 Spec (`.kiro/specs/`) as the first AIDLC artifact.

## 10. Open Questions

1. **Autonomous-over-existing-Spec chaining** — the core undocumented mechanic; resolved empirically by the §7 spike.
2. **`REPORT.md` placement & granularity** — per-sprint vs. per-Spec; how much it duplicates the Decision Journal vs. complements it. *(Leaning: per-sprint, thin, human sign-off only.)*
3. **`/review-pr` scope** — how much it automates (CI-status + checklist surfacing) vs. leaves to human judgment, without eroding the STOP-and-hold gate.
4. **When to switch on Track-A/B + roster** — the trigger event (first non-lead contributor) that promotes §8's deferred structure into the active process.

## 11. Risks & Mitigations

| Risk | Mitigation |
| :--- | :--- |
| Undocumented Autonomous+Spec chaining fails or is awkward | §7 spike de-risks on the smallest useful task (M1); findings recorded before broader adoption. |
| Autonomous agent merges unreviewed work | Hard human gate at Phase 4 (`RFC-LAB-000-004` PR + CI); Autonomous stops at PR, never merges. |
| Process ceremony outpaces a solo team | Progressive formality (§5) keeps lead-paired work light; full Spec only for delegated/onboarded execution. |
| Premature multi-team structure | §8 defers roster/tracks until real contributors; executor-role model scales without rewrite. |
| `REPORT.md` becomes noise duplicating the journal | §10.2 keeps it thin and sign-off-only; Decision Journal stays the curated reasoning record. |
