---
name: spec-run
description: >-
  The Kiro IDE one-liner that executes a merged Kiro Spec end-to-end for Cetana Labs (RFC-LAB-000-009 Phase 2 Build / the "implement" phase). Given only a spec id, it owns everything repeatable — syncs main, self-checks the phase state, runs a silent preflight (surface, toolchain, git, deps, env/data), creates the branch the Spec names — then executes tasks.md, self-validates against the requirements.md EARS DoD (the per-task functional + verification concern), and opens a PR — then STOP-and-holds. NEVER merges. Use when the user runs /spec-run <spec-id>.
---

# Skill: Run a Spec (`/spec-run <spec-id>`)

## Objective
Make executing a Kiro Spec a **true one-liner** in Kiro IDE — the **implement** phase of the lifecycle (`RFC-LAB-000-009` §3, Build). You supply only the **spec id**; the skill owns *everything repeatable* (git sync, branch checkout, env/toolchain/deps preflight, PR mechanics) so your attention is spent only on the two things that vary per task: **the functional change and its verification** (encoded in the Spec's `tasks.md` + EARS DoD). It ends by opening a PR and **STOP-and-holds** for the human gate (`/review-pr`). It **never merges**.

### Lifecycle position & the merge-first rule
```
/plan-start* → /plan-done   →   /spec-run <id>   →   /review-pr <PR>   →   /sprint-done
  (brainstorm/Scope, Web)        (implement/IDE)       (verify/Web)          (done/Record)
   authors + MERGES the Spec      THIS SKILL
```
- **Merge-first (precondition):** the Spec is authored and **merged to `main` as a doc PR during Scope** (`/plan-done`). That is what lets `/spec-run` need only the id — the Spec is already on `main`, so this skill can `git pull` and find it with **no manual branch checkout**. If the Spec is not on `main`, this skill STOPs and tells you to merge the plan first (see §2). This is the deliberate design that removes the extra checkout step (`RFC-LAB-000-009` state machine).

## Trigger Patterns
- `/spec-run <spec-id>`  (e.g. `/spec-run mvp-m1-live-pocketbase`)
- "run the M1 spec", "execute spec <id>", "implement <spec-id>"

## Steps

### 1. Surface gate + sync main (repeatable — the skill owns this)
- Confirm the surface is **Kiro IDE / local (stateful)**. If on Kiro Web, STOP: "Spec runs need the IDE (it runs the stack); switch surfaces." (`RFC-LAB-000-007` §2.1)
- Sync `main` so the merged Spec is present — **the user does NOT check anything out**:
  ```bash
  git fetch origin && git checkout main && git pull --ff-only
  ```

### 2. State guard — resolve the Spec on `main` (merge-first check)
- Look for `.kiro/specs/<spec-id>/` **on `main`**.
  - **Present ⇒ proceed.**
  - **Missing, but an OPEN plan/Spec PR exists for it ⇒ ALERT + HOLD** (do not proceed): "Spec `<id>` isn't on `main` yet — it's still in plan PR #NN. Merge the plan first (`/review-pr` → merge), then re-run `/spec-run <id>`." *(A missing prerequisite is a HOLD, never a silent skip — `RFC-LAB-000-009` state-guard semantics.)*
  - **Missing entirely ⇒ STOP** and list available specs (`ls .kiro/specs/`).
- Read `requirements.md` (EARS DoD + §0 Preconditions), `design.md`, and `tasks.md` (ordered plan + the **Execution header**: branch name, surface, EARS target).
- Echo a one-line plan: spec id · target branch (from the header) · task count. This confirms the contract before acting.

### 3. Silent preflight (repeatable — surfaced ONLY if something's broken)
- Run the Spec's `tasks.md` **T0** / `requirements.md` **§0** pre-checks: clean tree, toolchain (node/pnpm/python/pocketbase), deps installed, `.env` present, `data/` masters present, not stale.
- **If all green: print ONE line** (`✅ Preflight OK (surface, toolchain, git, deps, env) — proceeding`) and continue. Do **not** spend the user's attention on green checks.
- **If any check fails: show the ✅/❌ table and STOP-and-hold** with the exact fix. (Preflight is a *tripwire*, never a bypass.)

### 4. Create the branch the Spec names (repeatable)
- Read the branch name from the Execution header (e.g. `feat/mvp-m1-live-pocketbase`); do not invent one.
- From the now-synced `main`, create/checkout it (`RFC-LAB-000-004` naming); confirm the current branch is **not** `main`/`master`.
  ```bash
  git checkout -b <branch-from-spec>    # or checkout if it already exists (resume)
  ```

### 5. Execute `tasks.md` in order (the FUNCTIONAL concern — what varies)
- Work tasks **sequentially** (T1, T2, …), checking each off as its cited requirement is satisfied. Honor per-task STOP conditions.
- The Spec's **"Out of Scope"** is a hard boundary — never pull later phases forward.
- If a task is genuinely blocked, STOP and report which task and why — never silently skip a functional step.

### 6. Self-validate against the EARS DoD (the VERIFICATION concern — what varies)
- Walk every `requirements.md` acceptance criterion (R1, R2, …); run the Spec's own verification steps (e.g. parity/fallback checks) plus the standard gates:
  ```bash
  pnpm --dir app/web check && pnpm --dir app/web build && pnpm --dir app/web lint
  just validate-local
  ```
- Any unmet/unverifiable criterion ⇒ resolve or STOP with a clear note. A green build is necessary but **not** sufficient — the DoD is the bar.

### 7. Commit, open the PR, STOP (repeatable — never merge)
- Commit with a semantic message referencing the Spec's epic/task (`feat(...): <spec-id> — <summary> (BK-0XX)`).
- Push and open the PR into `main` via `gh api` (REST — `gh pr create`/GraphQL fail in this environment):
  ```bash
  git push -u origin <branch>
  gh api repos/agni-eialarasu/cetana-labs/pulls -f title="..." -f head="<branch>" -f base="main" -f body="..."
  ```
- PR body: DoD roll-up + link to the Spec. Ensure CI goes green.

### 8. Emit the Human Verification Plan, then STOP (open the verify loop)
- Read the **Human Verification Plan** from the Spec's `requirements.md` (the human-executable checklist — distinct from the EARS DoD the agent self-checked; see `RFC-LAB-000-009`). If the Spec has none, note it and fall back to deriving quick steps from R1–R6 (but a Spec *should* carry an authored plan).
- **Emit the plan inline** at the hand-off so the human knows exactly how to verify:
  > "PR #NN is open and CI is green. **Human verification (please run these):**
  > V1 … · V2 … · V3 … — report anything that fails; I'll push fixes to *this* PR (Single-PR rule). When it passes, run **`/verification-done`**."
- **STOP-and-hold.** State is now **IN_VERIFICATION**. Do **not** merge, and do **not** jump to `/review-pr` — the gate comes *after* human verification passes.

### 9. The verify loop + next phase
- **Iterate loop (IN_VERIFICATION):** the human runs the plan; on any finding, fix it and push to the **same PR** (never a new branch/PR — Single-PR rule); the human re-verifies. Repeat until the plan passes.
- On pass, the human runs **`/verification-done`** → it appends the Verification Log to `.kiro/specs/<id>/REPORT.md` (same PR) and transitions **IN_VERIFICATION → IN_REVIEW**.
- Then: **`/review-pr <PR>`** (the **KiroCrew Operator** gate — now reads the verification record as evidence) → human authorizes merge → **`/sprint-done`** (Record).
- If this was an AIDLC/delegated run, also capture the spike notes (`RFC-LAB-000-009` §7) in `REPORT.md`: did this run execute `tasks.md` directly or re-plan, and what hand-off worked.

## Rules
- **You supply only the spec id.** The skill owns all repeatable steps (sync, checkout, preflight, PR). Do not ask the user to check out a branch or run preflight manually.
- **Merge-first:** the Spec must be on `main`. Missing Spec ⇒ HOLD with "merge the plan first" (never fabricate it).
- **Never merge**, never post an approving review — this skill implements and opens; the human gates (`/review-pr`).
- **STOP-and-hold** on: wrong surface (§1), missing-Spec prerequisite (§2), any failed preflight (§3), any blocked task (§5), and always after opening the PR + emitting the Human Verification Plan (§7–§8) — the run ends in IN_VERIFICATION, awaiting the human loop, not at merge.
- **The Spec is the single source of truth** — branch, preconditions, scope, functional tasks, and verification all live in the Spec; no inline overrides. If the Spec lacks an Execution header or §0 preconditions, STOP and ask for them.
- **State-guard semantics** (`RFC-LAB-000-009`): redundant/already-done ⇒ skip + continue; missing prerequisite or gate ⇒ alert + HOLD. Never silently bypass a gate.
- **IDE-only**; GitHub via `gh api` (REST).
