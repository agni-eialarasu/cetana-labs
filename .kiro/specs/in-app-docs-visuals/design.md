# In-App Docs — Rich Visuals & Standard Navigation — Design

| Property | Value |
| :--- | :--- |
| **Spec ID** | `in-app-docs-visuals` |
| **Backlog** | `BK-037` |
| **Status** | Design — authored by the Operator 2026-10-10 for Kiro IDE `/spec-run` after merge-first. |

---

## 1. Design overview

Three cohesive changes to the `app/web` `/docs` surface, all client-render / build-time, no backend:

1. **Mermaid rendering** — a client-only post-render pass that finds `language-mermaid` code blocks and swaps them for mermaid-rendered SVG.
2. **Living-diagram embeds** — the three artifacts committed as static HTML assets, embedded via **sandboxed `<iframe srcdoc>`** so their inline `<script>` runs isolated (the markdown/`DOMPurify` path can't carry a `<script>`).
3. **Nav standard** — replace the ad-hoc "Back to Dashboard" with a single `Dashboard › Docs › <Guide>` breadcrumb; document the standard once.

## 2. R1 — Mermaid: client-only post-render

**Decision: client-side dynamic import of `mermaid`, run after the sanitized HTML mounts.** Rationale:
- `marked` has no mermaid support and `DOMPurify` would strip any `<svg>`/`<script>` mermaid emits at parse time — so rendering must happen **after** sanitize, on the mounted DOM, client-side (mermaid needs `document`).
- Keep the sanitizer honest: mermaid renders into a container we control, and we sanitize mermaid's SVG output too (`DOMPurify` SVG profile) before injecting — mermaid input is our own committed docs, but we defend-in-depth anyway.

**Mechanics (in `docs/+page.svelte`, `onMount`):**
```
1. marked renders ```mermaid → <pre><code class="language-mermaid">…source…</code></pre> (sanitized, source is text — safe).
2. onMount: dynamic import('mermaid'); mermaid.initialize({ startOnLoad:false, theme: <derived from app theme> }).
3. querySelectorAll('code.language-mermaid'); for each: mermaid.render(id, source) → svg; sanitize svg (DOMPurify SVG profile); replace the <pre> with the svg container.
4. try/catch per block → on failure leave the original <pre><code> (R1.3 fail-soft).
```
- **Theme (R1.2):** read the active theme (`theme.choice` / resolved) and pass mermaid `theme: 'dark' | 'default'`; re-run on theme change (subscribe to the same `matchMedia`/theme store the layout uses).
- **SSR/prerender (R1.4):** the import and render are inside `onMount` (never during SSR). `adapter-static` prerenders the page shell with the raw `<pre>` blocks; hydration upgrades them. Build stays green.
- **Dependency:** add `mermaid` to `app/web` dependencies (pinned exact version, Homebrew-managed pnpm). It is a sizable dep — load it **lazily** (`import()` only on `/docs`, only when a mermaid block exists) so the portfolio bundle is unaffected.

## 3. R2 — Living diagrams: sandboxed `<iframe srcdoc>`

**Decision: embed each diagram as committed static HTML, rendered in a `<iframe sandbox="allow-scripts" srcdoc="…">`.** Rationale (iframe vs. port-to-Svelte-component):

| Option | Verdict |
| :--- | :--- |
| **A. Sandboxed `<iframe srcdoc>` (chosen)** | The artifact HTML runs verbatim — zero re-authoring, its IIFE works untouched, and `sandbox="allow-scripts"` (NO `allow-same-origin`) gives a hard isolation boundary: the script can't reach the app's DOM, cookies, or storage (R2.5). Theme passed in by injecting the resolved CSS-variable values into the `srcdoc` `<style>`. One small `<DiagramEmbed>` Svelte wrapper handles sizing + theme injection. |
| B. Port each diagram to a Svelte component | Re-authors 3 complex interactive widgets (~400 lines of JS each) into Svelte — huge effort, and every future artifact refresh must be re-ported. Rejected: it breaks the "living diagram, one source" model. |
| C. Inject HTML + run script via the markdown path | Impossible — `DOMPurify` strips `<script>`; loosening the sanitizer to allow inline scripts in docs is an XSS footgun. Rejected on security. |

**Mechanics:**
- **Asset location:** committed refreshed HTML at `app/web/src/lib/docs/diagrams/{working-model,runtime-infra,app-functionality}.html` (build-time `?raw` import, same glob mechanism `registry.ts` already uses for markdown).
- **`<DiagramEmbed>` component:** props `{ src: rawHtml, title }`. Builds `srcdoc` = `<base target="_parent">` + a `<style>:root{ --text:…; --bg:…; … }` block (resolved from the app's computed theme values) + the artifact HTML. Renders `<iframe sandbox="allow-scripts" srcdoc={…} title={title}>`.
- **Sizing:** iframe height is content-driven — the embed posts its scrollHeight via `postMessage` on load (add a tiny height-reporter to the committed HTML, or use a fixed max-height with internal scroll as the simpler v1). **v1 = fixed responsive max-height with internal scroll** (no postMessage plumbing); auto-height is a follow-up if needed.
- **No `allow-same-origin`** → the sandboxed script cannot read parent cookies/PB session (R2.5). No `allow-top-navigation` → it can't hijack the tab.
- **Surfacing (R2.1):** add a "Diagrams" entry to the docs sidebar/nav (a dedicated `/docs?doc=diagrams` pseudo-doc, or three entries). The three embeds render stacked with their titles.

## 4. R3 — Navigation standard

- **Breadcrumb:** `app/web/src/routes/docs/+page.svelte` renders `Dashboard › Docs › <active guide title>` as the single orientation control; `Dashboard` → `{base}/`, `Docs` → `{base}/docs`. Remove the standalone "← Back to Dashboard" line (R3.1).
- **Global header/footer** (layout) already provide home/portfolio/theme/GitHub — unchanged. In-app docs rely on them (R3.2).
- **"View source on GitHub"** affordance retained, explicitly external (`↗`).
- **Document the standard (R3.3):** a short "In-app navigation standard" subsection in the design-system doc (`docs/reference/design-system-lab000.md`) — breadcrumb shape + "header owns home, breadcrumb owns parent."

## 5. Files touched (anticipated)
- `app/web/package.json` — add pinned `mermaid`.
- `app/web/src/lib/docs/mermaid.ts` (new) — lazy init + render-and-sanitize helper.
- `app/web/src/lib/docs/diagrams/*.html` (new, 3) — committed refreshed diagram HTML.
- `app/web/src/lib/components/DiagramEmbed.svelte` (new) — sandboxed iframe wrapper + theme injection.
- `app/web/src/lib/docs/registry.ts` — optional: register a `diagrams` pseudo-entry; possibly add `sprint-lifecycle` to the allow-list (R4.2, with rationale).
- `app/web/src/routes/docs/+page.svelte` — mermaid post-render pass; breadcrumb; render `<DiagramEmbed>`.
- `docs/reference/design-system-lab000.md` — nav standard subsection.
- `CHANGELOG.md`, Decision Journal — lockstep (R5.2).

## 6. Risks & mitigations
- **Mermaid bundle weight** → lazy `import()` scoped to `/docs` with a mermaid block present (§2).
- **Sanitizer vs mermaid SVG** → sanitize mermaid output with the SVG profile before injecting; fail-soft to the code block (R1.3).
- **iframe theme flashes on toggle** → re-inject `srcdoc` on theme change (cheap; three small iframes).
- **Static build breakage** → all dynamic work inside `onMount`; verify `pnpm build` in the DoD (R5.3).
- **Embedding stale content** → hard prerequisite: the three artifacts are refreshed + human-verified BEFORE their HTML is committed (R2.4 + prerequisite row in requirements).

---

> 🧭 **Navigation:** [⬆️ Top](#top) · [🏠 Repo](../../../README.md) · [📚 Docs Hub](../../../docs/README.md)
