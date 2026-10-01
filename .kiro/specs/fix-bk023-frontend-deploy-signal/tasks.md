# Frontend Deploy Signal — Tasks

| Property | Value |
| :--- | :--- |
| **Spec ID** | `fix-bk023-frontend-deploy-signal` |
| **Branch** | `feat/fix-bk023-frontend-deploy-signal` (self-created by `/spec-run`) |
| **Execution** | Kiro IDE Executor (clone `cetana-labs-kiro-ide/`) via `/spec-run fix-bk023-frontend-deploy-signal` |

---

## T0 — Preflight (STOP on failure; never fabricate)
- [ ] Surface = Kiro IDE/local in the Executor clone; `/env-doctor` ready; `gh` authed. *(P1)*
- [ ] This Spec merged to `main` (merge-first). *(P3)*
- [ ] Create `feat/fix-bk023-frontend-deploy-signal` off up-to-date `main`; clean tree. *(P2)*
- [ ] Baseline `/validate-local` green. *(P4)*
- [ ] **Re-verify the Vercel status surface** (`gh api .../commits/<sha>/status`): confirm the `Vercel` context posts per-commit, and record whether a FAILED build posts `failure`/`error` or is silent → sets R1.4's exact guard. *(P5)*

## T1 — `/review-pr`: read Vercel's real deployment status  → R1, R5.1
- [ ] Edit `.kiro/skills/review-pr/SKILL.md`: in the CI/signal section, add a **Frontend deploy (Vercel status)** check that reads `commits/<head-sha>/status`, evaluates the `Vercel` (and `Cetana Lab Staging - cetana-labs`) context, and matches it to the **head SHA**.
- [ ] Encode the states: success-on-head ⇒ ✅; failure/error ⇒ ❌ HOLD; missing-for-head or success-on-older-SHA ⇒ ⚠️ HOLD (per P5 finding). *(R1.2, R1.4)*
- [ ] Relabel "Vercel Preview Comments" explicitly as **comment posting, NOT deploy status**. *(R1.3)*
- [ ] Add the **Frontend deploy** row to the step-6 checklist with evidence (context, state, SHA match). *(R1.5)*
- [ ] Keep the skill read-only / STOP-and-hold / never-merge. *(R5.1)*

## T2 — Post-deploy live-bundle assertion  → R2
- [ ] Add `scripts/verify-live-frontend.sh <url> [expected_pb_url]` — curl the live site + main bundle; assert expected `VITE_PB_URL` present and the realtime-popup OAuth path absent; non-zero + clear message on mismatch. *(R2.1, R2.3)*
- [ ] Wire it post-merge as an **ops-alert** (a `workflow_dispatch` + on-push-to-`main` job, OR documented on-demand) — never a PR-gating or merge-reverting check. *(R2.2, R5.2)*

## T3 — Branch-protection guidance  → R3
- [ ] Document making the **`Vercel` deployment status a required check** on `main` as the durable enforcement; mark **[HUMAN]** (applied when branch protection lands post-org-transfer).

## T4 — Documentation lockstep  → R4
- [ ] `RFC-LAB-000-012` append-only note: the real Vercel signal = commit-status `Vercel` context; "Preview Comments" ≠ deploy signal.
- [ ] `developer-guide.md` §9A: the live-frontend check + reading Vercel status.
- [ ] `CHANGELOG.md` `[Unreleased]` entry; `BACKLOG.md` BK-023 part 2 → done; `SPRINT_TRACKER.md` close `TSK-063`.
- [ ] *(Operator follow-up, tracked not executed here)* Runtime Infrastructure artifact Deploy-plane note. *(R4.3)*

## T5 — Self-validate against the EARS DoD  → R5
- [ ] `/validate-local` green; existing CI unaffected; the live check is NOT in the PR-gating job. *(R5.2)*
- [ ] Walk each R1/R2/R3/R4 criterion against the diff; note gaps in `REPORT.md`.

## T6 — Open PR (STOP-and-hold; never merge)
- [ ] Push `feat/fix-bk023-frontend-deploy-signal`; open a PR via `gh api`. PR body: summary + EARS DoD checklist + what was validated. STOP for `/review-pr` + the human gate.
