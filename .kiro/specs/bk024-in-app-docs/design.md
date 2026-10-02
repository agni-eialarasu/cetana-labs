# In-App Docs View — Design

| Property | Value |
| :--- | :--- |
| **Spec ID** | `bk024-in-app-docs` |
| **Branch** | `feat/bk024-in-app-docs` (self-created by `/spec-run`) |
| **Builds on** | `app/web/` SvelteKit SPA (`RFC-LAB-000-005`); `app/web/scripts/copy-data.js` build-step precedent |

---

## 1. Approach

Add a `/docs` route to the SvelteKit SPA whose content is an **audience-filtered** set of repo docs, **imported at build time** and rendered as HTML. No runtime fetch, no PocketBase — git stays the single source of truth, mirroring the existing `copy-data.js` build-step philosophy (read canonical repo files at build, bake them into the bundle).

Pipeline, end to end:

```
docs/*.md (canonical)
   │  (build time — Vite / prebuild step)
   ├─ read via explicit ALLOW-LIST  ──► fail-loud if a listed path is missing (R5.1)
   ├─ strip leading breadcrumb line (R4.1)
   ├─ rewrite relative repo links → in-app section / absolute GitHub URL / plain text (R4.2/R4.3)
   ├─ render markdown → HTML (sanitized)
   └─ expose as a typed module the /docs route imports
   │
   ▼
src/routes/docs/+page.svelte  ──► doc picker (index) + rendered body, Tailwind-typography styled
   ▲
footer link ("Docs") on the global layout  ──► /docs (client-side nav)
```

### 1.1 Vite mechanism

Two viable mechanisms; the Spec leans on **`import.meta.glob` with `?raw`** plus a small transform module, falling back to a `prebuild` script only if the glob path (reaching **outside** `app/web/` into the repo `docs/`) proves awkward under Vite's `fs.allow` / Vercel's build context.

| Mechanism | How | Pros | Cons / risk |
| :--- | :--- | :--- | :--- |
| **`import.meta.glob('/…/docs/*.md', { query: '?raw', eager: true })`** | Vite inlines the raw markdown strings at build; a small `$lib/docs/registry.ts` applies the allow-list + strip + rewrite + render | Pure Vite, no extra script in `package.json`; HMR in dev; content provably in-bundle (R3.1/R3.2) | Globbing **outside** the project root needs `server.fs.allow` (dev) and a path that resolves under Vercel's `Root Directory = app/web` build context — must be verified (echoes the `BK-023` `copy-data` context lesson) |
| **`prebuild` transform script** (extends/sits beside `copy-data.js`) | A Node script reads the allow-listed `../../../docs/*.md`, strips+rewrites+(optionally pre-renders), writes typed artifacts into `src/lib/docs/generated/` | Exact precedent (`copy-data.js` already reaches `../../../data`); full control over missing-file **fail-loud**; no Vite `fs.allow` concern | Generated files (gitignore vs commit decision); a second step to keep in lockstep; less "live" in dev |

**Recommendation:** start with `import.meta.glob('…?raw')` for the read, and do strip/rewrite/render in a plain TS module at import time. **If** the cross-root path fights Vite `fs.allow` or Vercel's build context (a real risk given the `BK-023` `copy-data`/Vercel-context history), fall back to the `prebuild` script — it is the proven pattern in this repo. Either way the **render** choice below is independent of the read mechanism.

### 1.2 Markdown renderer — honest tradeoff (evaluate 1–2 options)

The included docs use GFM: tables, task lists, fenced code, emoji, and **mermaid** flowcharts (the Project Owner Guide has a `mermaid` block). Mermaid *rendering* is explicitly a nice-to-have, not required — R1.2 only needs it to be *readable text, not a crash*.

| Option | Size / shape | Pros | Cons |
| :--- | :--- | :--- | :--- |
| **`marked`** (+ `DOMPurify` sanitize, optional `marked-gfm-heading-id`) | ~35 KB min; tiny, synchronous, zero-config GFM | Smallest footprint; trivial build-time use (string→HTML); fast; easy to post-process the HTML for link-rewrite; well-matched to a static SPA | No plugin ecosystem as rich as remark; must pair with DOMPurify for safe HTML; mermaid needs a separate pass (fine — out of scope to render) |
| **`markdown-it`** (+ plugins) | ~45 KB + plugins | Mature, pluggable (anchors, footnotes, container blocks); good GFM | Heavier; plugin config overhead we don't need for 2–3 docs; same sanitize requirement |
| **`unified`/`remark`+`rehype`** | largest | Most powerful AST pipeline — link-rewrite + sanitize as proper rehype plugins; cleanest for complex transforms | Heaviest dep tree + build complexity; overkill for a 2–3-doc allow-list; slower to stand up |

**Recommendation: `marked` + `DOMPurify`.** Rationale (one line): for a fixed 2–3-doc allow-list rendered **at build time**, `marked` is the smallest, simplest string→HTML path that still covers the GFM the docs actually use, and DOMPurify gives the one safety guarantee we need — anything heavier (`markdown-it` plugins, a full `unified` pipeline) buys flexibility this scope will not use. The link-rewrite (R4) is a bounded post-process on the rendered HTML (or a `marked` renderer override for `link`/`image` tokens), which `marked` supports directly. Mermaid blocks render as fenced code (readable text) — acceptable per R1.2; upgrading to live mermaid is a future enhancement, not this Spec.

> Trust note: the input markdown is **our own repo content**, not user input, so XSS risk is low — but DOMPurify is kept as defense-in-depth and because the output is a consumer surface.

## 2. Components

| Component | Path (under `app/web/`) | Responsibility |
| :--- | :--- | :--- |
| **Allow-list + transform module** | `src/lib/docs/registry.ts` | The single explicit allow-list (R5.2); reads raw markdown (via `import.meta.glob` or generated artifacts), strips breadcrumb (R4.1), rewrites links (R4.2/R4.3), renders via `marked`+DOMPurify, exports a typed `{ slug, title, html }[]`. Carries the inline governance note (R6.2). |
| **`/docs` route** | `src/routes/docs/+page.svelte` | Doc picker (index of included docs) + renders the selected doc's `html` into a Tailwind-`prose` container; theme-aware (R1.1/R1.2/R1.4). |
| **(optional) prebuild step** | `scripts/build-docs.js` + `package.json` `prebuild` | Fallback read mechanism if `import.meta.glob` cross-root is awkward; fail-loud on a missing allow-listed path (R5.1). |
| **Footer link** | global layout (`src/routes/+layout.svelte`) or a `Footer.svelte` | A minimal consumer-labeled link → `/docs` (R2). Branded footer chrome deferred to `BK-013`. |
| **Lockstep edits** | `docs/governance/ai-collaboration-model.md`, `CHANGELOG.md`, `BACKLOG.md`, `SPRINT_TRACKER.md` | Governance consequence (R6.1) + lockstep (R7). |

## 3. Data flow (build time → render)

1. **Build** runs the read (glob `?raw` or prebuild script) over the **allow-list** only.
2. For each doc: **strip** the leading breadcrumb line → **rewrite** links → **render** to sanitized HTML.
3. A **missing** allow-listed path → **fail the build, naming the path** (R5.1 preferred policy; the final policy is stated here and is fail-loud).
4. The route imports the typed doc array; **no network, no PocketBase** at runtime (R3.2).
5. Reader hits `/docs` (SPA fallback already handles client routing) → picks a doc → sees rendered HTML.

### 3.1 The allow-list (R1.3 / R5.2)

```ts
// src/lib/docs/registry.ts  — the ONE place the in-app doc set is defined.
// NOTE: a doc listed here becomes a CONSUMER SURFACE — editing it changes what
// leads/leadership see in the product. Review such edits with UX impact in mind.
// (See docs/governance/ai-collaboration-model.md — in-app docs are consumer surfaces.)
export const INCLUDED_DOCS = [
  { slug: 'user-guide',       src: 'guides/user-guide.md',                    title: 'User Guide' },
  { slug: 'project-owner',    src: 'guides/project-owner-guide.md',           title: 'Project Owner Guide' },
  // OPTIONAL third ("how we build this"): enable deliberately.
  // { slug: 'how-we-build',  src: 'governance/ai-collaboration-model.md',    title: 'How We Build This' },
] as const;
```

### 3.2 Link / breadcrumb rewrite (R4)

- **Breadcrumb:** drop the first line if it matches the breadcrumb shape (`^\[🏠 … \]\(.*README\.md\).*/\s*\*\*.*\*\*\s*$`) — robust to the exact category label.
- **Links:** a `marked` `link` renderer override (or a rehype-style post-process):
  - target is an **included** doc → rewrite to the in-app section (`/docs#<slug>` or the picker).
  - target is an **excluded / out-of-app** repo file (`../../README.md`, `DECISION-JOURNAL.md`, an RFC) → rewrite to its **absolute GitHub URL** (`https://github.com/agni-eialarasu/cetana-labs/blob/main/<path>`), opening out of the app.
  - unresolvable / anchor-only → render as plain text, never a dead in-app `href`.

## 4. Out of scope (restated for the executor)
- Branded footer/about **chrome** = `BK-013`. This Spec: link target + one minimal link only.
- **No DB:** no PocketBase collection, no runtime fetch (R3.2).
- **No excluded docs** rendered (RFCs, Decision Journal, developer-guide, sprint-lifecycle, project-protocol, DESIGN, capability-map) (R1.3).
- No in-app editing; no docs search/index.
- Live **mermaid** rendering (readable fenced text is sufficient this Spec).

## 5. Risks & mitigations
| Risk | Mitigation |
| :--- | :--- |
| Vite `import.meta.glob` can't reach `../../docs` cross-root under Vercel's `Root Directory=app/web` (the `BK-023` build-context class of bug) | Fall back to the proven `prebuild` script pattern (`copy-data.js` already reaches `../../../data`); verify on a real Vercel build, not just local. |
| A silently-dropped consumer doc (missing/renamed source) ships an empty section | **Fail-loud** build policy naming the path (R5.1); allow-list is explicit (R5.2). |
| Rewritten/stripped markdown renders a dead in-app link | R4 rewrite rules + Human Verification step 3 (hover every former relative link). |
| An unreviewed doc edit silently changes the product | Governance note (R6.1) + inline allow-list pointer (R6.2) make the consumer-surface consequence visible at the point of change. |
| XSS via rendered HTML | DOMPurify sanitize; input is our own repo content (low risk) but sanitized as defense-in-depth. |
| Scope creep into branding | §4: footer chrome is `BK-013`; this Spec adds only the link + target. |
