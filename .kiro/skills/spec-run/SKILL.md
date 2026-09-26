---
name: spec-run
description: >-
  The IDE one-liner that executes a Kiro Spec end-to-end for Cetana Labs (RFC-LAB-000-009 Phase 2 Build). Given a spec id, it reads the self-describing Spec (.kiro/specs/<id>/), runs the Spec's preflight/pre-checks (surface, clean tree, toolchain, deps, env/data), creates the branch the Spec names, executes tasks.md in order, self-validates against the requirements.md EARS DoD, and opens a PR — then STOP-and-holds for the human gate. NEVER merges. Use when the user runs /spec-run <spec-id>.
---

# Skill: Run a Spec (`/spec-run <spec-id>`)

## Objective
Turn a merged, self-describing **Kiro Spec** into a delivered PR with a single command — the **Build** phase of the sprint lifecycle (`RFC-LAB-000-009` §3), executed on the **Kiro IDE** surface. The Spec is the contract; this skill is the executor that reads it and drives it: **preflight → branch → execute `tasks.md` → self-validate against the EARS DoD → open PR → STOP.**

The one-liner is the DX goal: everything the run needs (branch name, preconditions, ordered tasks) lives *in the Spec*, so `/spec-run <spec-id>` needs no other arguments. This skill **never merges** — it hands off to `/review-pr` (the human gate, Phase 4).

> **Boundary (do not confuse):** `/sprint-start` is a **Web/plan** skill that opens a sprint in `BACKLOG.md` (Scope). `/spec-run` is an **IDE/execute** skill that runs a Spec (Build). Different surface, different phase — kept separate on purpose (`RFC-LAB-000-007` §2.1, `RFC-LAB-000-009` §3).

## Trigger Patterns
- `/spec-run <spec-id>`  (e.g. `/spec-run mvp-m1-live-pocketbase`)
- "run the M1 spec", "execute spec <id>", "kickstart <spec-id> in the IDE"

## Steps

### 0. Resolve the Spec
- Locate `.kiro/specs/<spec-id>/`. If it doesn't exist, list available specs (`ls .kiro/specs/`) and STOP.
- Read all three files: `requirements.md` (EARS DoD + §0 Preconditions), `design.md` (approach), `tasks.md` (ordered plan + the **Execution header** — branch name, surface, kickoff).
- Echo a one-line plan: spec id, target branch (from the Execution header), and task count. This confirms the contract before acting.

### 1. Surface gate (must be Kiro IDE)
- Confirm the current surface is **Kiro IDE / local (stateful)**, not Kiro Web — a Spec run needs to run servers/DB (`RFC-LAB-000-007` §2.1). If on Web, STOP and tell the user to switch to the IDE.
- Run `/env-doctor` (read-only readiness) and require an IDE-**ready** report before proceeding.

### 2. Preflight / pre-checks (from the Spec — STOP on any failure)
- Execute the Spec's **`tasks.md` T0** / **`requirements.md` §0 Preconditions** exactly as written. These are Spec-owned, not hardcoded here — this skill runs whatever the Spec declares. Typical checks:
  - clean working tree (`git status --short`); toolchain (node/pnpm/python/pocketbase); deps installed; `.env` present; `data/` masters present; not stale.
- Emit a ✅/❌ preflight table. **Any ❌ ⇒ STOP-and-hold** (do not start the build). This protects an autonomous run from acting in the wrong surface / on a dirty tree / against an unready stack.

### 3. Create the branch the Spec names
- Read the branch name from the Spec's Execution header (e.g. `feat/mvp-m1-live-pocketbase`); do not invent one.
- From an up-to-date `main`, create/checkout it (`RFC-LAB-000-004` naming). Confirm the current branch is **not** `main`/`master`.
  ```bash
  git fetch origin && git checkout main && git pull --ff-only
  git checkout -b <branch-from-spec>    # or checkout if it already exists
  ```

### 4. Execute `tasks.md` in order
- Work the tasks **sequentially** (T1, T2, …), checking each off as its cited requirement is satisfied. Respect any per-task STOP conditions written in the Spec.
- Stay within the Spec's scope; the Spec's "Out of Scope" section is a hard boundary — do not pull later phases forward.
- If a task is genuinely blocked, STOP and report which task and why — do not silently skip.

### 5. Self-validate against the EARS DoD
- Walk every `requirements.md` acceptance criterion (R1, R2, …) and confirm it is demonstrably met, running the Spec's own verification steps (e.g. parity/fallback checks) and the quality gates:
  ```bash
  pnpm --dir app/web check && pnpm --dir app/web build && pnpm --dir app/web lint
  make validate-local
  ```
- Any unmet/unverifiable criterion ⇒ resolve or STOP with a clear note. A green build is necessary but **not** sufficient — the DoD is the bar.

### 6. Commit, open the PR, and STOP (do NOT merge)
- Commit with a semantic message referencing the Spec's epic/task (e.g. `feat(...): <spec-id> — <summary> (BK-0XX)`).
- Push the branch; open a PR into `main` via `gh api` (REST — the `gh pr create`/GraphQL subcommands are unavailable here):
  ```bash
  git push -u origin <branch>
  gh api repos/agni-eialarasu/cetana-labs/pulls -f title="..." -f head="<branch>" -f base="main" -f body="..."
  ```
- PR body should summarize the DoD roll-up and link the Spec. Ensure CI goes green.
- **STOP-and-hold.** Report the PR number/URL and hand off: "Ready for `/review-pr <PR>` (the human gate)." Do **not** merge.

### 7. Point to the next phase
- Remind the user of the remaining lifecycle: **`/review-pr <PR>`** (Phase 4 gate) → on approval, squash-merge → **Record** (CHANGELOG/BACKLOG lockstep, `/brainstorm-save` if decisions, `REPORT.md` sign-off, release at `/sprint-done`).
- If the Spec is an AIDLC/delegated run, remind the user to capture the spike notes (`RFC-LAB-000-009` §7) in the `REPORT.md` — whether this run executed `tasks.md` directly or re-planned, and the hand-off that worked.

## Rules
- **Never merge** and never post an approving review — this skill executes and opens; the human gates (`/review-pr`).
- **STOP-and-hold** at three points: any failed preflight (§2), any blocked task (§4), and always after opening the PR (§6).
- **The Spec is the source of truth** — branch name, preconditions, and scope come from the Spec, not from this skill. If the Spec lacks an Execution header or §0 preconditions, STOP and ask for them rather than guessing.
- **IDE-only.** If run on Kiro Web, STOP (it can't run the stack).
- Reads/writes to GitHub use `gh api` (REST); `gh pr`/GraphQL subcommands fail in this environment.
- Honor progressive formality (`RFC-LAB-000-009` §5): this skill is for Specs (delegated/onboarded work). Lead-paired quick asks don't need it.
