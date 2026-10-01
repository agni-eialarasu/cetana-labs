# Frontend Deploy Signal — Design

| Property | Value |
| :--- | :--- |
| **Spec ID** | `fix-bk023-frontend-deploy-signal` |
| **Branch** | `feat/fix-bk023-frontend-deploy-signal` |
| **Builds on** | `/review-pr` skill; `scripts/verify-bundle.sh` (`BK-017`); `RFC-LAB-000-011/-012` |

---

## 1. Approach — use Vercel's real signal (C), verify reality once (B)

Two complementary signals, each at the right moment:

```
PR open ──▶ /review-pr reads commits/<head-sha>/status → `Vercel` context
            success+SHA-match ⇒ ✅   | not-success / stale / missing ⇒ HOLD      (C, pre-merge)
                                                   │
                                            human squash-merge
                                                   │
            Vercel Git integration deploys ──▶ scripts/verify-live-frontend.sh
            asserts live bundle has VITE_PB_URL + no /api/realtime ⇒ ops-alert    (B, post-merge)
```

- **C is the pre-merge gate signal** — the truest cheap signal: Vercel's own deployment status for *this commit*. Fixes the exact blind spot (gate trusted "Preview Comments").
- **B is the post-merge reality check** — C says "the build succeeded"; B says "the right bundle is actually served." Ops-alert semantics (never reverts a merge), mirroring the backend `BK-022` deploy check.

## 2. C — reading the right status (the subtlety)

The incident's trap: during the 3-failure window Vercel kept serving the last *successful* build, so a naive "is there a `Vercel` success anywhere?" would read green while the latest commit was broken. **Guard:** the gate matches the `Vercel` status to the **PR head SHA** and treats *success on an older SHA* / *no status for head* as **⚠️ HOLD**, not a pass.

```bash
head=$(gh api repos/agni-eialarasu/cetana-labs/pulls/<n> --jq .head.sha)
gh api repos/agni-eialarasu/cetana-labs/commits/$head/status \
  --jq '.statuses[] | select(.context=="Vercel") | {state, target_url, updated_at}'
# empty  → ⚠️ no Vercel status for head → HOLD
# failure/error → ❌ HOLD
# success → ✅ (and it IS for head, since we queried head's SHA)
```
**P5 open item resolved at build:** confirm whether a *failed* Vercel build posts a `failure`/`error` state (clean ❌) or is simply absent (⚠️ handled by the missing-status branch). Either way the gate HOLDs — the guard is failure-safe.

## 3. B — the live-bundle assertion

Reuse the `verify-bundle.sh` idea (`BK-017`) but against the **live site**, not the local `build/`:
```bash
# scripts/verify-live-frontend.sh <url> [expected_pb_url]
# 1. curl the site + its main JS bundle
# 2. assert the bundle contains the expected VITE_PB_URL (Railway PB)
# 3. assert it does NOT contain the realtime-popup OAuth path (/api/realtime for auth)
# non-zero + message on any mismatch
```
Runs post-merge (a small `workflow_dispatch` + on-push-to-main step, or on-demand locally). **Ops-alert, not a gate** — a red result never reverts the merge (`done` = the gated merge, Entry 014 D50).

## 4. Why NOT option A (CI mirrors Vercel's build) — rejected

A would make CI build from `app/web` with no Python prestep + schema-check `vercel.json`. Rejected because **C supersedes it**: A is a *proxy* for "did Vercel's build pass," and C reads that answer *directly* from Vercel. Maintaining a CI mirror of Vercel's exact build env is drift-prone (every Vercel config change must be re-mirrored). Use the real signal, not a simulation. *(Kept as a note; not built.)*

## 5. Risks & mitigations
| Risk | Mitigation |
| :--- | :--- |
| Vercel posts success on stale SHA (the incident) | §2 head-SHA match; older-SHA success ⇒ HOLD. |
| Failed build posts no status (silence) rather than `failure` | Missing-status-for-head ⇒ ⚠️ HOLD (failure-safe); confirmed at P5. |
| Context name drift (`Vercel` / `Cetana Lab Staging - cetana-labs`) | Match either known context; P5 re-verifies names before build. |
| Branch protection not yet enforceable (pre-org-transfer) | R3 is [HUMAN]-documented now, applied when protection lands; `/review-pr` enforces in the meantime. |
| Live check flaky (network) | On-demand + post-merge only; never in PR-gating CI (R5.2); clear retriable message. |
