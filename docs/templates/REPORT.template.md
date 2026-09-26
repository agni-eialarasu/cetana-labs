# Sprint / Spec REPORT — <SPRINT-XX or spec-id>

> **Purpose.** The lightweight human **sign-off** artifact of the sprint lifecycle
> (`RFC-LAB-000-009` §3 Phase 5, §9). It is the one genuine gap Kiro-native features
> don't cover: a thin summary a human signs to close a unit of work. Keep it **thin and
> sign-off-only** — it complements, and must not duplicate, the Decision Journal (which
> records *why*) or the CHANGELOG (which records *what*). Per `RFC-LAB-000-009` §10.2, the
> default granularity is **per-sprint**; author a **per-Spec** REPORT only for a delegated /
> AIDLC Spec run (where the executor had no conversational context and the run itself is
> the thing being signed off).
>
> Copy this file to `docs/reports/REPORT-<SPRINT-XX>.md` (or, for a Spec run,
> `.kiro/specs/<spec-id>/REPORT.md`), fill it in, and have the lead sign §6.

| Property | Value |
| :--- | :--- |
| **Report for** | `<SPRINT-XX>` / Spec `<spec-id>` |
| **Executor role** | Lead-paired · Delegated-agent · Onboarded-dev *(pick one — `RFC-LAB-000-009` §5)* |
| **Surface(s)** | Web (plan) · IDE (execute) |
| **Date** | YYYY-MM-DD |
| **Related** | RFC(s): `RFC-LAB-000-0XX` · Epic/Task: `BK-0XX` / `TSK-0XX` · PR(s): #NN |

---

## 1. Outcome (one paragraph)
<What shipped, in plain terms. The single sentence you'd tell a reviewer.>

## 2. Definition of Done — met? (the gate summary)
> For a Spec run, this is the roll-up of the EARS acceptance criteria (`requirements.md`).
> For a sprint, roll up the planned items. Keep it to the verdict — details live in the PR/Spec.

| DoD item (R#/TSK) | Met? | Evidence (PR, check, note) |
| :--- | :---: | :--- |
| `<R1 / TSK-0XX>` | ✅ / ⚠️ / ❌ | `<PR #NN / CI green / verification>` |
| … | | |

**Verdict:** `DONE` / `DONE with deferrals` / `NOT DONE — <why>`

## 3. Deferred / carried forward (scope honesty)
<Anything intentionally out of scope or pushed to a later phase, with a one-line reason and where it's tracked (BACKLOG id).>

## 4. Human gate
- PR(s): #NN — reviewed via `/review-pr` · CI green · squash-merged: yes/no
- Any STOP-and-hold raised, and how it was resolved: <…>

## 5. AIDLC spike notes *(delegated / autonomous runs only — else "n/a")*
> Only for a Spec executed via Autonomous mode / a delegated agent. Resolves the open
> chaining question in `RFC-LAB-000-009` §7 from **evidence**, not assumption.
- Did Autonomous execute the Spec's `tasks.md` directly, or re-plan from `requirements.md`? <…>
- The Web→IDE hand-off point that worked: <…>
- Were the EARS acceptance criteria sufficient as the agent's self-validation target? <…>
- Anything to fold back into `RFC-LAB-000-009` / the Spec method: <…>

## 6. Sign-off
- **Signed:** `<name>` (`<role>`) — YYYY-MM-DD
- Decision Journal entry created (if this produced a decision)? yes / n/a — `/brainstorm-save` (never auto-run — D17)
- Release tagged (if sprint close)? `/sprint-done` → `vX.Y.0` / n/a
