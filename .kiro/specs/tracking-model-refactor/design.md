# Tracking-Model Refactor — Design

> Companion to `requirements.md`. Technical approach for implementing `RFC-LAB-000-010` — the physical split, the status remap, and the skill/validator/doc updates — with history preserved and validators green.

---

## 1. Approach: a pure move + reference-retarget (no behavior change)

The safest framing: this is a **content move + pointer update**, not a logic change. Sprint state literally relocates from `BACKLOG.md` → `SPRINT_TRACKER.md`; every reader is retargeted; the status labels are renamed to the state-machine vocabulary. The lifecycle commands behave identically — they just read/write a different file for sprint state.

## 2. File operations

- **`SPRINT_TRACKER.md`** (root — resolving OQ-1 toward root, since `project_validate.py` already falls back to it):
  - Move the **`## 🎯 Current Sprint`** block and the **`## 📦 Delivered Sprints Archive`** section out of `BACKLOG.md` verbatim.
  - Add a short header: title, a pointer back to `BACKLOG.md` (ideas) and `CHANGELOG.md` (shipped), `RFC-LAB-000-010` decision-of-record link, and the §4 status legend + Definition-of-Ready note.
- **`BACKLOG.md`** (trimmed): keep the intro + **`## 💡 Prioritized Backlog`** only; add a top pointer to `SPRINT_TRACKER.md`. Cite `RFC-LAB-000-010`.
- History: because whole sections move intact, a plain edit preserves the archive text; no `git mv` is strictly needed (both files already exist), but keep the delivered-archive entries byte-identical.

## 3. Status vocabulary remap (R3)

| Old (BACKLOG) | New (SPRINT_TRACKER) | State |
| :--- | :--- | :--- |
| `📋 Planned` | `📋 Backlog` (Spec not yet merged) or `✅ Ready` (Spec merged) | pre-funnel / `READY_TO_BUILD` |
| `🚧 In Progress` | `🔨 In Progress` | Build |
| *(none today)* | `🔍 In Verification` | `IN_VERIFICATION` |
| *(none today)* | `👀 In Review` | `IN_REVIEW` |
| `✅ Done` | `✅ Done` | `RECORDED` |

SPRINT-09 rows (OQ-2 leaning): `TSK-051` (this Spec, merged) → `🔨 In Progress`; `TSK-049`/`TSK-050`/`TSK-025`/`TSK-026` → `📋 Backlog` (their Specs not yet authored/merged).

## 4. Skill updates (R5 — text/target only, behavior identical)

- **`/sprint-start`**: change "Current Sprint block in `BACKLOG.md`" → "`SPRINT_TRACKER.md`"; Step 1 reads highest SPRINT id from `SPRINT_TRACKER.md`; TSK-id-uniqueness scan now spans **both** `SPRINT_TRACKER.md` and `BACKLOG.md`; lockstep note → `SPRINT_TRACKER.md` + `CHANGELOG.md`. Keep the "reads `BACKLOG.md` for `BK-` ideas" behavior.
- **`/sprint-done`**: Steps 1–2 inspect/archive the Current Sprint in `SPRINT_TRACKER.md`; the "initialize next sprint block" writes to `SPRINT_TRACKER.md`; CHANGELOG/STATUS/journal steps unchanged. Front-matter description updated.
- No change to `/plan-*`, `/spec-run`, `/review-pr` logic — they reference ids, not file structure (verify wording doesn't hard-say "BACKLOG").

## 5. Validator update (R7)

`scripts/project_validate.py` — the sprint-sync block (verified at lines ~166–178): it currently regex-matches `Delivered Sprints Archive|Delivered Tasks|### Sprint N` **in `backlog_file`**. After the split those markers live in `SPRINT_TRACKER.md`. Update so the check reads the **tracker** for those markers (it already resolves `tracker_file`), and treats `BACKLOG.md` as the idea bucket. Ensure the check still *passes for a real reason*, not by accident (e.g. don't let it fall through to the journal branch). Keep the `docs/sprints/` → root fallback intact.

## 6. Reference updates (R6)

- **`AGENTS.md`**: §1.1 "sprint backlogs (`BACKLOG.md`)" → "sprint tracker (`SPRINT_TRACKER.md`) + idea backlog (`BACKLOG.md`)"; §1.5 lockstep → tracker+changelog; §1.6 governance-docs fast-path list add `SPRINT_TRACKER.md`; §4 verb map lines for `/sprint-start`/`/sprint-done` → tracker.
- **`docs/sprint-lifecycle.md`**: verb-map + walkthrough references to where sprint state lives; add a one-liner on the three-tier funnel linking `RFC-LAB-000-010`.
- **`docs/work-environment.md`**: the Sprint row / any "BACKLOG" mention.
- **`README.md`**: doc-links already point at RFC-010; add `SPRINT_TRACKER.md` if the header lists tracking files.
- **`.github/pull_request_template.md`**: lockstep checklist item → `SPRINT_TRACKER.md` / `CHANGELOG.md`.

## 7. Verification (feeds `tasks.md` + `/verification-done`)

1. Diff-based id audit: extract all `SPRINT-`/`TSK-`/`BK-` ids from pre-refactor `BACKLOG.md`; confirm the union of post-refactor `SPRINT_TRACKER.md` + `BACKLOG.md` is a superset (R8.2).
2. Run the three validators (R7.2); confirm the sprint-sync check reads the tracker.
3. Grep the repo for lingering "Current Sprint" / "Delivered Sprints" strings pointing at `BACKLOG.md` in docs/skills.

## 8. Trade-offs

| Decision | Chosen | Rejected | Why |
| :--- | :--- | :--- | :--- |
| Tracker path | root `SPRINT_TRACKER.md` | `docs/sprints/` | Simpler; validator already falls back to root; can relocate later (OQ). |
| Delivered archive home | in `SPRINT_TRACKER.md` | separate history file | Keep it lean now (RFC-010 OQ-2). |
| Validator pillar for vocab/traceability | defer | add now | Out of scope; candidate follow-up (RFC-010 OQ-3). |
| History preservation | in-place section move | `git mv` gymnastics | Both files exist; byte-identical archive text preserves history in the diff. |
