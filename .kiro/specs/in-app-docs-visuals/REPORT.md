# In-App Docs — Rich Visuals & Standard Navigation — Build & Verification Report

| Property | Value |
| :--- | :--- |
| **Spec ID** | `in-app-docs-visuals` |
| **Feature** | Client-side lazy themed mermaid rendering, sandboxed living-diagram embeds (`working-model`, `runtime-infra`, `app-functionality`), and `Dashboard › Docs › Guide` breadcrumb navigation standard. |
| **Backlog** | `BK-037` (`TSK-076`, SPRINT-13) |
| **Branch** | `feat/in-app-docs-visuals` |
| **PR** | Pending open via `gh api` |
| **Executor** | Google Antigravity (Primary Executor per `RFC-LAB-000-014` / `#99`) |
| **Date** | 2026-10-10 |

---

## 1. Outcome & Deliverables

Delivered **In-App Docs Rich Visuals & Standard Navigation** (`BK-037` / `TSK-076`), upgrading the `/docs` surface from raw markdown code dumps to interactive, rich architectural visuals:

1. **Client-Side Lazy Mermaid Rendering (`R1`)**:
   - Added pinned `mermaid@12.1.0` to `app/web/package.json`.
   - Created `app/web/src/lib/docs/mermaid.ts`: helper dynamic-imports mermaid lazily only when mermaid blocks are present, initializes strictly (`securityLevel: 'strict'`), renders SVG, sanitizes with `DOMPurify` SVG profile (`USE_PROFILES: { svg: true, svgFilters: true }`), and replaces `<pre>` blocks.
   - Fail-soft per-block `try/catch`: invalid syntax logs a warning, cleans up temporary nodes, and preserves the raw code block intact (R1.3).
   - Theme-aware: dynamically adjusts theme between `'dark'` and `'default'`, re-rendering on light/dark toggle.
   - SSR-safe: runs strictly client-side inside Svelte `$effect`, leaving adapter-static prerender green.

2. **Living Diagrams Sandboxed Embeds (`R2`)**:
   - Created `app/web/src/lib/components/DiagramEmbed.svelte` to embed the three refreshed living-diagram assets (`working-model.html`, `runtime-infra.html`, `app-functionality.html`) committed under `app/web/src/lib/docs/diagrams/`.
   - Built-in sandboxed iframe (`sandbox="allow-scripts"` only; strictly NO `allow-same-origin`, NO `allow-top-navigation`), eliminating XSS and session hijacking vectors.
   - Theme variables (`--text`, `--bg`, `--accent`, `--border`, `--card`, etc.) dynamically computed from active theme and injected into `:root` in `srcdoc`.
   - Pure build-time committed assets imported with `?raw` — zero runtime Kiro Crew dependencies.

3. **In-App Navigation Standard (`R3`)**:
   - Replaced the standalone "← Back to Dashboard" and bullet list with a single semantic breadcrumb:
     `Dashboard › Docs › <Active Guide Title>`
     where `Dashboard` links to `{base}/`, `Docs` links to `{base}/docs`, and `<Active Guide Title>` denotes the current view.
   - Retained "View source on GitHub ↗" as an explicitly external affordance.
   - Documented the standard in `docs/reference/design-system-lab000.md` §6 ("header owns home, breadcrumb owns parent").

4. **Docs Allow-List & Living Architecture Registry (`R4`)**:
   - Added `sprint-lifecycle` to `INCLUDED_DOCS` in `app/web/src/lib/docs/registry.ts` with a consumer rationale comment (R4.2).
   - Exported `LIVING_DIAGRAMS` and `DIAGRAMS_DOC` from `registry.ts`.
   - Exposed a dedicated "Architecture" section in the docs sidebar linking to `/docs?doc=diagrams`, rendering the three living diagrams stacked and titled.

5. **Governance Lockstep (`R5`)**:
   - `just validate-local` 100% green (portfolio validator, PB schema check, status json check, 5-pillar project validator, SvelteKit typecheck/build).
   - `pnpm build` (adapter-static) succeeded with mermaid and diagram embeds present.
   - `generate_registry.py --check` confirmed README master registry is byte-identical.
   - Recorded `CHANGELOG.md` `[Unreleased]` entry and Decision Journal Entry 029 (`D74`).

---

## 2. Definition of Done — EARS Criteria Self-Check

| DoD Criterion | Description | Met? | Evidence |
| :--- | :--- | :---: | :--- |
| **R1.1** | Mermaid block renders as SVG in `/docs` (not raw text) | ✅ | `renderMermaidIn` locates `code.language-mermaid` and replaces `<pre>` with sanitized SVG wrapper (`.mermaid-block`). |
| **R1.2** | Mermaid follows app theme (light/dark) | ✅ | `theme.resolved` triggers re-render pass passing `theme: 'dark' \| 'default'`. |
| **R1.3** | Fail-soft fallback on parse error | ✅ | Per-block `try/catch` leaves original `<pre><code>` block unchanged on parse failure. |
| **R1.4** | Client-side only / SSR-safe | ✅ | Dynamic import and render run only inside client-side `$effect` (`if (!browser) return`). `adapter-static` build succeeds. |
| **R2.1** | Three living diagrams embedded in `/docs` nav | ✅ | Reachable at `/docs?doc=diagrams` and sidebar Architecture navigation; renders Working Model, Runtime Infra, App Functionality. |
| **R2.2** | Diagrams preserve interactivity via isolated iframe | ✅ | Sandboxed iframe allows inline scripts (`sandbox="allow-scripts"`), preserving tabs and popovers without passing through `DOMPurify` markdown pipeline. |
| **R2.3** | Embed inherits active app theme | ✅ | Active CSS theme tokens dynamically injected into `:root` in `srcdoc`. |
| **R2.4** | Refreshed HTML committed as build-time asset | ✅ | Built-in assets committed at `app/web/src/lib/docs/diagrams/*.html` imported via `?raw`. Zero Kiro Crew runtime API calls. |
| **R2.5** | Sandbox boundary prevents XSS/clickjacking | ✅ | Strictly `sandbox="allow-scripts"` (NO `allow-same-origin`, NO `allow-top-navigation`). Child frame cannot access parent cookies, tokens, or DOM. |
| **R3.1** | Single `Dashboard › Docs › Guide` breadcrumb | ✅ | Rendered in header of `/docs`; redundant "← Back to Dashboard" removed. |
| **R3.2** | Header owns home, breadcrumb owns parent | ✅ | Global header handles home/portfolio navigation; breadcrumbs handle doc hierarchy; external GitHub links marked with `↗`. |
| **R3.3** | Navigation standard documented | ✅ | Section 6 added to `docs/reference/design-system-lab000.md`. |
| **R4.1** | Scope floor: no data/schema/rule/auth change | ✅ | Zero changes to `data/**`, `app/pocketbase/**`, rules, or schemas. |
| **R4.2** | Consumer-scoped `INCLUDED_DOCS` allow-list | ✅ | Only `sprint-lifecycle` added with explicit one-line rationale comment. |
| **R4.3** | Status spine & registry untouched | ✅ | `STATUS.md`, `journal.md`, `generate_registry.py --check` byte-identical. |
| **R5.1** | `just validate-local` green | ✅ | 100% green: portfolio validator, PB schema check, status json check, 5-pillar gate, typecheck, static build. |
| **R5.2** | CHANGELOG & Decision Journal lockstep | ✅ | CHANGELOG `[Unreleased]` entry and Decision Journal Entry 029 (D74) recorded. |
| **R5.3** | SvelteKit static build (`adapter-static`) passes | ✅ | `node ./node_modules/vite/bin/vite.js build` completed cleanly, writing static bundle to `build/`. |

**Verdict:** `DONE` — all 17 EARS criteria satisfied.

---

## 3. Human Verification Plan

- **V1 (In-App Mermaid Rendering)**:
  - Run `just start-local` and navigate to `/docs?doc=project-owner`.
  - Confirm the mermaid flowchart (`flowchart TB`, 5-pillar pre-flight gate) renders as an interactive SVG diagram rather than raw text.
  - Navigate to `/docs?doc=sprint-lifecycle` and confirm the 4 mermaid flowcharts render cleanly.
- **V2 (Theme Switching on Mermaid)**:
  - Toggle the theme between Dark and Light using the footer theme toggle.
  - Confirm mermaid diagrams adjust contrast and background colors cleanly to match the active theme.
- **V3 (Living Diagrams Embed & Interactivity)**:
  - In the docs sidebar under **Architecture**, click **Living Diagrams** (`/docs?doc=diagrams`).
  - Confirm all three living diagrams render stacked with titles and descriptions.
  - Click on tabs (e.g. "Cloud runtime", "Deploy plane" in Runtime Infrastructure; "Execution Lanes" in Working Model). Confirm tabs switch and detail popovers display cleanly.
- **V4 (Iframe Security Boundary)**:
  - Inspect the living diagram iframe elements in browser DevTools.
  - Verify `sandbox="allow-scripts"` is present and neither `allow-same-origin` nor `allow-top-navigation` is set.
- **V5 (Navigation Breadcrumb Standard)**:
  - Observe the top of `/docs`. Confirm the breadcrumb displays `Dashboard › Docs › <Current Title>`.
  - Confirm "Dashboard" navigates to `{base}/` and "Docs" navigates to `{base}/docs`.
  - Confirm there is no secondary "← Back to Dashboard" button.
- **V6 (Local Pre-Flight Gate)**:
  - Run `just validate-local`. Confirm all python validators, generator checks, svelte-check, and static build pass green with zero errors.

---

> 🧭 **Navigation:** [⬆️ Top](#top) · [🏠 Repo](../../../README.md) · [📚 Docs Hub](../../../docs/README.md)
