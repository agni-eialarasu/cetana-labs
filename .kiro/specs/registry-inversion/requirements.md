# Registry Inversion — PocketBase as Source of Truth (RFC-016 Phase 3) — Requirements

| Property | Value |
| :--- | :--- |
| **Spec ID** | `registry-inversion` |
| **Feature** | Invert the project-metadata source of truth: PocketBase becomes the live master; `data/*.json` becomes a **generated export** (not a hand-authored master). Re-point the README registry generator at the export, flip the lockstep step to `just export-live-data`, re-point the registry CI pillar to assert export-matches-PB, and retire the two file-based metadata-lifecycle skills (`project-add`, `project-edit`). |
| **Backlog** | `BK-036` (`TSK-075`, SPRINT-13) |
| **Work class** | **Sprint deliverable** (changes the governance spine — generators, CI pillar, skills) → **FULL gate**. Not security-sensitive (no live-data migration; data already exists in PB post-BK-034), but high blast radius → careful scope floor. |
| **Depends on** | `BK-035` (`D71`, `docs/governance/registry-retirement-design.md` — the OQ answers), `BK-034` (`#89` — PB is now the authoritative identity store), `BK-014` (`export_pb_to_data.py` + reconciliation). |
| **RFCs** | `RFC-LAB-000-016` (Decision 2 / Phase 3), `RFC-LAB-000-002` (relational data — amended: `data/` is now downstream). |
| **Executor role** | **Kiro IDE** (escalated — touches the governance spine: generators + CI pillar + skill deletions + AGENTS.md; needs careful parity verification). Antigravity acceptable if the Director prefers, but the parity oracle (R6) is the risk. |
| **Source** | RFC-016 Phase 3, gated behind and unblocked by BK-035's OQ answers. |

---

## 1. Introduction

Today the data flow is `data/*.json ──seed──▶ PocketBase` — the hand-authored JSON masters are the source of truth and PB is seeded from them (`pb_import.py` / `just seed`). After BK-034, PB holds the single authoritative identity + the live portfolio (editable via the BK-014 admin CRUD). This Spec **flips the direction**:

```text
BEFORE:  data/*.json  ──seed──▶  PocketBase        (data/ is master)
AFTER:   PocketBase  ──export──▶  data/*.json      (PB is master, data/ is a committed snapshot)
```

The README registry generator (`generate_registry.py`) **already reads `data/portfolio.json` + `data/users.json`**, and `export_pb_to_data.py` **already writes those same files** — so the generator itself is largely unchanged. The inversion is about **who authors `data/`** (PB export, not hand-edits), **the lockstep step** (`just export-live-data` replaces hand-editing), **the CI pillar's assertion** (export-matches-PB), and **retiring the 2 skills** that encoded the hand-authored lifecycle.

## 2. Current-state facts (verified 2026-10-09 on `main`)
- `export_pb_to_data.py --apply` writes `data/portfolio.json` + `data/users.json` from live PB (the export path exists today, used post-CRUD for reconciliation — BK-014 R7.1).
- `generate_registry.py` loads `data/portfolio.json` + `data/users.json` and renders the README `<!-- BEGIN:registry -->` block.
- `generate_status_json.py` builds `data/status.json` from `STATUS.md` (unchanged by this Spec — status spine is out of scope per BK-035).
- `generate_status.py` (WhatsApp broadcast) reads `STATUS.md` only (unaffected).
- `project-add` / `project-edit` skills scaffold/edit `projects/LAB-XXX/` + hand-write `data/` + README — the lifecycle the app's `admin/projects` CRUD now owns.
- The 5-pillar validator's "registry lockstep" pillar asserts README-matches-`data/` with `data/` as hand-authored master.

## 3. Requirements (EARS acceptance criteria = Definition of Done)

### R1 — `data/` becomes a generated export, not a master
- **R1.1** `data/portfolio.json` + `data/users.json` SHALL be documented and treated as **generated artifacts** — regenerated via `just export-live-data`, never hand-edited. They SHALL be added to the "never hand-edit; regenerate" list in `.kiro/steering/structure.md` alongside the existing generated artifacts (README registry block, `pb_schema.json`, `status.json`).
- **R1.2** `data/*.json` SHALL remain **committed** (per OQ-2) so GitHub still renders the portfolio and the app's `src/lib/data.ts` offline/seed fallback still works.
- **R1.3** `data/memberships.json` (if present) SHALL be handled by the same export path OR explicitly documented as retained-as-is with a reason.

### R2 — README registry is generated from the export
- **R2.1** `generate_registry.py` SHALL render the README registry block from `data/*.json` as produced by `export_pb_to_data.py` (input unchanged; the only change is that the input is now export-sourced, not hand-authored). No regression in the rendered block for the current 6 projects.
- **R2.2** `generate_registry.py --check` SHALL stay green (README matches the committed export).

### R3 — Lockstep step is the export, not hand-editing
- **R3.1** The documented reconciliation/lockstep step for project-metadata changes SHALL be `just export-live-data` (export PB → `data/`) followed by `generate_registry.py` (export → README). AGENTS.md §5 (synchronized registry) + `.kiro/steering/structure.md` SHALL be updated to describe this flow.
- **R3.2** The divergence-banner reconciliation (D-CRUD-1, BK-014) SHALL remain the in-app signal that live PB and the committed export disagree — unchanged.

### R4 — Registry CI pillar re-pointed (OQ-1)
- **R4.1** The "registry lockstep" pillar in `validate_portfolio.py` / `project_validate.py` SHALL assert **the committed `data/` export is in sync with live PB** (export-freshness) rather than README-matches-hand-authored-`data/`. Where a live PB is not reachable in CI, the pillar SHALL assert the committed export is internally consistent with the README block (the existing `generate_registry --check`), and the export-freshness assertion runs where PB is reachable (local `just validate-local` / staging).
- **R4.2** `audit-project` SHALL be updated to describe the export as the registry source.
- **R4.3** All existing `--check` gates (`generate_registry --check`, `generate_status_json --check`, `generate_pb_schema --check`) SHALL remain green.

### R5 — Retire the 2 metadata-lifecycle skills
- **R5.1** `.kiro/skills/project-add/` and `.kiro/skills/project-edit/` SHALL be removed. Project creation/editing is now app-only (`admin/projects` CRUD) → `just export-live-data` → commit.
- **R5.2** `AGENTS.md` §3 (archetypes/templates) + §4 (skills suite) SHALL be updated: remove the two retired `/commands`, document app-side create/edit as the replacement, and note `project-update`/`project-status`/`project-validate`/`audit-*` are retained (they manage the executive/governance layer the app doesn't own).
- **R5.3** Any doc referencing `/project-add` or `/project-edit` (developer-guide, project-owner-guide, README) SHALL be updated to the app-side flow (lockstep).
- **R5.4** `projects/LAB-XXX/` directories SHALL be **kept** (existing STATUS.md/journal.md still managed by the retained skills). `templates/` SHALL be **kept** for now, with a one-line note that it is a Phase-3 follow-up candidate once app-side create is proven.

### R6 — Parity oracle (the correctness gate)
- **R6.1** After the inversion, running `just export-live-data` against the current live PB (6 projects, post-BK-034 identity) THEN `generate_registry.py` SHALL produce a README registry block **byte-identical** to the one on `main` today (no project dropped, renamed, or re-owned). This is the proof the inversion is lossless.
- **R6.2** `just validate-local` SHALL be fully green (5 pillars re-pointed + all generator `--check` gates).

### R7 — Scope floor
- **R7.1** This Spec SHALL NOT touch the status-reporting spine: `STATUS.md`, `journal.md`, `generate_status.py`, `generate_status_json.py`, `project-update`, `project-status`. (Out of scope per BK-035.)
- **R7.2** This Spec SHALL NOT change auth rules, `is_admin`, `OWNER_RULE`, or `RULE_ADMIN` (BK-034's territory).
- **R7.3** This Spec SHALL NOT delete `data/` or `projects/` or `templates/` directories (OQ-2/OQ-3 decided keep).

## 4. Out of scope / non-goals
- Deleting `templates/` (deferred follow-up).
- Any change to the WhatsApp broadcast or STATUS.md lifecycle.
- Org-level intake hub (Stage-D).
