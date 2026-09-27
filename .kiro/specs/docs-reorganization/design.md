# Docs Reorganization — Design

> Companion to `requirements.md`. Approach for grouping `docs/`, adding the docs-hub index + breadcrumb standard, renaming `work-environment` → `developer-guide`, and fixing referrers — with history preserved (`git mv`) and no broken links.

---

## 1. Approach: structure + navigation only (no content rewrites)

Treat this as **file relocation + navigation scaffolding**, not a content edit. Prose stays as-is except: (a) a breadcrumb line added at the top of each doc, (b) scope-clarifying headers on `developer-guide` (R2.2) and a staleness note on `cloud-dev-guide` (R5.3), and (c) the new `docs/README.md`. All moves use `git mv` so blame/history survive.

## 2. Target layout

```
docs/
├── README.md            # NEW — docs hub: index + the breadcrumb standard (copyable)
├── index.html           # UNTOUCHED (deployment concern; RFC-011)
├── guides/
│   ├── user-guide.md
│   ├── developer-guide.md        # renamed from work-environment.md
│   ├── project-owner-guide.md
│   ├── sprint-lifecycle.md
│   └── cloud-dev-guide.md        # + staleness note (OQ-1)
├── reference/
│   ├── project-protocol.md
│   ├── DESIGN.md
│   └── design-system-lab000.md
├── governance/
│   ├── DECISION-JOURNAL.md
│   └── ai-collaboration-model.md
├── rfc/                 # unchanged
└── templates/           # unchanged
```

**Path-depth note:** docs move from `docs/x.md` → `docs/<cat>/x.md`, so **intra-doc relative links change depth** (e.g. a link to `rfc/RFC-...` from a governance doc becomes `../rfc/RFC-...`). The link-fix pass (R6) must account for this, not just the renames.

## 3. Breadcrumb standard (R4)

Every `docs/**/*.md` (except `rfc/*`, `templates/*`, `index.html`) opens with:

```markdown
[🏠 Cetana Labs](../../README.md) / [📚 Docs](../README.md) / Guides / **Developer Guide**
```

- Category segment matches the folder (`Guides` / `Reference` / `Governance`).
- Relative depth is `../../` to repo root and `../` to `docs/README.md` (all docs are now one level deep under a category).
- Documented verbatim in `docs/README.md` under a "Nav standard" section, and referenced from `AGENTS.md` §1 (a new bullet: "docs follow the breadcrumb standard in `docs/README.md`").

## 4. `docs/README.md` index (R3)

Sections mirror the folders (Guides / Reference / Governance / RFCs / Templates), each a table of `doc | one-line purpose | link`. Opens with a breadcrumb back to root README and a short "how docs are organized + the nav standard" note. This is the **hub** the root README's doc-links header can point at (root README keeps its curated top links *and* gains a "📚 All docs → docs/README.md" entry).

## 5. Referrer updates (R5)

- **Root `README.md`:** doc-links header paths (→ `docs/guides/…` etc.); add "📚 All docs" → `docs/README.md`; **refresh the Repository-Structure tree** to real current contents (docs subfolders + the full `.kiro/skills/` list incl. `/spec-run`, `/plan-start`, `/plan-done`, `/review-pr`, `/verification-done`, `/sprint-start`, `env-doctor`, `validate-local`, `start/stop/status-local`).
- **`AGENTS.md`:** any `docs/work-environment.md` → `docs/guides/developer-guide.md`; add the breadcrumb-standard reference.
- **`docs/rfc/RFC-LAB-000-007-*`:** it names `work-environment.md` as a deliverable — update the reference to `developer-guide.md` (note: renamed) without rewriting the RFC's decision.
- **`templates/*/README.md`:** the runbook link `docs/work-environment.md` → `docs/guides/developer-guide.md`.
- **History (`journal.md`, delivered CHANGELOG entries, prior RFC prose):** leave historical mentions; only fix links that are *active navigation* (R5.2). Judgment call per occurrence.

## 6. Link-check (R6)

- **Baseline (T0/P6):** grep all `](...docs/...)` and `](...work-environment...)` intra-repo links; record targets.
- **After moves:** re-resolve each; a link is broken if its target path no longer exists. Fix until zero broken. A tiny throwaway shell/grep loop suffices (OQ-2); do not commit it.
- Focus areas: the root README doc-links header (most links), cross-doc links (depth change), AGENTS.md, templates.

## 7. Verification (feeds `tasks.md` + `/verification-done`)

Maps to V1–V8: grouping present; index resolves + links home; breadcrumbs correct on a sample; rename complete + referrers updated; **zero broken links** (the core bar); README tree accurate; `index.html`/`deploy-pages.yml` untouched; validators green.

## 8. Trade-offs

| Decision | Chosen | Rejected | Why |
| :--- | :--- | :--- | :--- |
| Move mechanism | `git mv` | delete+recreate | Preserves history/blame. |
| Nav standard home | `docs/README.md` + AGENTS ref | scatter in each doc | One copyable source of truth. |
| `index.html` | exclude | retire here | Coupled to the Vercel cutover (RFC-011); deleting now leaves no live dashboard mid-flight. |
| `cloud-dev-guide` | keep + staleness note | delete | Don't destroy content on a guess; human confirms supersession (OQ-1). |
| History mentions | leave as-is | rewrite | Journal/CHANGELOG are historical records (RFC-004 spirit). |
