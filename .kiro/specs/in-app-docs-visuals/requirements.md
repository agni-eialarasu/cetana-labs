# In-App Docs — Rich Visuals & Standard Navigation — Requirements

| Property | Value |
| :--- | :--- |
| **Spec ID** | `in-app-docs-visuals` |
| **Feature** | Make the in-app `/docs` view (BK-024) render rich visuals correctly and give docs a navigation standard consistent with the rest of the app. Three parts: (1) **render mermaid** diagrams (today they show as raw ` ```flowchart ` code blocks); (2) **embed the three living-diagram visuals** (Working Model · Runtime Infrastructure · App Functionality) as interactive panels; (3) a **standard in-app docs navigation** (breadcrumb from Dashboard → Docs → Guide; no redundant back-link) matching the global header/footer. |
| **Backlog** | `BK-037` (`TSK-0NN`, SPRINT-13) |
| **Work class** | **Sprint deliverable** (product UI a user exercises — the consumer-facing `/docs` surface) → **FULL gate**: Spec → `/spec-run` → `/review-pr` scorecard → human merge. |
| **Depends on** | `BK-024` (in-app docs view + `registry.ts` allow-list — live), `BK-027` (global header/footer + center-nav slot — merged `#71`), `BK-032` (density/nav pass — `ui-density-nav-pass`). |
| **Prerequisite (doc-class, lands first)** | Refresh the three living-diagram artifacts to current state (they predate `#89`–`#97`: show retired `/project-add` + `/project-edit`, label OAuth/RBAC as "frontier"). The refreshed, verified HTML is the embed source — a stale embed would ship drift into the product. |
| **RFCs** | `RFC-LAB-000-005` (Sleek UI design system), `RFC-LAB-000-007` / `ai-collaboration-model.md` (in-app docs are **consumer surfaces**). |
| **Executor role** | **Kiro IDE** (escalation per `RFC-LAB-000-014`) — this touches the markdown render pipeline, client-side mermaid loading, iframe sandboxing/XSS boundary, and the sanitizer; subtle security/SSR regressions could hide here, so it is NOT routine Antigravity work. |
| **Source** | Operator session 2026-10-10 — user screenshot showed a raw `flowchart TB` block rendering as text in the Project Owner Guide; user asked to validate the Cetana-tagged artifacts and bring them into the app docs. |

---

## 1. Introduction

The in-app `/docs` route (BK-024) renders allow-listed consumer docs via `marked` + `DOMPurify`. Two gaps hurt DX:

1. **Mermaid is dead on arrival.** The Project Owner Guide (and others) contain ` ```mermaid ` / ` ```flowchart ` fenced blocks. `marked` renders them as a plain `<pre><code>` block, so a lead viewing the guide in-app sees raw diagram source, not a diagram (confirmed in the user's 2026-10-10 screenshot). On GitHub the same block renders natively — so the in-app surface is strictly worse than the repo.
2. **The three living diagrams aren't in the product.** We maintain three rich, interactive HTML visuals (Working Model · Runtime Infrastructure · App Functionality) as Kiro Crew artifacts. They are the best explanation of how the lab works, but a lead can only see them if the Operator pastes them into chat — they're absent from the app a lead actually uses.

A third, smaller gap: the `/docs` page carries its own "← Back to Dashboard" link that duplicates the global header's home link, and the markdown nav footer (repo-file links) is stripped/irrelevant in-app — so docs navigation diverges from the rest of the app.

## 2. Current-state facts (verified 2026-10-10 on `main`)

- **`app/web/src/lib/docs/registry.ts`** — `INCLUDED_DOCS` allow-list = `user-guide`, `project-owner` (a 3rd, `how-we-build`, is commented out). Renders with `marked` (`gfm: true`) + a custom link renderer, then `DOMPurify.sanitize(html, { ADD_ATTR: ['target','rel'] })`. **`DOMPurify` strips `<script>`**, so artifact HTML with an inline `<script>` CANNOT go through this path as-is.
- **`stripBreadcrumb()`** removes the leading breadcrumb line from each doc before render (so the markdown breadcrumb never shows in-app).
- **No mermaid dependency** anywhere in `app/web` (`marked` only). Mermaid fences render as `<pre><code class="language-mermaid">`.
- **`app/web/src/routes/docs/+page.svelte`** — renders a sidebar (INCLUDED GUIDES) + the doc HTML; line 25 has its own `<span>Back to Dashboard</span>`.
- **`app/web/src/routes/+layout.svelte`** — global sticky header (branding · Portfolio · admin tabs · auth) + footer (theme · Docs · GitHub). This is the app's nav standard.
- **The three artifacts** (Kiro Crew, tag `cetana-labs`): `fd26dcf5ca990145` Working Model (v13), `cetana-labs-runtime-infrastructure` (v6), `cetana-labs-app-functionality` (v5). Each is self-contained `<style>` + markup + an IIFE `<script>`, themed via CSS variables (`--text`, `--bg`, `--accent`, …). **All three are stale** (predate `#89`–`#97`).

## 3. Requirements (EARS acceptance criteria = Definition of Done)

### R1 — Mermaid renders in-app
- **R1.1** WHEN a bundled doc contains a fenced ` ```mermaid ` block, THE system SHALL render it as an SVG diagram in the `/docs` view (not as raw text).
- **R1.2** THE mermaid theme SHALL follow the app theme (light/dark) via the existing CSS theme variables / mermaid theme config, so a diagram is legible in both modes.
- **R1.3** IF a mermaid block fails to parse, THEN THE system SHALL fall back to showing the original code block (fail-soft, never a blank or a thrown error that breaks the page).
- **R1.4** Mermaid SHALL be loaded client-side only (it needs the DOM); SSR/prerender of `/docs` SHALL NOT break (the static build must still succeed).

### R2 — Living-diagram visuals embedded
- **R2.1** THE `/docs` view SHALL present the three living diagrams (Working Model, Runtime Infrastructure, App Functionality) as interactive panels reachable from the docs navigation.
- **R2.2** Each embedded diagram SHALL preserve its interactivity (tab switching, click-for-detail popovers) — i.e. its inline `<script>` SHALL execute in an isolated context (sandboxed `<iframe>` or an equivalent dedicated component), NOT via the `DOMPurify` markdown path (which strips `<script>`).
- **R2.3** THE embed SHALL inherit the app theme (the diagram's CSS variables resolve to the active light/dark palette), so it matches the surrounding page.
- **R2.4** THE embedded diagram source SHALL be the **refreshed, current-state** HTML (post-prerequisite), committed into the repo as a build-time asset — NOT fetched live from the Kiro Crew artifact store at runtime (the app must build and deploy without any Kiro Crew dependency).
- **R2.5** THE iframe/embedding boundary SHALL NOT introduce an XSS or clickjacking regression: the embedded content is first-party committed HTML, sandboxed to script-only (no top-navigation, no form posts to third parties).

### R3 — Standard in-app docs navigation
- **R3.1** THE `/docs` view SHALL show a single breadcrumb `Dashboard › Docs › <Guide>` consistent with the app, and SHALL NOT also render a separate redundant "← Back to Dashboard" control.
- **R3.2** In-app doc navigation SHALL rely on the global header for "home"/portfolio and on the breadcrumb for "where am I / back to parent" — no repo-file links leak into the consumer view (the existing GitHub "View source" affordance is retained and clearly labelled as external).
- **R3.3** THE navigation standard (breadcrumb shape, back-to-parent behavior) SHALL be documented once (a short section in `docs/README.md` or the design system doc) and applied identically to every in-app doc.

### R4 — Scope floor (what must NOT change)
- **R4.1** NO change to data, schema, PocketBase rules, or auth behavior. This is a render-pipeline + nav + content-embed change only.
- **R4.2** THE `INCLUDED_DOCS` allow-list SHALL remain a deliberate consumer-facing set; this Spec MAY add the sprint-lifecycle guide and/or a diagrams entry, but SHALL NOT bulk-expose internal guides. Any added doc is listed explicitly with a one-line rationale.
- **R4.3** THE status-reporting spine (STATUS.md / journal / broadcast) and the generated README registry block SHALL be untouched (byte-identical registry).

### R5 — Governance lockstep
- **R5.1** `just validate-local` (portfolio validator + generator `--check` gates + SvelteKit typecheck/build) SHALL pass green.
- **R5.2** CHANGELOG `[Unreleased]` SHALL record the feature; the Decision Journal SHALL get an entry if an architectural choice is made (iframe vs component for R2).
- **R5.3** THE SvelteKit static build (`pnpm build`, `adapter-static`) SHALL succeed with mermaid + the embedded diagrams present.

---

## 4. Out of scope
- Live fetching of artifacts from Kiro Crew at runtime (R2.4 forbids it — embeds are committed assets).
- A general "render ANY artifact in the app" framework — this Spec embeds exactly the three named living diagrams.
- Exposing internal guides (AIDLC, release, dev-guide) in-app — the allow-list stays consumer-scoped (R4.2).
- The living-diagram **content refresh** itself is a doc-class prerequisite (tracked separately), not part of this gated build — this Spec consumes the refreshed HTML.

---

> 🧭 **Navigation:** [⬆️ Top](#top) · [🏠 Repo](../../../README.md) · [📚 Docs Hub](../../../docs/README.md)
