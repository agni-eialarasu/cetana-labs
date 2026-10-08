# `is_admin` Auth Tier — Tasks (`/spec-run is-admin-auth`)

> Executor = **Kiro IDE** (security-sensitive, budgeted — escalated from Antigravity default per `RFC-LAB-000-014`). Implements `RFC-LAB-000-008` A1. STOP-and-hold at the PR; never merge.

---

## T0 — Preflight + baseline (STOP on failure) → P1–P5
- [x] Surface = an Executor clone; `just setup && just start-local` brings up PocketBase + SvelteKit; Node/pnpm + PocketBase on PATH.
- [x] This Spec merged to `main` (merge-first).
- [x] `RFC-LAB-000-008` A1 (D67) present on `main` (the design record).
- [x] Create `feat/is-admin-auth` off up-to-date `main`; clean tree; not `main`.
- [x] Baseline: `just validate-local` green (5 validators + `generate_pb_schema --check` + `pnpm check && build`).

## T1 — The `is_admin` field → R1
- [x] `pb_provision.py`: append `f_bool("is_admin")` to `users_spec.fields`.
- [x] `generate_pb_schema.py`: append the mirror `{"name":"is_admin","type":"bool",...}` to `users.fields`.

## T2 — Admin predicate + rule matrix → R2
- [x] `pb_provision.py`: add `RULE_ADMIN = '@request.auth.id != "" && @request.auth.is_admin = true'`.
- [x] `projects.createRule` → `RULE_ADMIN`. *(R2.2)*
- [x] `projects.updateRule` → `(OWNER_RULE) || (RULE_ADMIN)` with the existing owner rule preserved verbatim. *(R2.3)*
- [x] `projects.deleteRule` → `RULE_ADMIN`. *(R2.4)*
- [x] `settings.createRule`/`updateRule`/`deleteRule` → `RULE_ADMIN`; list/view stay `RULE_PUBLIC`. *(R2.5)*
- [x] `users.updateRule` → `RULE_ADMIN`; create stays `RULE_PUBLIC`, delete stays `None`. *(R2.6)*
- [x] Mirror ALL the above rule changes into `generate_pb_schema.py`.

## T3 — Regenerate the generated artifact → R3
- [x] `python3 scripts/generate_pb_schema.py` → regenerate `app/pocketbase/pb_schema.json`.
- [x] `python3 scripts/generate_pb_schema.py --check` passes.

## T4 — Bootstrap → R4
- [x] Document in `REPORT.md` the one-time superuser bootstrap (admin UI → `users` → toggle `is_admin`).
- [x] (Optional, local dev) flip `is_admin=true` on a designated `data/users.json` seed row; document if done.

## T5 — Rule-behavior tests → R6 (the DoD proof)
- [x] Add/extend a rule-test harness (`scripts/test-rbac-admin.*` or extend `test-settings.js`) covering the full R6 matrix (admin / owner-non-admin / plain-authed / anon), fail-closed.
- [x] Run against the local provisioned instance; all pass. Capture output for `REPORT.md`.

## T6 — Guardrails verification → R5
- [x] Confirm R5.1 (non-admin cannot PATCH own `is_admin`), R5.3 (owner path preserved) explicitly in the test run.

## T7 — Gates, lockstep, PR → R7
- [x] `just validate-local` green; scope floor held (only the rule sources + regenerated schema + optional seed/test script; NO `app/web/**` UI, NO new collection, NO memberships change).
- [x] Lockstep: `CHANGELOG.md` `[Unreleased]` → Added (BK-030/TSK-069); flip `SPRINT_TRACKER.md` TSK-069 at build.
- [x] Append `REPORT.md` (summary + bootstrap note + the R6 test results + the V1–V6 Human Verification Plan, left for `/verification-done`).
- [x] Open PR `feat/is-admin-auth → main`; self-validate vs EARS DoD; STOP-and-hold (never merge).

## Post-build (back on the Operator)
- `/verification-done` (Executor) records V1–V6 PASS → IN_REVIEW.
- `/review-pr <PR>` (Operator) — full scorecard incl. the R6 rule-test evidence per-criterion → human merge.
- Post-merge: TSK-069 → Done; `BK-031` (App Settings UI) + `BK-014` (CRUD) become buildable on the landed rules.
