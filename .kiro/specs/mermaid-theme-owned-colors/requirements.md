# Mermaid Node Labels — Theme-Owned Colors (Option C) — Requirements

| Property | Value |
| :--- | :--- |
| **Spec ID** | `mermaid-theme-owned-colors` |
| **Feature** | Fully fix in-app mermaid **flowchart + state-diagram node labels** rendering as empty boxes. Remove the custom `classDef`/`class` fill+`color:#fff` directives from the bundled diagram sources so **mermaid's theme owns both node fill and label contrast** — the labels then render as SVG `<text>` in a theme-correct color, with no sanitizer change and no per-node color coupling. |
| **Backlog** | `BK-039` (`TSK-078`, SPRINT-13) — **correction** of BK-038 (#102), which fixed edge labels but not node labels. |
| **Work class** | **Sprint deliverable** (product `/docs` surface) → **FULL gate**: Spec → `/spec-run` → `/review-pr` → human merge. |
| **Depends on** | BK-037 (#100, mermaid pipeline), BK-038 (#102, `htmlLabels:false` — kept). |
| **Executor role** | **Antigravity (Primary Executor)** — edits to 2 doc sources (+ possibly a mermaid config tidy). |
| **Source** | Operator session 2026-10-10 — after BK-038, user screenshots + a local test still showed **empty node boxes** (edge labels OK). A themeVariables spike (`spike/mermaid-node-text-color`) did NOT fix it → confirmed the root cause is the diagram sources' custom colors, not the render config. |

---

## 1. Root cause (now fully diagnosed, empirically)

- BK-037 rendered mermaid; BK-038 set `flowchart: { htmlLabels: false }` so labels are SVG `<text>` (fixed **edge** labels, which have no custom color).
- **Node** labels stayed invisible because the bundled flowchart sources use `classDef … color:#fff` (and dark custom fills `#1e3a5f`, `#0f2a1e`). The `color:` property styles **HTML** labels only — it does **not** color SVG `<text>` (which needs `fill:`). So after `htmlLabels:false`, node labels fall back to a color that is invisible against the custom fills → empty boxes.
- A `themeVariables` spike (global SVG text color) was tried and **rejected**: a single global text color cannot be readable on both the dark custom-filled nodes *and* the light/lavender default nodes at once. Verified by local test — issue persisted.
- The `stateDiagram-v2` in `sprint-lifecycle.md` also shows empty nodes; it has **no** `classDef` — its labels are governed purely by the theme, confirming the fix must let the theme own colors rather than fight it per-node.

## 2. The decision — let mermaid's theme own fill + text contrast (Option C)

Keep `htmlLabels: false` (BK-038) and keep the **tight DOMPurify SVG profile unchanged** (no `foreignObject`, no widening — the security posture BK-038 established stays). Instead, **remove the custom `classDef`/`class` fill+color directives** from the two bundled flowchart sources so each node uses mermaid's `theme: 'dark' | 'default'` palette, which colors SVG `<text>` labels for contrast automatically and consistently in both themes.

Rejected alternatives:
- **A (allow `<foreignObject>` + revert to `htmlLabels:true`)** — renders the custom colors but widens the sanitizer; reverses BK-038. Not chosen — C needs no sanitizer change.
- **B (themeVariables global text color)** — spike-tested, insufficient (can't satisfy dark + light fills simultaneously).

## 3. Requirements (EARS acceptance criteria = Definition of Done)

- **R1** THE bundled flowchart sources (`docs/guides/sprint-lifecycle.md`, `docs/guides/project-owner-guide.md`) SHALL have their custom `classDef … fill/color` definitions and `class …` applications **removed** (or reduced to stroke-only accents that do NOT set a node fill or a label `color`), so node fill + label color are owned by the mermaid theme.
- **R2** WHEN `/docs` renders these diagrams, EVERY flowchart node AND state-diagram node SHALL display its label text legibly, in **both** light and dark app themes (no empty boxes, no invisible text).
- **R3** THE `mermaid.initialize` config SHALL keep `securityLevel: 'strict'`, keep `flowchart: { htmlLabels: false }`, and keep the DOMPurify SVG-profile sanitize **unchanged** (no `foreignObject`, no profile widening). The spike `themeVariables` block, if present on any branch, SHALL NOT be carried in (or SHALL be kept only if it demonstrably helps light+dark and does not regress — default: remove it).
- **R4** Sequence diagrams and the three embedded living diagrams SHALL render unchanged (no regression).
- **R5** THE semantic meaning the colors conveyed (e.g. "gate" vs "action" nodes) SHALL be preserved by a theme-safe means if still desired — e.g. node shape, an emoji/text prefix in the label, or a stroke-only accent — NOT a custom fill that breaks label contrast. (If the distinction is non-essential, dropping it is acceptable.)
- **R6 (lockstep):** `just validate-local` green; static build succeeds; README registry byte-identical; CHANGELOG `[Unreleased]` records the correction.

## 4. Human Verification Plan (visual — Operator cannot verify headless)
- **V1:** `/docs?doc=sprint-lifecycle` — the flow-at-a-glance flowchart AND the state-machine `stateDiagram` nodes show labels, **light + dark**.
- **V2:** `/docs?doc=project-owner` — the flowchart nodes show labels, light + dark.
- **V3:** `/docs?doc=diagrams` — living diagrams + sequence diagrams unchanged (no regression).
- **V4:** `just validate-local` green.

## 5. Out of scope
- Sanitizer changes / `foreignObject` (that is Option A, explicitly not chosen).
- The living-diagram HTML assets (self-contained, unaffected).

---

> 🧭 **Navigation:** [⬆️ Top](#top) · [🏠 Repo](../../../README.md) · [📚 Docs Hub](../../../docs/README.md)
