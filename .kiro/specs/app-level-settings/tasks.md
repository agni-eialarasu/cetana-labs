# App-Level Settings — Tasks (`/spec-run` build plan)

## Execution header
- **Kickoff:** `/spec-run app-level-settings`
- **Surface:** Kiro IDE (+ local stack `/start-local` for verification)
- **Branch to create:** `feat/app-level-settings` (off up-to-date `main`)
- **EARS target (DoD):** `requirements.md` §3 R1–R6; verify against §4b V1–V7
- **Merge-first:** this Spec + `RFC-LAB-000-013` must be on `main` before kickoff (satisfied by `/plan-done`)

> Ordered plan for `/spec-run` (Build) on **Kiro IDE**. Executes `tasks.md`, self-validates against the `requirements.md` EARS DoD, opens a PR into `main`, emits the Human Verification Plan (§4b), and **STOPs in `IN_VERIFICATION`**. **Never merges.**

- [ ] **T0 — Preflight (gate — STOP on any ❌)**
  - Confirm P1–P6: on `feat/app-level-settings` off up-to-date `main`, clean tree; toolchain + data→schema + seed flow present; baseline green (5 validators + `pnpm check && build`).

- [ ] **T1 — `settings` collection + schema (R1)**
  - Add `settings` to `generate_pb_schema.py → collections()` (`key` unique/required, `value`, `type` select, `group` optional) + the unique index. Add `data/settings.json` + `data/settings.schema.json`. `generate_pb_schema.py --check` green (R1.2).

- [ ] **T2 — API rules / RBAC (R2)**
  - Public `list`/`view`; superuser-only `create`/`update`/`delete`. (Verified via V4 positive/negative controls.)

- [ ] **T3 — Seed (R4.1, R4.3)**
  - Seed `app_name` (repo name) + `app_description` (repo description) via the `data/` + `pb_provision.py`/`pb_import.py` flow. Reserve/document logo keys — do NOT seed them.

- [ ] **T4 — Typed accessor façade (R3)**
  - Add the SPA `settings` accessor (mirror `data.ts`): eager load, typed getters (`appName()`, `appDescription()`) with hardcoded defaults, `type`-driven casting, absent-key ⇒ default.

- [ ] **T5 — Read-wiring (R4.2)**
  - Wire the app header/title (and page metadata where applicable) to `settings.appName()` — one real consumer, proving the public read-path end-to-end (V2).

- [ ] **T6 — Docs (R5)**
  - Document the settings pattern in `developer-guide.md` (+ `data/README.md` if that's the collection-docs home): the collection, the accessor, "how to add a setting", RBAC posture, reserved logo keys → BK-013.

- [ ] **T7 — Governance lockstep (Pillar 2)**
  - `CHANGELOG.md` `[Unreleased]` entry for `TSK-057`/`BK-012`. Confirm `SPRINT_TRACKER.md` `TSK-057` coherent (→ `👀 In Review` on the PR; `✅ Done` in the post-merge tidy).

- [ ] **T8 — Quality gates + no-regression (R6)**
  - 5 validators (incl. `generate_pb_schema.py --check`), `make validate-local`, `pnpm --dir app/web check && build`. No secret in settings; existing collections unaffected.

- [ ] **T9 — Commit, open PR, emit Human Verification Plan, STOP**
  - Open PR into `main` via `gh api`; CI green; emit §4b (V1–V7; V2/V4 headline). STOP in `IN_VERIFICATION`. **Never merge.**

- [ ] **T10 — After human verification passes: `/verification-done`**
  - Human runs V1–V7 on the local stack (esp. V2 public read renders app_name, V3 default fallback, V4 superuser-only write). Fixes ride the same PR. On pass → `/verification-done` → `IN_REVIEW` → `/review-pr`.
