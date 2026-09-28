# POC Log — ⟨POC name⟩

> The **single, collapsed artifact** for a Mini-AIDLC POC. It folds the five standard artifacts (tracker · backlog · changelog · decision-journal · spec-pointer) into one file, **sectioned along the graduation seams** so `/graduate` can lift each section into its standard-model counterpart cleanly (see `MIGRATION.md`).
>
> **Keep it terse.** POC speed. At graduation this file is *derived from*, then **frozen as historical reference** — not deleted.

| Field | Value |
| :--- | :--- |
| **POC** | ⟨name⟩ |
| **Stack** | ⟨language/framework/datastore, or TBD⟩ |
| **Started** | YYYY-MM-DD |
| **Status** | 🔬 POC in progress · (→ ✅ Approved → run `/graduate`) |
| **Model** | Mini AIDLC (`aidlc-mini/KICKSTART.md`) |

---

## § Decisions  → seeds `DECISION-JOURNAL.md` (carry forward at graduation)
> Real decisions only — the formative bets. Format: what triggered it · options · the choice + why. Terse is fine.

- **D1 — ⟨decision title⟩** *(YYYY-MM-DD)* — Trigger: ⟨…⟩ · Options: ⟨A/B⟩ · **Chose ⟨…⟩ because ⟨…⟩.**

## § Now  → seeds `SPRINT_TRACKER.md` (migrate active work)
> What's being built right now. Simple states: `todo` / `doing` / `done`.

| Item | State | Note |
| :--- | :---: | :--- |
| ⟨first thing⟩ | todo | |

## § Ideas  → seeds `BACKLOG.md` (migrate the idea bucket)
> Things for later — not committed. The shelf.

- ⟨idea⟩

## § Shipped  → seeds `CHANGELOG.md` (carry forward as history)
> What works, newest first — with the **eyeball-verify** note (the human-gate record at POC speed).

- *(YYYY-MM-DD)* ⟨what shipped⟩ — verified: ⟨how you eyeballed it⟩ · approved by ⟨name⟩.

## § Spec  → grows into full Kiro Spec(s) at graduation
> Pointer to the current `POC-SPEC.md` (if a unit of work warranted one). Small asks can skip this.

- Current: `POC-SPEC.md` — ⟨feature⟩ · or "none (inline asks)".

---

<!-- At graduation, /graduate appends a freeze header here:
## ⛔ FROZEN — graduated to standard on YYYY-MM-DD
This POC-LOG is now a historical reference. Active work → SPRINT_TRACKER.md; ideas → BACKLOG.md;
shipped history → CHANGELOG.md; decisions → DECISION-JOURNAL.md; specs → .kiro/specs/. Do not edit above.
-->
