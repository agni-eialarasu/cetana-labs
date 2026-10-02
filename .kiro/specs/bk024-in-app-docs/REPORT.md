# In-App Docs View — Build Report

| Property | Value |
| :--- | :--- |
| **Spec ID** | `bk024-in-app-docs` |
| **Feature** | Surface consumer-facing documentation inside the deployed Sleek UI (`/docs`) |
| **Branch** | `feat/bk024-in-app-docs` |
| **Executor** | Antigravity (Executor trial) |
| **Date** | 2026-10-02 |

---

## 1. What was built

Surface consumer-facing documentation directly inside the deployed Sleek UI (`/docs`) so leads and leadership can read how the platform and status protocol work without navigating to GitHub.

Key deliverables:
- **Build-Time Markdown Import & Transform (`app/web/src/lib/docs/registry.ts`)**: Inlines raw markdown at build time via Vite's `import.meta.glob` (`?raw`, eager), strips leading breadcrumb lines, rewrites relative repo links (internal included docs to in-app routes, excluded/out-of-app files to canonical GitHub URLs), renders sanitized HTML via pinned `marked` and `DOMPurify`, and exports a typed `DOCS` array. Carries the inline governance consequence notice.
- **Fail-Loud Build Guard (`app/web/scripts/check-docs.js` & `package.json`)**: Prebuild and predev script that asserts all allow-listed docs exist in `docs/` before build starts, failing loudly with exit code 1 and naming the missing path if a doc is renamed or deleted.
- **In-App Help/About Route (`app/web/src/routes/docs/+page.svelte` & `+page.ts`)**: Two-column layout featuring a sticky doc picker sidebar, top navigation with back-to-dashboard breadcrumbs, ThemeToggle, and a styled markdown article container mapped to Sleek UI `--np-*` design tokens for full light/dark theme awareness.
- **Minimal Footer Link (`app/web/src/routes/+layout.svelte`)**: Added a consumer-facing "Docs" link to the global layout footer using client-side routing (`base + '/docs'`), while strictly avoiding branded chrome (deferred to `BK-013`).
- **Governance Consequence (`docs/governance/ai-collaboration-model.md §6`)**: Recorded that allow-listed in-app docs are consumer surfaces whose modifications carry direct UX/product consequences.
- **Lockstep Updates**: Recorded `BK-024` under `CHANGELOG.md` `[Unreleased]`, updated `BACKLOG.md` status to `In PR (Spec bk024-in-app-docs)`, and added `TSK-065` to `SPRINT_TRACKER.md`.

Files touched:
- `app/web/package.json` — pinned `marked` and `dompurify` dependencies; added `check-docs.js` to `predev`/`prebuild`.
- `app/web/pnpm-lock.yaml` — updated dependency lockfile.
- `app/web/vite.config.ts` — configured `server.fs.allow: ['../..']` to permit cross-root repo markdown imports in Vite.
- `app/web/scripts/check-docs.js` — fail-loud build guard for allow-listed doc paths.
- `app/web/src/lib/docs/registry.ts` — allow-list, breadcrumb stripping, link rewriting, marked/DOMPurify rendering.
- `app/web/src/routes/docs/+page.svelte` — `/docs` page component with doc picker and theme-aware styled typography.
- `app/web/src/routes/docs/+page.ts` — static prerender configuration for docs route.
- `app/web/src/routes/+layout.svelte` — sticky layout with minimal footer "Docs" link.
- `docs/governance/ai-collaboration-model.md` — recorded that in-app docs are consumer surfaces (§6).
- `CHANGELOG.md` — added `[Unreleased]` entry for `BK-024`.
- `BACKLOG.md` — updated `BK-024` row to `In PR (Spec bk024-in-app-docs)`.
- `SPRINT_TRACKER.md` — registered `TSK-065` for `BK-024`.

---

## 2. EARS DoD walk (R1–R8)

| Criterion | Verdict | Evidence |
| :--- | :---: | :--- |
| **R1.1** `/docs` route renders included docs as HTML | ✅ | `app/web/src/routes/docs/+page.svelte` renders User Guide and Project Owner Guide content from `DOCS`. |
| **R1.2** Navigable index / doc picker renders selected doc | ✅ | Sidebar nav in `+page.svelte` dynamically switches active doc via `?doc=<slug>` and renders selected doc. Mermaid code blocks render as readable preformatted text. |
| **R1.3** Only allow-listed docs rendered; no excluded internal docs surfaced | ✅ | `INCLUDED_DOCS` in `registry.ts` contains only `user-guide` and `project-owner`. Any cross-links to external docs are rewritten to GitHub absolute URLs. |
| **R1.4** Styled consistently with Sleek UI, readable light/dark | ✅ | `.doc-content` scoped CSS styles headings, tables, blockquotes, code, and lists using `--np-*` tokens (`--np-text`, `--np-bg-subtle`, `--np-border`, `--np-accent`). |
| **R2.1** Footer / nav link navigates to `/docs` | ✅ | `src/routes/+layout.svelte` includes `<a href="{base}/docs">Docs</a>` in the footer. |
| **R2.2** Client-side navigation from any route | ✅ | Uses SvelteKit SPA navigation (`base + '/docs'`) without page reloads. |
| **R3.1** Markdown imported/rendered at build time | ✅ | Raw markdown read via Vite's `import.meta.glob` (`?raw`, `eager: true`) and baked into the build bundle. |
| **R3.2** No runtime fetch, no PocketBase | ✅ | Pure static bundle data; `DOCS` requires zero network calls or PocketBase collections. |
| **R3.3** Reads from canonical `docs/` tree | ✅ | Directly imports from `../../../../../docs/**/*.md` — zero duplicated files. |
| **R4.1** Leading breadcrumb line stripped | ✅ | `stripBreadcrumb()` matches `^\[🏠.*?\]\(.*?README\.md\).*?\/\s*\*\*.*?\*\*\s*$` and removes the top navigation line and trailing whitespace. |
| **R4.2** Relative repo links rewritten / no dead in-app hrefs | ✅ | `rewriteRelativeRepoLink()` rewrites `../../README.md`, `../../BACKLOG.md`, `../../CHANGELOG.md` to absolute GitHub URLs. Unresolvable links render as plain text. |
| **R4.3** Included docs resolve in-app; excluded docs resolve to canonical GitHub | ✅ | Included docs map to `?doc=<slug>`; excluded repo files resolve to `https://github.com/agni-eialarasu/cetana-labs/blob/main/<path>`. |
| **R5.1** Missing allow-listed doc fails build loudly naming the path | ✅ | `scripts/check-docs.js` in `prebuild` plus `loadAndRenderDocs()` throw a loud fatal error with the exact path if an allow-listed doc is missing. |
| **R5.2** Single, explicit, reviewable allow-list | ✅ | `export const INCLUDED_DOCS` in `src/lib/docs/registry.ts` is the single source of truth. |
| **R6.1** Recorded in `ai-collaboration-model.md §6` | ✅ | Added "In-app docs are consumer surfaces (`BK-024`)" bullet to `ai-collaboration-model.md §6`. |
| **R6.2** Inline governance comment on allow-list | ✅ | Added banner comment directly above `INCLUDED_DOCS` in `src/lib/docs/registry.ts`. |
| **R7.1** `CHANGELOG.md` `[Unreleased]` entry + tracker rows | ✅ | `CHANGELOG.md`, `BACKLOG.md` (`BK-024`), and `SPRINT_TRACKER.md` (`TSK-065`) updated in lockstep. |
| **R7.2** Lockstep part of build task set | ✅ | Lockstep edits committed on the feature branch with the implementation. |
| **R8.1** Scope confined to `app/web/` + docs | ✅ | Git diff shows zero changes to `data/`, PocketBase schemas, migrations, or auth flows. |
| **R8.2** Build and check green | ✅ | `pnpm --dir app/web check` (0 errors, 0 warnings) and `pnpm --dir app/web build` pass cleanly. |

---

## 3. Verification run (agent self-check)

- **SvelteKit type check (`pnpm --dir app/web check`):** 0 errors, 0 warnings.
- **SvelteKit static build (`pnpm --dir app/web build`):** Succeeded in 2.27s; adapter-static generated site cleanly with fallback `index.html`.
- **Prettier code style check (`pnpm --dir app/web exec prettier --check ...`):** Clean on all touched files.
- **Python Governance Engine (5/5 pillars):**
  - Scraper Budget: 33/35 max lines [PASS]
  - Registry Synchronization: CHANGELOG, BACKLOG, SPRINT_TRACKER in lockstep [PASS]
  - Git Hygiene: Working tree clean on `feat/bk024-in-app-docs` [PASS]
  - AST Layer Isolation: 42/42 architectural boundaries passed [PASS]
  - Automated Test Suite: 6/6 portfolio integrity checks passed [PASS]
- **Fail-Loud Verification Test (R5.1):**
  - Temporarily altered allow-list to point to `guides/nonexistent-doc-for-test.md`.
  - Re-ran build: `check-docs.js` immediately exited 1 with `[check-docs] FATAL: Missing allow-listed doc: "guides/nonexistent-doc-for-test.md" (expected at .../docs/guides/nonexistent-doc-for-test.md)`.
  - Restored allow-list; build succeeded.
- **Render Output Inspection:**
  - `user-guide` rendered length: 9,901 chars. Leading breadcrumb `[🏠 Cetana Labs](../../README.md)...` stripped cleanly; first rendered element is `<h1>Cetana Labs — User Guide & Playbook</h1>`.
  - `project-owner` rendered length: 11,255 chars. First rendered element is `<h1>Project Lead & Developer Guide — Automated Status Protocol</h1>`.
  - Links verified: `../../BACKLOG.md` and `../../CHANGELOG.md` rewritten to `https://github.com/agni-eialarasu/cetana-labs/blob/main/...`. Zero dead relative paths.

---

## 4. AIDLC spike notes (`RFC-LAB-000-009` §7)

- **Vite Cross-Root Globbing (`import.meta.glob`):** Resolving `../../../../../docs/**/*.md` from `app/web/src/lib/docs/registry.ts` works seamlessly in Vite when `server.fs.allow: ['../..']` is configured in `vite.config.ts`.
- **Defense-in-Depth Fail-Loud Architecture:** Rather than relying solely on bundle evaluation, a lightweight Node prebuild validator (`app/web/scripts/check-docs.js`) runs before Vite build starts. This ensures that any missing or renamed allow-listed doc halts the pipeline immediately with a deterministic non-zero exit code.
- **Markdown & DOMPurify Integration:** Pinned `marked@18.0.14` and `dompurify@3.4.16`. In Node without DOM (during SSR/build), `marked` produces clean HTML from trusted repo sources; in the browser, `DOMPurify.sanitize` sanitizes with attribute preservation (`target`, `rel`).
- **Typography Tokens:** The Sleek UI does not use `@tailwindcss/typography`; all prose styling is cleanly mapped to the canonical Nexus Pulse `--np-*` tokens in `src/routes/docs/+page.svelte`, ensuring 100% theme fidelity in dark and light modes.

---

## 5. Verification Log

### Human Verification Plan (Agent-Executable Steps)

| Step | Test Description | Result | Evidence / Finding |
| :---: | :--- | :---: | :--- |
| **V1** | Build & load | ✅ | `pnpm check` and `pnpm build` pass with 0 errors. Static adapter writes build bundle. |
| **V2** | Footer link | ✅ | Minimal consumer-labeled link added to `src/routes/+layout.svelte` pointing to `{base}/docs`. |
| **V3** | User Guide renders clean | ✅ | Breadcrumb line stripped; links to `BACKLOG.md` and `CHANGELOG.md` rewritten to canonical GitHub URLs. |
| **V4** | Project Owner Guide renders | ✅ | Renders correctly; mermaid code fence rendered as readable preformatted text. |
| **V5** | Audience filter holds | ✅ | Only allow-listed docs exist in `DOCS`; all external docs link to GitHub. |
| **V6** | Missing-doc fail-loud behavior | ✅ | Tested missing doc rename: build failed loud with exit code 1 naming the exact path. |
| **V7** | Theme | ✅ | Verified readable across both dark and light modes with high contrast; typography tokens cleanly render headings, code fences, tables, and blockquotes. |
| **V8** | Governance note present | ✅ | `ai-collaboration-model.md §6` and `registry.ts` both carry consumer-surface consequence notes. |

---

### Human Sign-Off (recorded via /verification-done)

- **Iterations:** 0 (clean on first pass; 1 rebase on upstream main)
- **Verdict:** PASS — human functional verification complete.
- **Verified by:** Agni Eialarasu (`arasu@agnitechnologies.com`) · **Surface:** Antigravity IDE / Kiro IDE
- **Date:** 2026-10-02

