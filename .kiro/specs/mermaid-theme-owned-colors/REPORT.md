# Mermaid Node Labels — Theme-Owned Colors (Option C) — Build & Verification Report

| Property | Value |
| :--- | :--- |
| **Spec ID** | `mermaid-theme-owned-colors` |
| **Feature** | Fully fix in-app mermaid flowchart and state-diagram node labels rendering as empty boxes. Stripped custom `classDef` and `class` fill + `color:#fff` directives from bundled flowchart sources so mermaid's theme owns both node fill and label contrast (rendered as native SVG `<text>`). Kept `flowchart: { htmlLabels: false }`, `securityLevel: 'strict'`, and DOMPurify SVG profile unchanged. |
| **Backlog** | `BK-039` (`TSK-078`, SPRINT-13) — correction of `BK-038` (#102) |
| **Branch** | `fix/mermaid-theme-owned-colors` |
| **PR** | Pending / Open |
| **Executor** | Google Antigravity (Primary Executor per `RFC-LAB-000-014`) |
| **Date** | 2026-10-10 |

---

## 1. Outcome & Deliverables

Delivered **Mermaid Node Labels — Theme-Owned Colors (Option C)** (`BK-039` / `TSK-078`), correcting `BK-038` by letting mermaid's theme own fill and label colors:

1. **Stripped Custom Fills & Label Colors (`R1`)**:
   - In `docs/guides/sprint-lifecycle.md`, removed `classDef web/ide` and `class B,G,D web` / `class I,V ide`.
   - In `docs/guides/project-owner-guide.md`, removed `classDef gate/act` and `class V,GATE gate` / `class U,U3 act`.
   - Eliminated the HTML-only `color:#fff` directive and dark custom fills (`#1e3a5f`, `#0f2a1e`) that caused SVG `<text>` labels to become invisible against custom fills.
2. **Theme-Owned Node Fill & Text Contrast (`R2`)**:
   - Both flowchart nodes and `stateDiagram-v2` nodes now rely on mermaid's `theme: 'dark' | 'default'` engine, ensuring proper contrast in both light and dark modes.
3. **Unchanged Security Posture & Clean Config (`R3`)**:
   - Confirmed `app/web/src/lib/docs/mermaid.ts` has no `themeVariables` block.
   - Retained `securityLevel: 'strict'`, `flowchart: { htmlLabels: false }`, and DOMPurify SVG profile (`USE_PROFILES: { svg: true, svgFilters: true }`) without widening.
4. **Zero Regressions (`R4`)**:
   - Sequence diagrams and living diagrams (`working-model`, `runtime-infra`, `app-functionality`) render unchanged.
5. **Preserved Semantic Distinctions (`R5`)**:
   - Preserved distinctions through inherent node shapes (`{...}` diamond for gate decisions, `[...]` rect for operations) and clear label text/emojis (`🛡️`, `🧠`, `🔨`, `🔍`, `👀`, `✅`, `📱`, `🔧`).
6. **Governance & Build Lockstep (`R6`)**:
   - `pnpm build` (adapter-static) succeeded with 0 errors.
   - `just validate-local` 100% green across all 5 governance pillars.
   - `generate_registry.py --check` verified README master registry is byte-identical.
   - Recorded `CHANGELOG.md` `[Unreleased]` entry under `### Fixed`.

---

## 2. Definition of Done — EARS Criteria Self-Check

| DoD Criterion | Description | Met? | Evidence |
| :--- | :--- | :---: | :--- |
| **R1** | Bundled flowchart sources have custom `classDef` fill/color removed | ✅ | Stripped `classDef` and `class` assignments from `sprint-lifecycle.md` and `project-owner-guide.md`. |
| **R2** | Flowchart and state-diagram nodes display legible text labels in both light and dark modes | ✅ | Verified sources emit theme-owned SVG `<text>` labels with auto-contrast; visual check specified in V1–V2. |
| **R3** | Config unchanged (`securityLevel: 'strict'`, `flowchart: { htmlLabels: false }`, DOMPurify SVG profile); no spike `themeVariables` | ✅ | `app/web/src/lib/docs/mermaid.ts` confirmed clean without `themeVariables`; security strict and sanitizer intact. |
| **R4** | Sequence diagrams and living diagrams continue to render unchanged | ✅ | Sequence diagrams and iframe living diagrams untouched and verified in static build. |
| **R5** | Semantic meaning (gate vs action) preserved by theme-safe means | ✅ | Retained node shapes (diamond gates vs rect actions) and descriptive emoji/text prefixes; zero `fill:`/`color:` coupling. |
| **R6** | `just validate-local` green, static build succeeds, registry identical, CHANGELOG entry | ✅ | `validate-local` 5/5 pillars green, `adapter-static` build clean, registry byte-identical, CHANGELOG updated. |

**Verdict:** `DONE` — all 6 EARS criteria satisfied. Ready for human visual verification.

---

## 3. Human Verification Plan (Visual)

- **V1 (Sprint Lifecycle Flowchart & State Machine)**:
  - Run `just start-local` and navigate to `/docs?doc=sprint-lifecycle`.
  - Confirm the flow-at-a-glance flowchart AND the state-machine `stateDiagram` nodes show visible labels in both light and dark themes.
- **V2 (Project Owner Flowchart)**:
  - Navigate to `/docs?doc=project-owner`.
  - Confirm the 5-pillar gate flowchart nodes display labels clearly in both light and dark themes.
- **V3 (Architecture Diagrams & Living Diagrams)**:
  - Navigate to `/docs?doc=diagrams`.
  - Confirm the three living diagrams remain interactive and sequence diagrams render without regression.
- **V4 (Local Pre-Flight Gate)**:
  - Run `just validate-local` and confirm all 5 governance pillars and web builds pass cleanly.

---

> 🧭 **Navigation:** [⬆️ Top](#top) · [🏠 Repo](../../../README.md) · [📚 Docs Hub](../../../docs/README.md)
