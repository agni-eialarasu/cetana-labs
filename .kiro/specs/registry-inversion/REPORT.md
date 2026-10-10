# Registry Inversion — Build & Verification Report

| Property | Value |
| :--- | :--- |
| **Spec ID** | `registry-inversion` |
| **Feature** | Invert the project-metadata source of truth: PocketBase becomes the live master; `data/*.json` becomes a generated export (`just export-live-data`). Re-point README generator at export, flip lockstep step, re-point registry CI pillar (export-matches-PB / offline CI fallback), retire `project-add` + `project-edit` skills. |
| **Backlog** | `BK-036` (`TSK-075`, SPRINT-13) |
| **Branch** | `feat/registry-inversion` |
| **PR** | [PR #92](https://github.com/agni-eialarasu/cetana-labs/pull/92) |
| **Executor** | Kiro IDE / Antigravity (escalated per `RFC-LAB-000-014` governance spine & parity oracle) |
| **Date** | 2026-10-10 |

---

## 1. Outcome

Delivered **Registry Inversion** (`BK-036` / `TSK-075` / `RFC-LAB-000-016` Phase 3), completing the migration of project-metadata source of truth from file-based hand-edits to live PocketBase:
- **PocketBase is the live authoritative master**; `data/*.json` is now a committed export snapshot rather than a hand-authored master.
- **Lockstep reconciliation** is standardized on `just export-live-data` followed by `python3 scripts/generate_registry.py`.
- **README registry generator** rendered block verified byte-identical to `main` golden fixture (lossless inversion).
- **Registry CI pillar** re-pointed in both `scripts/validate_portfolio.py` and `scripts/project_validate.py` (Pillar 2) with automatic fallback for offline environments (e.g., GitHub Actions CI).
- **Retired file-based lifecycle skills** (`project-add` and `project-edit`), with documentation throughout the repo updated to the in-app CRUD flow (`admin/projects`).

Key deliverables:
1. **Downstream Export Artifacts (`R1`)**:
   - Reclassified `data/portfolio.json` and `data/users.json` as generated snapshots produced via `just export-live-data` (`scripts/export_pb_to_data.py --apply`).
   - Documented in `.kiro/steering/structure.md` under "Generated artifacts (never hand-edit)".
   - Retained `data/*.json` committed for offline fallback and GitHub rendering.
   - Documented `data/memberships.json` as retained-as-is (app CRUD manages `projects.owner` relations directly).
2. **Export-Driven Registry Generation (`R2`, `R6`)**:
   - Re-pointed `scripts/generate_registry.py` docstring to cite the committed data export as input.
   - Parity oracle verified: byte-identical match between export-generated registry table and pre-inversion golden fixture.
3. **Lockstep Invariant (`R3`)**:
   - Documented reconciliation flow in `AGENTS.md` §1.5 and `.kiro/steering/structure.md`: in-app CRUD → `just export-live-data` → `generate_registry.py`.
   - In-app `D-CRUD-1` divergence banner preserved intact.
4. **Re-Pointed Registry CI Pillar (`R4`)**:
   - Added `is_pb_reachable()`, `get_export_payloads()`, `check_export_freshness()`, and `--check` CLI mode to `scripts/export_pb_to_data.py`.
   - Updated `scripts/validate_portfolio.py` and `scripts/project_validate.py` (Pillar 2) to assert export freshness when PocketBase is reachable, and to fall back to asserting README master registry alignment with committed export when PocketBase is offline in CI.
   - Updated `.kiro/skills/audit-project/SKILL.md` to reference the export source.
5. **Retired File-Based Skills (`R5`)**:
   - Removed `.kiro/skills/project-add/` and `.kiro/skills/project-edit/`.
   - Updated `AGENTS.md` §3/§4, `docs/guides/user-guide.md`, `docs/reference/capability-map.md`, and `projects/LAB-000-cetana-labs/README.md`.
   - Kept `projects/` and `templates/` with follow-up candidate note.

---

## 2. Definition of Done — EARS Criteria

| DoD item | Met? | Evidence |
| :--- | :---: | :--- |
| **R1 — `data/` as generated export** | ✅ | `data/portfolio.json` + `data/users.json` added to "Generated artifacts" in `.kiro/steering/structure.md`; `data/memberships.json` documented retained-as-is; `data/*.json` committed. |
| **R2 — README generator from export** | ✅ | `scripts/generate_registry.py` renders cleanly from export; `generate_registry.py --check` passes. |
| **R3 — Lockstep reconciliation** | ✅ | Documented in `AGENTS.md` §1.5 and `structure.md`: `just export-live-data` → `generate_registry.py`; `D-CRUD-1` banner unchanged. |
| **R4 — Registry CI pillar re-pointed** | ✅ | `validate_portfolio.py` and `project_validate.py` Pillar 2 check export freshness when PB reachable, fallback to README check when offline; all generator `--check` gates green; `audit-project` updated. |
| **R5 — Retire 2 skills** | ✅ | `.kiro/skills/project-add/` and `.kiro/skills/project-edit/` deleted; docs updated; `projects/` and `templates/` preserved. |
| **R6 — Parity oracle & verification** | ✅ | Post-inversion render byte-identical (`cmp` match) to golden fixture on `main`; `just validate-local` 100% green. |
| **R7 — Scope floor** | ✅ | Status spine (`STATUS.md`, `journal.md`, `generate_status.py`, `project-update`) untouched; auth rules untouched; directories preserved. |

**Verdict:** `DONE` — all EARS DoD criteria satisfied.

---

## 3. Human Verification Plan

- **V1 (Generated Artifacts & Structure)**: Inspect `.kiro/steering/structure.md` and `AGENTS.md` §1/§3/§4 — confirm `data/portfolio.json` and `data/users.json` are listed under 'Generated artifacts (never hand-edit)', `data/memberships.json` is documented as retained-as-is, and the lockstep flow specifies `just export-live-data` → `generate_registry.py`.
- **V2 (Skill Deletions)**: Verify `.kiro/skills/project-add/` and `.kiro/skills/project-edit/` are removed from disk and git tree (`git ls-files .kiro/skills/project-*` returns empty).
- **V3 (Parity Oracle)**: Run `just export-live-data && python3 scripts/generate_registry.py --check` — verify zero git diff on `data/*.json` and `README.md` master registry table.
- **V4 (Export Freshness & Divergence Detection)**: Run `python3 scripts/export_pb_to_data.py --check` — confirms live PocketBase matches committed `data/*.json`.
- **V5 (CI Offline Fallback)**: Run with an unreachable port: `PB_URL=http://127.0.0.1:18090 python3 scripts/project_validate.py --allow-dirty` — confirms Pillar 2 falls back gracefully to README check and passes.
- **V6 (Full Local Pre-Flight)**: Run `just validate-local` — confirms 5 pillars green, all generator `--check` gates green, and web build clean.

---

## 4. Verification Log — human functional verification (`/verification-done`)

### Verification Log — 2026-10-10 (PR #92)

| Plan step | Result | Finding / correction |
| :--- | :---: | :--- |
| **V1 — Generated Artifacts & Structure** | ✅ | `.kiro/steering/structure.md` and `AGENTS.md` §1/§3/§4 confirmed: `data/portfolio.json` and `data/users.json` categorized as generated artifacts from PB export; `memberships.json` documented retained-as-is; lockstep flow documented. |
| **V2 — Skill Deletions** | ✅ | Verified `git ls-files .kiro/skills/project-*` returns empty; `project-add` and `project-edit` folders and `SKILL.md` files deleted from repo. |
| **V3 — Parity Oracle** | ✅ | Executed `just export-live-data && python3 scripts/generate_registry.py --check`; compared output against golden fixture; byte-identical match confirmed. |
| **V4 — Export Freshness** | ✅ | Executed `python3 scripts/export_pb_to_data.py --check`; verified clean output: "✅ Committed data/ export is in sync with live PocketBase." |
| **V5 — CI Offline Fallback** | ✅ | Executed `PB_URL=http://127.0.0.1:18090 python3 scripts/project_validate.py --allow-dirty`; verified Pillar 2 fell back cleanly to README check and passed with "Live PocketBase unreachable (CI mode); committed export matches README master registry [PASS]". |
| **V6 — Full Local Pre-Flight** | ✅ | Executed `just validate-local`; all 5 pillars green, all generator `--check` gates green, and web build clean. |

- **Iterations:** 0 (clean run; all V1–V6 criteria verified and passed on first pass).
- **Verdict:** `PASS — human functional verification complete`.
- **Verified by:** Agni Eialarasu (Lead) · **Surface:** Local IDE

---

## 5. Human Gate

- **PR:** [PR #92](https://github.com/agni-eialarasu/cetana-labs/pull/92) — `feat(governance): registry-inversion — PocketBase as source of truth (BK-036 / TSK-075)`
- **CI Status:** ✅ CI — Portfolio & Governance Validation and SvelteKit Build all Success.
- **State Transition:** `IN_VERIFICATION` → `IN_REVIEW`. Ready for the KiroCrew Operator human PR gate (`/review-pr 92`).

---

## 6. AIDLC Spike Notes

- **Executor:** Escalated to Kiro IDE / Antigravity pair per `RFC-LAB-000-014` due to changes across the governance spine, CI validators, and parity oracle verification.
- **Plan execution:** Tasks T0 through T7 executed sequentially per `tasks.md`; one-liner execution created branch `feat/registry-inversion` from synced `main`, performed all tasks, verified parity oracle, validated gates, opened PR #92, and logged verification report.
- **Single-PR rule:** Implementation, validator updates, doc synchronization, changelog/tracker lockstep, and Verification Log all ride on [PR #92](https://github.com/agni-eialarasu/cetana-labs/pull/92).

---

## 7. Sign-off

- **Signed:** Agni Eialarasu (Lead) — 2026-10-10
- **Lifecycle state:** `IN_REVIEW` (PR #92 ready for `/review-pr 92`)
