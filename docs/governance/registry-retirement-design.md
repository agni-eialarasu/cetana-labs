[🏠 Cetana Labs](../../README.md) / [📚 Docs](../README.md) / Governance / **Registry-Retirement Design (BK-035 · RFC-016 Phase 2)**

# Registry-Retirement Design — Cetana Labs

> **BK-035 · RFC-016 Phase 2.** Answers the gating open questions (OQ-1..OQ-4) that
> [`RFC-LAB-000-016`](../rfc/RFC-LAB-000-016-github-identity-and-registry-retirement.md)
> left open before any deletion. This is the design record Phase 3 (BK-036, the registry
> inversion) must cite — **no master/skill is deleted until the answers here are agreed.**

---

## 1. The one decisive finding

The web app's CRUD (BK-014: `admin/projects`, `admin/developers`) owns project **metadata** —
the `portfolio.json` / `users.json` fields (owner, repo, archetype, slug). It does **NOT** own
the executive layer: per-project `STATUS.md` + `journal.md`, and the daily WhatsApp broadcast,
which `scripts/generate_status.py` sources **exclusively from `STATUS.md`** (verified: 11 refs,
zero to `data/`).

**Consequence:** the registry retirement is only about project-**metadata** source-of-truth. The
status-reporting spine is untouched. That splits the `project-*` skillset cleanly and materially
de-risks the whole phase.

---

## 2. OQ-3 — the skill retirement list (the per-skill call)

| Skill | Operates on | App replaces it? | Verdict |
| :--- | :--- | :---: | :--- |
| `project-add` | Scaffolds `projects/LAB-XXX/`, writes `data/portfolio.json` + README registry | ✅ Yes — `admin/projects` create | **RETIRE** |
| `project-edit` | Edits metadata across registry + `data/` | ✅ Yes — `admin/projects` edit | **RETIRE** |
| `project-update` | Writes `STATUS.md` + `journal.md` | ❌ No app editor for these | **KEEP** |
| `project-status` | Reads `STATUS.md` → WhatsApp broadcast | ❌ Broadcast is `STATUS.md`-sourced | **KEEP** |
| `project-validate` | 5-pillar pre-flight gate (`project_validate.py`) | ❌ Guards structure the app doesn't enforce | **KEEP** (re-point registry pillar, OQ-1) |
| `audit-doc` | Single-doc hygiene | ❌ Registry-agnostic | **KEEP** |
| `audit-project` | Whole-project governance sweep | ❌ The governance sweep | **KEEP** (re-point at PB export) |

**Net: retire 2 of 7.** `project-add` and `project-edit` — the pure metadata lifecycle the app now
owns. The other five operate on the executive/governance layer the app deliberately doesn't touch.

### `projects/` and `templates/`
- **`projects/LAB-XXX/`** directories are **kept** — existing ones retain their `STATUS.md`/`journal.md`,
  which the kept skills (`project-update`, `project-status`) still manage. Phase 3 stops *creating new*
  disk dirs on project add (that becomes an app action); it does not delete existing ones.
- **`templates/`** — the `mini-app`/`research`/`verification`/`data-collection`/`aidlc-mini` archetype
  scaffolds are tied to `project-add`'s disk-scaffolding. **Keep for now**, re-evaluate once app-side
  create is proven (they are cheap and harmless at rest; premature deletion risks losing the archetype
  reference). Flagged as a Phase-3 follow-up, not a Phase-3 deletion.

---

## 3. OQ-1 — Registry CI pillar → **re-point, do not retire**

The "registry lockstep" pillar changes its assertion:

- **Today:** `README.md` registry block matches hand-authored `data/*.json`.
- **After:** committed `data/*.json` **export** matches live PocketBase (i.e. `just export-live-data`
  was run and the export is not stale).

Still a real gate — it now guards *export freshness* instead of *hand-edit consistency*. This keeps the
at-rest GitHub registry view that D68 reframed (README registry as a reconciled snapshot).

---

## 4. OQ-2 — `data/` as export vs gone → **keep as a generated export**

Confirms the RFC's lean. `just export-live-data` already writes `data/*.json`; the app's
`src/lib/data.ts` offline/seed fallback depends on it; GitHub keeps rendering the portfolio. Deleting
`data/` entirely loses the at-rest view for ~zero gain.

**Decision:** keep `data/`, flip its role **master → generated artifact**. Add `data/*.json` to the
"never hand-edit; regenerate via `just export-live-data`" list in `.kiro/steering/structure.md`
alongside the existing generated artifacts.

---

## 5. OQ-4 — PB uniqueness / migration safety → **already satisfied (BK-034, #89)**

The handle-unique index + upsert-by-handle hook + the atomic owner-re-point-before-delete migration
shipped in [PR #89]. The project `owner` relation is re-pointed to the survivor before the orphan is
deleted, so no project is ever left ownerless, and the no-escalation post-condition holds.

---

## 6. The hard dependency Phase 3 must own — the data-flow inversion

Retiring `project-add` assumes PocketBase is the **live master** and `data/` is downstream. Today the
flow is inverted. Phase 3's core work is flipping its direction:

```text
TODAY:   data/*.json  ──seed──▶  PocketBase        (data/ is master, PB seeded from it)
PHASE 3: PocketBase  ──export──▶  data/*.json      (PB is master, data/ is a committed snapshot)
```

This flip implies, in the Phase-3 (BK-036) Spec:
1. New projects are **created in the app**, not scaffolded on disk.
2. `just export-live-data` becomes the **lockstep step** in place of `generate_registry.py` running
   from hand-authored masters (`generate_registry` re-points to render the README block *from the export*).
3. The `project-validate` + `audit-project` registry pillars assert **export-matches-PB**, per §3.
4. The two retired skills (`project-add`, `project-edit`) are removed; AGENTS.md §3/§4 and the docs that
   reference them are updated in the same PR (lockstep).

**Unchanged throughout:** the executive broadcast spine — `STATUS.md`, `journal.md`, `project-status`,
`project-update`. The registry retirement does not touch status reporting.

---

## 7. Summary — what BK-035 decides

| OQ | Decision |
| :--- | :--- |
| **OQ-1** | Re-point the registry CI pillar at the PB export (export-matches-PB); do not retire it. |
| **OQ-2** | Keep `data/*.json` as a generated export; flip role master → downstream artifact. |
| **OQ-3** | Retire **2 skills** (`project-add`, `project-edit`); keep the other 5. Keep `projects/` + `templates/`; re-evaluate `templates/` as a Phase-3 follow-up. |
| **OQ-4** | Already satisfied by BK-034 (#89). |
| **Core** | Phase 3 (BK-036) = **invert the data flow** (PB master, `data/` export) — the one consequential change; status spine untouched. |

**Phase 3 is now unblocked to be specced** — its Spec cites this doc for the OQ answers.
