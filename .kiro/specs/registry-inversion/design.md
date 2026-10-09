# Registry Inversion (RFC-016 Phase 3) — Design

> Cites `docs/governance/registry-retirement-design.md` (BK-035 / D71) for the OQ answers.

## 1. The core insight (why this is smaller than it looks)

`generate_registry.py` already reads `data/portfolio.json` + `data/users.json`, and
`export_pb_to_data.py --apply` already writes those same files. The inversion is therefore
**mostly a documentation + lockstep + skill-retirement change**, not a generator rewrite:

- The generator's **input is unchanged** — it keeps reading `data/*.json`.
- What changes is **who produces `data/*.json`**: PB export (`just export-live-data`), not hand-edits.
- The CI pillar's **assertion** flips to export-freshness (OQ-1).
- Two skills are **removed** (OQ-3); the app's CRUD is the replacement.

## 2. Data-flow before/after

```text
BEFORE (data/ is master):
  human edits data/*.json ──▶ generate_registry ──▶ README registry block
  data/*.json ──pb_import/just seed──▶ PocketBase

AFTER (PB is master):
  admin/projects CRUD ──▶ PocketBase (live)
  PocketBase ──just export-live-data──▶ data/*.json (committed snapshot)
  data/*.json ──generate_registry──▶ README registry block
```

## 3. Changes by surface

| Surface | Change |
| :--- | :--- |
| `.kiro/steering/structure.md` | Add `data/portfolio.json` + `data/users.json` to the "generated — never hand-edit" list; document the export-sourced flow. |
| `AGENTS.md` §1/§3/§4 | `data/` is now downstream; remove `/project-add` + `/project-edit` from the skills suite; document app-side create/edit; note retained skills. |
| `scripts/validate_portfolio.py` / `project_validate.py` | Registry pillar asserts export-matches-PB where PB reachable; else export-matches-README (`generate_registry --check`). |
| `.kiro/skills/project-add/`, `.kiro/skills/project-edit/` | **Removed.** |
| `.kiro/skills/audit-project/SKILL.md` | Describe export as the registry source. |
| docs (developer-guide, project-owner-guide, README) | Replace `/project-add`/`/project-edit` references with the app-side flow. |

## 4. The parity oracle (R6 — the correctness gate)

The single proof the inversion is lossless: on the current live PB (6 projects, post-BK-034),
`just export-live-data && python3 scripts/generate_registry.py` must yield a README registry
block **byte-identical** to `main` today. If it differs, the export is lossy and the Spec is not done.

Capture the pre-inversion README registry block (`git show main:README.md`, extract the
`BEGIN:registry`..`END:registry` span) as the golden fixture; diff the post-inversion render against it.

## 5. Risk & reversibility

- **Not a live-data migration** — PB already holds the data (BK-034); this changes authorship/flow, not records. Lower risk than Phase 1.
- **Reversible by revert** — pure governance-spine + skills + docs; a revert PR restores the hand-authored-master model. No DB state to roll back.
- **Blast radius** — the CI pillar re-point (R4) is the delicate part: a mis-scoped pillar either goes green when it shouldn't (export silently stale) or red in CI where PB is unreachable. R4.1 handles the CI-no-PB case explicitly.

## 6. Executor note
Kiro IDE (escalated) — the parity oracle + CI-pillar re-point need careful verification against a
live PB and a CI run. The skill deletions + doc edits are mechanical, but the pillar logic is the
one place a subtle regression hides.
