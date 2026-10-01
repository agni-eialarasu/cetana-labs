# Review-Record — Tasks

| Property | Value |
| :--- | :--- |
| **Spec ID** | `review-record` |
| **Branch** | `feat/review-record` (self-created by `/spec-run`) |
| **Execution** | Kiro IDE Executor (clone `cetana-labs-kiro-ide/`) via `/spec-run review-record` |

---

## T0 — Preflight (STOP on failure)
- [ ] Surface = Kiro IDE/local, Executor clone; `gh` authed. *(P1)*
- [ ] Spec merged to `main` (merge-first). *(P3)*
- [ ] Create `feat/review-record` off up-to-date `main`; clean tree. *(P2)*
- [ ] Baseline `/validate-local` green. *(P4)*

## T1 — Edit `/review-pr` to post the verdict comment  → R1, R2, R5
- [ ] In `.kiro/skills/review-pr/SKILL.md` §6, add a final sub-step: post the checklist + verdict as a PR comment via `gh api …/issues/<n>/comments` — **comment only, never `pulls/<n>/reviews`**. *(R1.1, R1.3)*
- [ ] Body carries the recommendation-not-approval header + the per-row evidence table (CI, Vercel status, scope, EARS, verification, lockstep). *(R1.2, R1.4)*
- [ ] HOLD verdicts are posted too (verdict HOLD + blocking reasons). *(R2.1)*
- [ ] Keep the skill read-only / STOP-and-hold / never-merge / **never-approve**. *(R5.1)*

## T2 — Idempotency  → R3
- [ ] Add a dated run header (`gate run — <ISO date>`) so re-runs are distinguishable; optionally (if simple) edit the prior gate comment in place via a hidden marker + `PATCH issues/comments/<id>`.

## T3 — Docs lockstep  → R4
- [ ] `ai-collaboration-model.md §6`: note the gate verdict is recorded transactionally on the PR.
- [ ] `CHANGELOG.md` `[Unreleased]` entry; backlog/tracker rows.

## T4 — Self-validate  → R5
- [ ] `/validate-local` green; `/review-pr` unchanged except the added comment step; confirm no `pulls/<n>/reviews` call anywhere in the skill.
- [ ] Walk R1–R5 against the diff; note gaps in `REPORT.md`.

## T5 — Open PR (STOP-and-hold; never merge)
- [ ] Push `feat/review-record`; open PR via `gh api`. STOP for `/review-pr` + the human gate. *(This PR's own review will exercise the new comment-posting behavior.)*
