# Docs Reorganization — Tasks

> Ordered plan for `/spec-run` (Build). Execute on **Kiro IDE**. Do NOT merge; open a PR, emit the Human Verification Plan, STOP in `IN_VERIFICATION`.

## Execution header (self-describing — read by `/spec-run`)

| Field | Value |
| :--- | :--- |
| **Spec id** | `docs-reorganization` |
| **Kickoff (IDE one-liner)** | `/spec-run docs-reorganization` |
| **Surface** | Kiro **IDE** (file moves + link-resolution checks) |
| **Branch to create** | `feat/docs-reorganization` (off up-to-date `main`, per `RFC-LAB-000-004`) |
| **Base for PR** | `main` |
| **Preflight** | Requirements §0 (P1–P6) + task **T0** — STOP on any ❌ |
| **Self-validation target** | `requirements.md` EARS R1–R7 |
| **Human Verification Plan** | `requirements.md` §4b (V1–V8) |
| **On completion** | Open PR via `gh api`, emit the Verification Plan, STOP → `/verification-done` → `/review-pr` (never merge) |
| **Executor role** | Delegated-agent / onboarded-dev |

---

- [ ] **T0 — Preflight (gate — STOP on any ❌)**
  - Surface=IDE (`/env-doctor`); clean tree; branch `feat/docs-reorganization` off fresh `main`; this Spec on `main` (merge-first).
  - Baseline green (P5): the three validators.
  - **Link inventory (P6):** grep + record all intra-repo links matching `docs/` and `work-environment` (targets) for the T6 diff.
  - _Refs: §0, design §6._

- [ ] **T1 — Create the folder taxonomy + move files (`git mv`, history preserved)**
  - Create `docs/guides/`, `docs/reference/`, `docs/governance/`.
  - `git mv`: guides ← user-guide, work-environment (→ renamed in T2), sprint-lifecycle, project-owner-guide, cloud-dev-guide; reference ← project-protocol, DESIGN, design-system-lab000; governance ← DECISION-JOURNAL, ai-collaboration-model.
  - **Do NOT touch `docs/index.html`** (excluded — R1.3).
  - _Refs: R1.1, R1.2, R1.3._

- [ ] **T2 — Rename `work-environment.md` → `docs/guides/developer-guide.md`**
  - `git mv`; add a scope-clarifying header (setup/commands/surfaces) distinguishing it from `project-owner-guide.md`.
  - _Refs: R2.1, R2.2._

- [ ] **T3 — Add breadcrumbs to every doc (R4.3)**
  - Prepend the standard breadcrumb (`[🏠 Cetana Labs](../../README.md) / [📚 Docs](../README.md) / <Category> / **This Doc**`) to each `docs/**/*.md` except `rfc/*`, `templates/*`, `index.html`. Verify relative depths.
  - _Refs: R4.1, R4.3, design §3._

- [ ] **T4 — Create `docs/README.md` (docs hub + nav standard)**
  - Index every doc by category (table: doc · purpose · link); breadcrumb back to root README; document the **breadcrumb standard** verbatim (the copyable convention). Ensure the 3 formerly-orphaned docs appear.
  - _Refs: R3.1, R3.2, R4.2, R5.3._

- [ ] **T5 — Update referrers + refresh the README tree**
  - Root `README.md` doc-links paths → new locations; add "📚 All docs" → `docs/README.md`; **refresh the Repository-Structure tree** to real current `docs/` + `.kiro/skills/` contents.
  - `AGENTS.md` (path + add breadcrumb-standard reference); `docs/rfc/RFC-LAB-000-007-*` (work-environment → developer-guide, note renamed); `templates/*/README.md` runbook link.
  - `cloud-dev-guide.md` staleness note (R5.3, pending human confirm in V-review).
  - Leave historical mentions in `journal.md` / delivered CHANGELOG / prior RFC prose (R5.2).
  - _Refs: R5.1, R5.2, R5.3, design §5._

- [ ] **T6 — Link-check (the core safety bar)**
  - Re-resolve every intra-repo `docs/*` / `developer-guide` link against the T0 baseline; fix all dangling links until **zero broken**. (Throwaway grep/script — do not commit.)
  - _Refs: R6.1, R6.2, design §6._

- [ ] **T7 — Validators green**
  - `validate_portfolio.py`, `generate_status_json.py --check`, `project_validate.py --allow-dirty`. If any hard-codes a moved `docs/` path, fix it.
  - _Refs: R7.1._

- [ ] **T8 — Commit, open PR, emit Human Verification Plan, STOP**
  - Branch `feat/docs-reorganization`; semantic commit referencing `TSK-052`.
  - Open PR into `main` via `gh api`; CI green; emit §4b plan (V1–V8); STOP in `IN_VERIFICATION`. **Never merge.**
  - _Refs: R-all, `RFC-LAB-000-009` §3.2._

- [ ] **T9 — After human verification passes: `/verification-done`**
  - Human runs V1–V8 (incl. confirming `cloud-dev-guide` supersession); fixes ride the same PR; on pass, `/verification-done` writes the Verification Log to this Spec's `REPORT.md` → `IN_REVIEW` → `/review-pr`.
  - _Refs: `RFC-LAB-000-009` §3.2._

---

### Governance lockstep reminder (Record, after merge)
Note the docs standardization in CHANGELOG (`TSK-052`); the breadcrumb standard in `docs/README.md` is now the convention new docs must follow (blueprint). `index.html` retirement remains queued under `RFC-LAB-000-011` (deployment).
