# Sprint / Spec REPORT — Spec `mvp-m3-m4-rbac-owner-writes`

> Human sign-off artifact for the AIDLC Spec run (`RFC-LAB-000-009` §3 Phase 5).
> Thin and sign-off-only; complements the Decision Journal (*why*) and CHANGELOG (*what*).

| Property | Value |
| :--- | :--- |
| **Report for** | Spec `mvp-m3-m4-rbac-owner-writes` |
| **Executor role** | Delegated-agent (full Spec — `RFC-LAB-000-009` §5) |
| **Surface(s)** | Web (Scope — Spec authored) · IDE (execute + human verify) |
| **Date** | 2026-09-28 |
| **Related** | RFC(s): `RFC-LAB-000-006` (auth/RBAC), `RFC-LAB-000-008` (MVP §4/§6) · Epic/Task: `BK-011` / `TSK-050` · PR(s): #34 |

---

## 1. Outcome (one paragraph)
Completed the MVP's local auth loop: minimum RBAC (public read / owner-writes-own) enforced by PocketBase API rules, plus an owner's in-app status edit (`status_health`/`status_note`) persisting to PocketBase and reflected live in the UI. No RBAC library — the datastore rule is the boundary. M1 read + `status.json` dual-track and M2 sign-in/guard remain intact. Only M5 (deploy) remains for the full MVP.

## 2. Definition of Done — met? (the gate summary)

| DoD item (R#) | Met? | Evidence |
| :--- | :---: | :--- |
| R1 — RBAC matrix enforced + test-proven | ✅ | V3: non-owner 404, owner 200, anon 404, public read 200 |
| R2 — Editable status fields, owner-rule-covered, idempotent seed | ✅ | `status_health`/`status_note`/`status_updated_at`; seed-if-empty importer |
| R3 — Owner write path + reflect | ✅ | V1/V2 (after fixes) |
| R4 — Read status_* back | ✅ | data.ts maps + effective-health merge |
| R5 — Enforcement (rule) vs UX (hide) separated | ✅ | V3 (rule) + V4 (control hidden) independently confirmed |
| R6 — M1/M2 no regression | ✅ | V6 public read intact; M2 sign-in/guard intact |
| R7 — Superuser escape hatch | ✅ | V7: superuser edits any project (incl. unassigned LAB-005) |
| R8 — Gates green | ✅ | V8: check/build/lint + validate-local; CI green |

**Verdict:** `DONE`

## 3. Deferred / carried forward (scope honesty)
- **`BK-016` (new, logged to `main` `1d38667`)** — terminal-state edit policy: a `✅ Completed` project is currently editable by its owner (spec-faithful — minimum RBAC is ownership-only, no state machine). Whether terminal states should be edit-locked / require "reopen" is deferred as a deliberate product call.
- Full 5-role `memberships` model / admin CRUD (`BK-014`); `status_snapshots` history + status.json→PB reconciliation (post-MVP); audit trail; deploy (M5 / `RFC-LAB-000-011`).
- Classic-dashboard footer link retirement — left to M5/RFC-011 deployment cleanup (its owner).

## 4. Corrections & scope decisions during verification (append-only)

Verification surfaced **three issues** that only appeared under live human exercise (the agent's self-validation was type/build/lint-green throughout). All fixed on this PR (Single-PR rule) or logged; two accepted scope nuances noted.

- **`529dde0` — owner-write 404 (the big one).** Owner status edits failed with 404. Root cause: PocketBase creates a **separate auth record per GitHub OAuth identity**, so the OAuth session's `id` ≠ the seeded owner the `projects.owner` relation points to; the original rule `owner = @request.auth.id` denied a *real* owner. Fix (approved Option 3): added `app/pocketbase/pb_hooks/oauth_github_handle.pb.js` (populates `github_handle` on OAuth sign-in) and changed the `updateRule` to match on handle: `@request.auth.id != "" && @request.auth.github_handle != "" && owner.github_handle = @request.auth.github_handle`. Environment-robust (ids change per seed; handles don't). Diagnosed from PB admin **Logs**.
- **`0e13aad` — pill didn't reflect the edit (Option A, accepted scope nuance).** The card's health pill read `status.json` while the owner block read PB `status_health`, so an owner edit updated the block but not the prominent pill. Fix: `data.ts` computes an **effective health** (PB `status_health` wins when set, else snapshot) driving pill/severity/sort; the editor's `onSaved` callback updates the pill live (no reload). *This lets the owner-edited value take visual precedence — a small, deliberate step beyond the Spec's strict "dual-track, no reconciliation" line, accepted by the lead in verification.*
- **Completed-project editability ⇒ `BK-016`.** Not changed (spec-faithful); logged as a backlog decision.

### Environment consolidation (pre-verification, docs to `main`)
- The local PocketBase had **two diverged `pb_data` dirs**; the canonical `app/pocketbase/pb_data` was reset + reseeded so `make start-local` serves the good instance. GitHub OAuth re-added by the lead. Captured the **`pb_data` CWD gotcha + recovery** in `developer-guide.md` (`ab5d8e1`) and the **OAuth ownership-linking** design (`8c44667`).

## 5. Verification Log — human functional verification

### Verification Log — 2026-09-28 (PR #34)
| Plan step | Result | Finding / correction |
| :--- | :---: | :--- |
| V1 — Owner edits own status | ❌→✅ | 404 on save (OAuth-record vs seeded-owner mismatch); fixed `529dde0`. Passed after fix. |
| V2 — Persisted to PB + UI reflects | ❌→✅ | Persistence OK, but the health pill showed the old value (dual-track); fixed `0e13aad`. Passed after fix. |
| V3 — Non-owner denied (rule, SECURITY) | ✅ | Non-owner write → **404** (rule-denied); positive control: owner writes own → 200; no trace left. |
| V4 — Non-owner sees no edit control | ✅ | No owner block on LAB-004/005; present on owned LAB-000/001/002/003. |
| V5 — Anonymous denied | ✅ | Signed-out: no control (UX); anon API write → 404 (rule); no write landed. |
| V6 — Public read intact (M1) | ✅ | Full 6-card dashboard renders anonymously; anon projects readable = 6. |
| V7 — Superuser escape hatch | ✅ | Superuser edits any project incl. unassigned LAB-005 (200/200). |
| V8 — Quality gates | ✅ | `pnpm check` 0/0, build ok, lint only 3 pre-existing; `make validate-local` green; CI green. |

- **Iterations:** 2 code fixups on this PR during verification (`529dde0`, `0e13aad`); 1 behavior logged as backlog (`BK-016`); env consolidation + 2 docs to `main` (`ab5d8e1`, `8c44667`) + `BK-016` (`1d38667`).
- **Verdict:** PASS — human functional verification complete (V1–V8).
- **Verified by:** Agni Eialarasu · **Surface:** Kiro IDE

> **Notes:** (1) V3 (the RBAC security check) was exercised directly via SDK/curl, not assumed — the whole point of minimum RBAC. (2) The owner-write 404 was a genuine design gap M2's read-only verification couldn't catch; worth folding the handle-based linking back into how M2/M4 are described. (3) Test-only passwords (`TestPass2026!`) were set on two seeded accounts for RBAC testing — **rotate/clear post-verification** (known creds).

## 6. Human gate
- PR: #34 — verification PASS recorded; state **IN_REVIEW**, ready for `/review-pr 34` · CI green (Validate Portfolio ✅, Build Sleek UI ✅) · squash-merged: no (awaiting gate).

## 7. Sign-off
- **Signed:** Agni Eialarasu (Lead) — 2026-09-28 — human functional verification PASS (V1–V8).
- Release tagged? n/a — `/sprint-done` (SPRINT-09) will tag at close. **M3–M4 completes the MVP local auth loop; only M5 (deploy) remains.**
