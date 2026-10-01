# Push-Changes Skills — Tasks

| Property | Value |
| :--- | :--- |
| **Spec ID** | `push-changes-skills` |
| **Branch** | `feat/push-changes-skills` (self-created by `/spec-run`) |
| **Execution** | Kiro IDE Executor via `/spec-run push-changes-skills` |

---

## T0 — Preflight (STOP on failure; never fabricate)
- [ ] Surface = Kiro IDE/local; `/env-doctor` IDE-ready (git configured, `origin` reachable). *(P1)*
- [ ] This Spec is merged to `main` (merge-first). *(P3)*
- [ ] Create `feat/push-changes-skills` off up-to-date `main`; clean tree. *(P2)*
- [ ] Baseline: `/validate-local` green. *(P4)*

## T1 — `/push-changes` skill  → R1, R3
- [ ] Create `.kiro/skills/push-changes/SKILL.md` with `name` + `description` frontmatter.
- [ ] Document the branch-aware push gate (design §2) as the Step-by-Step: list what would push (`git log origin/<branch>..HEAD`), run the gate, push by explicit branch name (`-u` if no upstream), report the pushed ref.
- [ ] Encode refusals: protected-branch + code paths ⇒ refuse with feat/+PR instruction; never force/`--all`/`--mirror`/bare push; nothing-to-push ⇒ clean exit. *(R1.3–R1.5, R3)*

## T2 — `/commit-and-push-changes` skill  → R2, R3
- [ ] Create `.kiro/skills/commit-and-push-changes/SKILL.md` with conforming frontmatter.
- [ ] Procedure: run `/commit-changes` (status + secret/`.idea/` check + prefix + commit), THEN `/push-changes` gate.
- [ ] Cross-reference both parent skills (no rule duplication); include 3 worked examples (feat/ push; docs-on-main confirm; code-on-main refuse-at-push). *(R2.2–R2.4)*

## T3 — Documentation lockstep  → R4
- [ ] Add both skills to `AGENTS.md §4` under governance/lifecycle tooling.
- [ ] *(Operator follow-up, tracked not executed here)* update working-model diagram artifact `fd26dcf5ca990145` to show the two skills on the Operator surface.

## T4 — Self-validate against the EARS DoD  → R5
- [ ] Re-run `/validate-local` — green, no new drift. *(R5.2)*
- [ ] Confirm `/commit-changes` behavior unchanged. *(R5.1)*
- [ ] Walk each R1/R2 criterion against the two SKILL.md files; note any gap in `REPORT.md`.

## T5 — Open PR (STOP-and-hold; never merge)
- [ ] Push `feat/push-changes-skills`; open a PR via `gh api repos/{owner}/{repo}/pulls`.
- [ ] PR body: summary, the EARS DoD checklist, what was validated. STOP for `/review-pr` + the human gate.
