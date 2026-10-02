# RFC-LAB-000-014: Multi-Executor Model — cost-first routing across Kiro IDE + Google Antigravity

| Property | Value |
| :--- | :--- |
| **RFC ID** | `RFC-LAB-000-014` |
| **Title** | Executor as a multi-instance role; cost-first routing (default Antigravity, escalate to Kiro IDE) |
| **Author** | Eialarasu (LAB-000 Control Hub) |
| **Status** | ✅ Accepted (2026-10-01) · **§7 trial PASSED 2026-10-02** — Antigravity is a live Executor and cost-first routing is standing practice; §8 lockstep done (see Decision Journal Entry 021, trial build PR #58 / `BK-024`) |
| **Date** | 2026-10-01 |
| **Builds On** | `RFC-LAB-000-007` (surface roles / work environment), `RFC-LAB-000-009` (sprint lifecycle / gate), `RFC-LAB-000-004` (branching) |
| **Decision Journal** | Entry 017 (Operator/Executor/fallback), 018 (background-worker lane + workspace isolation) |

---

## 1. Context & Problem Statement

The operating model (`RFC-LAB-000-007`, Journal 017) defines **one Executor** — Kiro IDE — that runs `/spec-run`, builds on a `feat/` branch, verifies, and opens a PR. Two features have shipped through it (`push-changes-skills`, `fix-bk023-frontend-deploy-signal`); the model works.

**The problem is cost, not capability.** Kiro IDE execution consumes **Kiro Pro+ credits (firm-budgeted — finite)**. **Google Antigravity (AI Pro) is free** (bundled with the broadband plan). Routing routine builds to the free executor and reserving the budgeted one for where it earns its keep would materially cut cost **without changing the model** — because "Executor" was deliberately defined as a **role, not a product** (`RFC-LAB-000-007` §4: "defined by executor role, not named people").

Secondary (minor) driver: occasionally run **parallel** builds (two independent Specs at once). This is **rare and functionality-dependent**, not the main intent — the primary intent is **cost reduction**.

## 2. Decision (summary)

1. **Executor is a multi-instance role.** The pipeline supports **≥1 Executor**; adding one is an instance of an existing role, not a model change.
2. **Registered executors:** **Kiro IDE** (Kiro-native `/spec-run`; firm-budgeted credits) and **Google Antigravity IDE** (free, AI Pro; executes the Spec's `tasks.md` directly — the *contract* is portable even where the `/spec-run` slash-command is not).
3. **Cost-first routing (the default):** **default to Antigravity (free); escalate to Kiro IDE only with a stated reason.** (Routing table — §4.)
4. **Workspace isolation per executor** (extends `RFC-LAB-000-007`/Journal D63): one clone each — `cetana-labs/` (Operator), `cetana-labs-kiro-ide/`, `cetana-labs-antigravity/` — syncing only via `origin`, never a shared worktree.
5. **The gate is invariant.** More executors = more build *throughput*, never more merge *authority*. Every PR, from any executor, goes through the identical `/review-pr` + human gate. The Operator still never merges.
6. **The contract is identical across executors.** Every executor reads the same Kiro Spec, works on a `feat/` branch, never pushes `main`, writes the same `REPORT.md` verification record, and shares the committed `.kiro/`. Only the *tool* differs — never the contract.

## 3. What makes a surface a valid Executor (the contract)

A surface qualifies as an Executor — regardless of vendor — iff it can honor **all** of:
- **Reads a Kiro Spec** (`requirements.md` EARS DoD, `design.md`, `tasks.md`) as its brief and executes `tasks.md`.
- **Branch discipline:** builds on a `feat/|fix/|chore/|refactor/` branch; **never pushes `main`**; opens a PR (`gh api`).
- **Verification record:** produces/updates `.kiro/specs/<id>/REPORT.md` (the evidence `/review-pr` consumes).
- **Shared config:** uses the committed `.kiro/` (skills/specs/steering travel via the repo); its own clone.
- **STOP-and-hold:** opens the PR and stops — never merges, never self-approves.

**Antigravity-specific note:** it is **not Kiro-native**, so `/spec-run` as a *slash command* may be absent. Mitigation: its agent executes `tasks.md` from the Spec directly (the Spec *is* the brief — `RFC-LAB-000-007` progressive formality). Confirm at adoption (§7 trial) that it can read the Spec, honor the branch/PR/REPORT contract, and see `.kiro/`.

## 4. Cost-first routing heuristic (the decision rule)

**Default to the free executor; escalate to the budgeted one only with a stated reason.**

| Build class | Executor | Why |
| :--- | :--- | :--- |
| **Routine / mechanical / docs-and-skills / bulk / low-risk** (default) | **Antigravity (free)** | No credit cost; the bulk of builds. The *default route*. |
| **Complex / high-stakes / deep-codebase / Kiro-native-feature-dependent** | **Kiro IDE (budgeted)** | Worth the credits where capability or Kiro-native tooling earns it. **Escalation requires a one-line reason.** |
| **Occasional parallel** (two independent Specs, rare, functionality-driven) | **both** (one Spec each, separate clones) | Only when two Specs are genuinely independent and throughput matters. Not the norm. |

- **Routing is advisory, recorded, and the human's to override.** The Operator proposes the route (with the reason when escalating to Kiro IDE); the human decides. Default is always Antigravity unless a reason is stated.
- **Credit math is measured, not assumed** (§7): the trial compares the *same class* of Spec on both to validate the saving and the capability fit before this becomes standing practice.

## 5. Guarantees preserved (why this stays trustworthy)
- **Human gate unchanged** — every PR, any executor, gated identically (`RFC-LAB-000-009` §4). The gate is the invariant.
- **Branching unchanged** — app code via PR+CI+squash; `main` never pushed by an executor (`RFC-LAB-000-004`).
- **One contract** — identical Spec/branch/PR/REPORT across executors; the moment an executor needs a *different* contract, that is a new RFC, not a silent fork.
- **Isolation** — clone-per-executor; `origin` is the only sync point.

## 6. Risks & mitigations
| Risk | Mitigation |
| :--- | :--- |
| Antigravity can't honor the full contract (no `/spec-run`, can't see `.kiro/`, won't write REPORT) | §7 trial gates adoption; if it can't, it stays a non-executor (fallback: Kiro IDE only). |
| "Free" isn't actually cheaper end-to-end (rework, slower, more review cycles) | §7 measures credits **and** fit on the same Spec class; routing is revisited on evidence. |
| Contract fork (Antigravity does Specs its own way) | §2.6 / §5 hard rule: identical contract or it's a new RFC. |
| Coordination overhead (which clone built what; parallel-merge ordering) | Operator coordinates + records the route; parallel is rare by design (§1). |
| Quality drift on the cheaper executor | The gate is identical — a weaker build simply HOLDs at `/review-pr`; cost routing never relaxes the gate. |

## 7. Trial (before this is standing practice)
- Run **one real Spec on Antigravity** end-to-end (`feat/` branch → `tasks.md` → REPORT → PR → `/review-pr` → gate). Candidate: a routine docs/skills Spec (e.g. `review-record`, if not already built on Kiro IDE).
- **Measure:** credits consumed (both plans), wall-clock, review iterations, contract adherence (did it write REPORT? honor the branch/PR/`main` rules?).
- **Record** the findings in the Decision Journal; promote cost-first routing to standing practice only if the trial confirms saving **and** fit.

## 8. Deliverables
- This RFC.
- Lockstep: `ai-collaboration-model.md §2` (Executor → "Executor(s)" + routing note), the standing lesson, the **Working Model** artifact (Executor lane shows both executors + the cost-first default), `AGENTS.md` surface line.
- A new clone `cetana-labs-antigravity/` ([HUMAN] setup) + Antigravity onboarded on it.
- Decision Journal entry (the decision + the §7 trial findings when run).

## 9. Open Questions
1. Does Antigravity reliably read `.kiro/` steering + the Spec as its brief without a Kiro-native loader? *(Resolved by the §7 trial.)*
2. Should the routing table live in `AGENTS.md` (always-on) or just the RFC + lesson? *Leaning: a one-line pointer in `AGENTS.md`, full table here.*
3. Credit accounting: is there a simple way to attribute per-build cost, or is it eyeballed from each plan's dashboard? *Deferred to the trial.*
