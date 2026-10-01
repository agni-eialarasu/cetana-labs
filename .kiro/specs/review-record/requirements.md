# Review-Record — Requirements

| Property | Value |
| :--- | :--- |
| **Spec ID** | `review-record` |
| **Feature** | `/review-pr` posts its gate verdict as a **PR comment** (transactional, auditable record) — recommendation only, never a GitHub approving review |
| **Backlog** | `BK-` (governance/DX) — `TSK-TBD` |
| **Status** | 🟡 Proposed (authored on KiroCrew Operator; execution on Kiro IDE Executor) |
| **RFCs** | `RFC-LAB-000-009` (lifecycle §4 gate), `RFC-LAB-000-004` (branching) |
| **Executor role** | Delegated-agent / onboarded-dev |

---

## 1. Introduction

The `/review-pr` gate currently produces its verdict **only in chat** — ephemeral, not attached to the PR it judges. Nothing on the artifact records that the gate ran, what it checked, or that it returned READY/HOLD. This breaks the model's **auditable** principle (`ai-collaboration-model.md §6`) and leaves a reviewer/auditor on GitHub with no evidence the gate happened. (Surfaced 2026-10-01 reviewing PR #54; a one-off comment was posted manually — this Spec makes it standard.)

**Fix:** `/review-pr` ends by posting its checklist + verdict as a **PR comment** via `gh api`, explicitly a **recommendation, not an approval**. **This is DX/governance plumbing** — edits the `review-pr` skill only; no app/`data`/migration logic.

## 0. Preconditions (preflight — enforced by `tasks.md` T0)
- **P1 — Surface:** Kiro IDE/local (Executor clone `cetana-labs-kiro-ide/`); `gh` authed.
- **P2 — Branch:** `feat/review-record` off up-to-date `main`; clean tree; not `main`.
- **P3 — Merge-first:** this Spec merged to `main` before `/spec-run`.
- **P4 — Baseline green:** `/validate-local` passes.

## 2. Current-state facts (verified)
- `review-pr` SKILL §6 emits the checklist to chat + STOP-and-holds; it does **not** write to the PR.
- The skill's Rules already forbid **posting an approving review via the API** (the human gate) — this Spec must preserve that: a **comment**, never an approve/request-changes *review*.
- `gh api repos/<owner>/<repo>/issues/<n>/comments -f body=…` posts an issue comment on a PR (verified working on #54, `issuecomment-5933374174`).

## 3. Requirements (EARS acceptance criteria = DoD)

### R1 — Post the verdict as a PR comment
- **R1.1** At the end of step 6, `/review-pr` SHALL post its checklist + verdict (READY / HOLD) as a **PR comment** via `gh api …/issues/<n>/comments`.
- **R1.2** The comment SHALL be explicitly labeled a **recommendation, not an approval** — stating the human still authorizes the merge (`RFC-LAB-000-009` §4; Operator never merges).
- **R1.3** The skill SHALL NOT post a GitHub **review** (no approve / request-changes via `pulls/<n>/reviews`) — comment only. *(Preserves the existing never-approve rule.)*
- **R1.4** The comment body SHALL carry the per-row evidence (CI, Vercel deploy status, scope, EARS DoD, verification record, lockstep) so the PR is self-documenting without a checkout.

### R2 — HOLD is recorded too
- **R2.1** WHEN the verdict is HOLD, the skill SHALL still post the comment (verdict HOLD + the blocking reasons), so a held PR shows *why* on the artifact. *(The record is not success-only.)*

### R3 — Idempotency / no spam
- **R3.1** On re-running `/review-pr` for the same PR, the skill SHOULD update/supersede its prior gate comment (or clearly mark a new dated run) rather than silently stacking identical comments. *(Lean: a short dated header per run is acceptable; an edit-in-place is nicer-to-have.)*

### R4 — Docs lockstep
- **R4.1** `ai-collaboration-model.md §6` (governance guarantees) SHALL note that the gate verdict is recorded transactionally on the PR.
- **R4.2** `CHANGELOG.md` `[Unreleased]`; backlog/tracker rows updated.

### R5 — No regression
- **R5.1** `/review-pr` SHALL remain read-only w.r.t. the repo, STOP-and-hold, never-merge, never-approve (`RFC-LAB-000-009` §4) — this adds a *comment*, not an action on the merge.

## 4. Out of scope
- Posting GitHub approve/request-changes reviews (forbidden — the human gate).
- Any auto-merge or status-check creation.

## 5. Human Verification Plan
1. Run `/review-pr <n>` on a READY PR → a gate comment appears on the PR, labeled recommendation-not-approval, with the evidence table (R1).
2. Run it on a HOLD PR → a comment with verdict HOLD + reasons appears (R2).
3. Confirm no GitHub *review* (approve/request-changes) was posted — only an issue comment (R1.3/R5.1).
4. Re-run on the same PR → prior gate comment is updated or clearly re-dated, not blindly duplicated (R3).
