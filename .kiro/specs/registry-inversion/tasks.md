# Registry Inversion (RFC-016 Phase 3) — Tasks

> `/spec-run registry-inversion` executes these in order. Full gate (sprint deliverable).
> Parity oracle (T6) is the correctness proof; nothing merges without it green.

## T0 — Preflight
- [x] Sync `main`, cut `feat/registry-inversion` off clean `main`. Confirm BK-035's `D71` design doc is on `main` (this Spec cites it).
- [x] Capture the **golden fixture**: extract the current `<!-- BEGIN:registry -->`..`<!-- END:registry -->` span from `main`'s README into a scratch file for the T6 byte-diff.

## T1 — `data/` → generated artifact (R1)
- [x] Add `data/portfolio.json` + `data/users.json` to the "never hand-edit; regenerate via `just export-live-data`" list in `.kiro/steering/structure.md`.
- [x] Handle `data/memberships.json` per R1.3 (export path OR documented retained-as-is).
- [x] Keep `data/*.json` committed (R1.2) — do NOT delete.

## T2 — README generator from export (R2)
- [x] Confirm `generate_registry.py` renders correctly from export-produced `data/*.json` (input unchanged). Fix only if the export shape differs from the hand-authored shape.
- [x] `generate_registry.py --check` green.

## T3 — Lockstep step = export (R3)
- [x] Update AGENTS.md §5 + `.kiro/steering/structure.md`: the project-metadata lockstep step is `just export-live-data` → `generate_registry.py`.
- [x] Leave the D-CRUD-1 divergence banner unchanged.

## T4 — Re-point the registry CI pillar (R4)
- [x] In `validate_portfolio.py` / `project_validate.py`: the registry pillar asserts export-matches-PB where PB is reachable; else falls back to `generate_registry --check` (export-matches-README) for CI-no-PB. Implement the fallback explicitly (R4.1).
- [x] Update `audit-project` skill text (R4.2).
- [x] All three generator `--check` gates stay green (R4.3).

## T5 — Retire the 2 skills (R5)
- [x] Remove `.kiro/skills/project-add/` and `.kiro/skills/project-edit/`.
- [x] Update AGENTS.md §3/§4: drop the two `/commands`, document app-side create/edit as the replacement, note the 5 retained skills.
- [x] Grep + update every doc referencing `/project-add` or `/project-edit` (developer-guide, project-owner-guide, README) → app-side flow (R5.3).
- [x] Keep `projects/` + `templates/`; add the one-line `templates/` follow-up note (R5.4).

## T6 — Parity oracle (R6 — the gate)
- [x] Run `just export-live-data` against live PB (6 projects, post-BK-034) → `python3 scripts/generate_registry.py`.
- [x] Diff the rendered registry block against the T0 golden fixture — MUST be byte-identical (R6.1). If it differs, the export is lossy — STOP and report, do not merge.
- [x] `just validate-local` fully green (re-pointed pillars + all `--check` gates) (R6.2).

## T7 — Lockstep + PR
- [x] Register nothing new in `data/` by hand. Update CHANGELOG under TSK-075.
- [x] `just validate-local` green.
- [ ] Push `feat/registry-inversion`; open PR via `gh api` REST; self-validate against R1-R7; STOP-and-hold for `/review-pr`. **Never merge.**

## Scope floor (R7) — do NOT touch
- `STATUS.md`, `journal.md`, `generate_status.py`, `generate_status_json.py`, `project-update`, `project-status` (status spine).
- Auth rules, `is_admin`, `OWNER_RULE`, `RULE_ADMIN` (BK-034).
- Do NOT delete `data/`, `projects/`, or `templates/` directories.
