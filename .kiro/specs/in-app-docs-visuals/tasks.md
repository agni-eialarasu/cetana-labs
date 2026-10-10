# In-App Docs — Rich Visuals & Standard Navigation — Tasks

| Property | Value |
| :--- | :--- |
| **Spec ID** | `in-app-docs-visuals` · **Backlog** `BK-037` |
| **Branch** | `feat/in-app-docs-visuals` |
| **Executor** | Antigravity (Primary Executor) — SvelteKit/mermaid/iframe build; render-pipeline + sandbox care via the EARS DoD + human gate. |
| **Gate** | Full gate: `/spec-run` → PR → `/review-pr` scorecard → human merge. Merge-first: this Spec on `main` before build. |

> **Prerequisite (doc-class, must land first):** the three living-diagram artifacts are refreshed to current state and human-verified; their HTML is exported to `app/web/src/lib/docs/diagrams/*.html`. Do NOT start Task 3 until the refreshed HTML is committed. (Tracked as a separate doc-class task — see Task 0.)

---

## Task 0 — Prerequisite gate (verify, don't build)
- [x] Confirm `app/web/src/lib/docs/diagrams/working-model.html`, `runtime-infra.html`, `app-functionality.html` exist and are the **refreshed** (post-`#89`–`#97`) versions — no `/project-add`/`/project-edit`, OAuth not labelled "frontier", pillar-6 registry inversion reflected.
- [x] IF missing or stale → STOP and hand back to the Operator (the refresh is doc-class, not part of this gated build).

## Task 1 — Add mermaid, lazily
- [x] Add `mermaid` to `app/web/package.json` dependencies, pinned to an exact version; `pnpm install`.
- [x] Create `app/web/src/lib/docs/mermaid.ts`: a `renderMermaidIn(container, theme)` helper that dynamic-`import('mermaid')`, `initialize({ startOnLoad:false, securityLevel:'strict', theme })`, finds `code.language-mermaid`, renders each to SVG, sanitizes the SVG (DOMPurify SVG profile), replaces the `<pre>`; per-block `try/catch` leaves the original block on failure.
- **Verify:** unit-level — a sample mermaid string renders to an `<svg>`; a malformed string leaves the code block intact.

## Task 2 — Wire mermaid into /docs (client-only)
- [x] In `app/web/src/routes/docs/+page.svelte`, call `renderMermaidIn(docEl, resolvedTheme)` inside `onMount` after the doc HTML mounts; re-run on theme change (subscribe to the theme store / `matchMedia`).
- [x] Ensure it runs ONLY client-side (inside `onMount`), so SSR/prerender is untouched.
- **Verify:** `pnpm dev` → open `/docs?doc=project-owner` → the `flowchart TB` block renders as a diagram in both light and dark; `pnpm build` (adapter-static) succeeds.

## Task 3 — DiagramEmbed component (sandboxed iframe)
- [x] Create `app/web/src/lib/components/DiagramEmbed.svelte`: props `{ src:string, title:string }`; builds `srcdoc` = resolved-theme `:root` CSS-var `<style>` + `<base target="_parent">` + `src`; renders `<iframe sandbox="allow-scripts" srcdoc={…} title={title}>` with a responsive max-height + internal scroll. NO `allow-same-origin`, NO `allow-top-navigation`.
- [x] Re-inject `srcdoc` on theme change so the embed matches light/dark.
- **Verify:** the three diagrams render interactively (tabs + click-for-detail popovers work) inside the iframe; the sandboxed script cannot read `document.cookie` of the parent (confirm isolation).

## Task 4 — Surface the diagrams in docs nav
- [x] Register the diagrams in `registry.ts` (a `diagrams` pseudo-entry or three) and render them via `<DiagramEmbed>` on the `/docs` view (stacked, titled). Build-time `?raw` import of the committed HTML.
- [x] (R4.2 decision) IF adding `sprint-lifecycle` to `INCLUDED_DOCS`, add it with a one-line rationale comment; otherwise leave the allow-list consumer-scoped. Record the choice.
- **Verify:** the sidebar shows a Diagrams entry; all three render; the markdown mermaid in sprint-lifecycle (if added) renders via Task 2.

## Task 5 — Navigation standard
- [x] In `docs/+page.svelte`: replace the standalone "← Back to Dashboard" with a single breadcrumb `Dashboard › Docs › <active guide>` (links: `{base}/`, `{base}/docs`). Keep "View source on GitHub ↗" as the only external affordance.
- [x] Document the in-app nav standard in `docs/reference/design-system-lab000.md` (breadcrumb shape + "header owns home, breadcrumb owns parent").
- **Verify:** `/docs` shows one breadcrumb, no duplicate back-link; the standard subsection reads correctly and carries the nav footer.

## Task 6 — Lockstep + self-validate (DoD)
- [x] `just validate-local` green (portfolio validator + generator `--check` gates + SvelteKit typecheck/build).
- [x] `pnpm build` (adapter-static) succeeds with mermaid + embeds present (R5.3).
- [x] README registry block byte-identical (`generate_registry.py --check`).
- [x] CHANGELOG `[Unreleased]` entry; Decision Journal entry recording the iframe-vs-component decision (R5.2).
- [x] Open PR via `gh api`; write `REPORT.md` with the EARS R1–R5 self-check per criterion; STOP-and-hold (never merge).

---

## Definition of Done (EARS roll-up)
- **R1** mermaid renders in-app, themed, fail-soft, SSR-safe.
- **R2** three living diagrams embedded interactively via sandboxed iframe, from committed refreshed HTML, no runtime Kiro Crew dependency, no XSS regression.
- **R3** single `Dashboard › Docs › Guide` breadcrumb; standard documented.
- **R4** no data/schema/rule/auth change; allow-list stays consumer-scoped; registry byte-identical.
- **R5** `validate-local` + static build green; lockstep recorded.

---

> 🧭 **Navigation:** [⬆️ Top](#top) · [🏠 Repo](../../../README.md) · [📚 Docs Hub](../../../docs/README.md)
