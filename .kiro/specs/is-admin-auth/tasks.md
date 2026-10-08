# `is_admin` Auth Tier — Tasks (`/spec-run is-admin-auth`)

> Executor = **Kiro IDE** (security-sensitive, budgeted — escalated from Antigravity default per `RFC-LAB-000-014`). Implements `RFC-LAB-000-008` A1. STOP-and-hold at the PR; never merge.

---

## T0 — Preflight + baseline (STOP on failure) → P1–P5
- [ ] Surface = an Executor clone; `just setup && just start-local` brings up PocketBase + SvelteKit; Node/pnpm + PocketBase on PATH.
- [ ] This Spec merged to `main` (merge-first).
- [ ] `RFC-LAB-000-008` A1 (D67) present on `main` (the design record).
- [ ] Create `feat/is-admin-auth` off up-to-date `main`; clean tree; not `main`.
- [ ] Baseline: `just validate-local` green (5 validators + `generate_pb_schema --check` + `pnpm check && build`).

## T1 — The `is_admin` field → R1
- [ ] `pb_provision.py`: append `f_bool("is_admin")` to `users_spec.fields`.
- [ ] `generate_pb_schema.py`: append the mirror `{"name":"is_admin","type":"bool",...}` to `users.fields`.

## T2 — Admin predicate + rule matrix → R2
- [ ] `pb_provision.py`: add `RULE_ADMIN = '@request.auth.id != "" && @request.auth.is_admin = true'`.
- [ ] `projects.createRule` → `RULE_ADMIN`. *(R2.2)*
- [ ] `projects.updateRule` → `(OWNER_RULE) || (RULE_ADMIN)` with the existing owner rule preserved verbatim. *(R2.3)*
- [ ] `projects.deleteRule` → `RULE_ADMIN`. *(R2.4)*
- [ ] `settings.createRule`/`updateRule`/`deleteRule` → `RULE_ADMIN`; list/view stay `RULE_PUBLIC`. *(R2.5)*
- [ ] `users.updateRule` → `RULE_ADMIN`; create stays `RULE_PUBLIC`, delete stays `None`. *(R2.6)*
- [ ] Mirror ALL the above rule changes into `generate_pb_schema.py`.

## T3 — Regenerate the generated artifact → R3
- [ ] `python3 scripts/generate_pb_schema.py` → regenerate `app/pocketbase/pb_schema.json`.
- [ ] `python3 scripts/generate_pb_schema.py --check` passes.

## T4 — Bootstrap → R4
- [ ] Document in `REPORT.md` the one-time superuser bootstrap (admin UI → `users` → toggle `is_admin`).
- [ ] (Optional, local dev) flip `is_admin=true` on a designated `data/users.json` seed row; document if done.

## T5 — Rule-behavior tests → R6 (the DoD proof)
- [ ] Add/extend a rule-test harness (`scripts/test-rbac-admin.*` or extend `test-settings.js`) covering the full R6 matrix (admin / owner-non-admin / plain-authed / anon), fail-closed.
- [ ] Run against the local provisioned instance; all pass. Capture output for `REPORT.md`.

## T6 — Guardrails verification → R5
- [ ] Confirm R5.1 (non-admin cannot PATCH own `is_admin`), R5.3 (owner path preserved) explicitly in the test run.

## T7 — Gates, lockstep, PR → R7
- [ ] `just validate-local` green; scope floor held (only the rule sources + regenerated schema + optional seed/test script; NO `app/web/**` UI, NO new collection, NO memberships change).
- [ ] Lockstep: `CHANGELOG.md` `[Unreleased]` → Added (BK-030/TSK-069); flip `SPRINT_TRACKER.md` TSK-069 at build.
- [ ] Append `REPORT.md` (summary + bootstrap note + the R6 test results + the V1–V6 Human Verification Plan, left for `/verification-done`).
- [ ] Open PR `feat/is-admin-auth → main`; self-validate vs EARS DoD; STOP-and-hold (never merge).

## Post-build (back on the Operator)
- `/verification-done` (Executor) records V1–V6 PASS → IN_REVIEW.
- `/review-pr <PR>` (Operator) — full scorecard incl. the R6 rule-test evidence per-criterion → human merge.
- Post-merge: TSK-069 → Done; `BK-031` (App Settings UI) + `BK-014` (CRUD) become buildable on the landed rules.
