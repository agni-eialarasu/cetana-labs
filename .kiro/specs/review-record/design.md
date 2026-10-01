# Review-Record — Design

| Property | Value |
| :--- | :--- |
| **Spec ID** | `review-record` |
| **Branch** | `feat/review-record` |
| **Builds on** | `.kiro/skills/review-pr/SKILL.md` |

---

## 1. Approach
Append a final sub-step to `/review-pr` §6: after emitting the checklist to chat and before STOP-and-hold, **post the same checklist as a PR comment**. The chat output and the PR comment share one rendered body.

```bash
# comment-only — NEVER pulls/<n>/reviews (no approve/request-changes)
gh api repos/agni-eialarasu/cetana-labs/issues/<n>/comments -f body="$VERDICT_MD"
```

The body is the step-6 checklist table + a header line that states **recommendation, not approval; human authorizes the merge.** Verified working on PR #54 (`issuecomment-5933374174`).

## 2. The approve-vs-comment boundary (the critical rule)
GitHub distinguishes an **issue comment** (`issues/<n>/comments` — plain discussion) from a **review** (`pulls/<n>/reviews` with `event: APPROVE|REQUEST_CHANGES|COMMENT`). The skill already forbids an *approving review*. This Spec uses **only the issue-comment endpoint** — it records the verdict without casting a review verdict on GitHub, so the human's approval remains the sole gate. `pulls/<n>/reviews` is **out of scope**, even with `event: COMMENT`.

## 3. Idempotency (R3)
Lean approach: each run posts a comment with a **dated header** (`gate run — <ISO date>`), so re-runs are distinguishable, not confusing. Nicer-to-have (optional, if cheap): find the Operator's prior gate comment (by a hidden marker string) and `PATCH issues/comments/<id>` to update in place. Pick edit-in-place only if it stays simple; otherwise dated-append is acceptable per R3.

## 4. HOLD recording (R2)
Same path for HOLD — the comment leads with **Verdict: HOLD** and lists the blocking rows, so a held PR self-documents why. The skill still STOPs; the comment is the durable trace.

## 5. Risks & mitigations
| Risk | Mitigation |
| :--- | :--- |
| Agent accidentally posts an approving *review* | R1.3 + §2: only `issues/<n>/comments`; `pulls/<n>/reviews` is out of scope. |
| Comment spam on re-runs | R3 dated header or edit-in-place. |
| Comment read as the human's approval | R1.2 explicit "recommendation, not approval; human authorizes merge" header. |
| `gh` auth / rate | Skill already uses `gh api`; failure ⇒ surface in chat, still STOP-and-hold (the chat verdict remains). |
