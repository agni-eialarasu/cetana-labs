# Mermaid Flowchart Labels Fix — Requirements

| Property | Value |
| :--- | :--- |
| **Spec ID** | `mermaid-flowchart-labels` |
| **Feature** | Fix in-app mermaid **flowchart** rendering: flowchart nodes currently render as empty colored boxes (labels missing) in `/docs`. Make flowchart node labels render. |
| **Backlog** | `BK-038` (`TSK-077`, SPRINT-13) — defect follow-up to `BK-037` (#100). |
| **Work class** | **Sprint deliverable** (product `/docs` surface a user exercises) → **FULL gate**: Spec → `/spec-run` → `/review-pr` → human merge. |
| **Depends on** | `BK-037` (#100 — the mermaid render pipeline this fixes). |
| **Executor role** | **Antigravity (Primary Executor)** — one-file config change in `app/web/src/lib/docs/mermaid.ts`. |
| **Source** | Operator session 2026-10-10 — user screenshots of `/docs?doc=diagrams`, `?doc=sprint-lifecycle`, `?doc=project-owner` showing empty flowchart node boxes; sequence diagrams render correctly. |

---

## 1. Introduction

BK-037 shipped client-side mermaid rendering. **Sequence** diagrams render correctly, but **flowchart** diagrams render their node shapes (boxes/diamonds/arrows, correctly colored) **with no label text inside** — empty boxes. Confirmed across three docs: the sprint-lifecycle state machine + flow-at-a-glance, and the project-owner flowchart.

## 2. Root cause (verified in `app/web/src/lib/docs/mermaid.ts` on `main`)

Two settings compound:
1. `mermaid.initialize({ securityLevel: 'strict', theme })` — in strict mode mermaid renders **flowchart** node labels as HTML wrapped in `<foreignObject>` (the mermaid default `flowchart.htmlLabels: true`).
2. The post-render sanitize `DOMPurify.sanitize(svg, { USE_PROFILES: { svg: true, svgFilters: true } })` — the SVG profile does **not** include `<foreignObject>` (nor its HTML children), so the labels are **stripped** after render → empty nodes.

**Sequence diagrams are unaffected** because they emit labels as native SVG `<text>`, which both strict mode and the SVG profile pass. This asymmetry (sequence ✅ / flowchart ✗) is the fingerprint that confirms the `<foreignObject>` path is the culprit.

## 3. Requirements (EARS acceptance criteria = Definition of Done)

- **R1** THE mermaid config SHALL set `flowchart: { htmlLabels: false }` in `mermaid.initialize(...)`, so flowchart node labels render as SVG `<text>` instead of HTML `<foreignObject>`.
- **R2** WHEN a doc contains a mermaid `flowchart`/`graph` block, THE rendered nodes SHALL display their label text in `/docs` (no empty boxes), in both light and dark themes.
- **R3** THE fix SHALL NOT loosen the security posture: `securityLevel` stays `'strict'` and the DOMPurify SVG-profile sanitize pass stays unchanged (no `ADD_TAGS: ['foreignObject']`, no profile widening). Labels-as-`<text>` is the sanitizer-compatible path.
- **R4** Sequence diagrams and the three embedded living diagrams SHALL continue to render unchanged (no regression).
- **R5** THE fail-soft behavior (R1.3 of BK-037 — per-block `try/catch` leaving the raw code block on parse error) and SSR-safety SHALL be preserved.
- **R6 (lockstep):** `just validate-local` green; static build (`adapter-static`) succeeds; README registry byte-identical; CHANGELOG `[Unreleased]` records the fix.

## 4. Human Verification Plan (visual — the Operator cannot verify rendering headless)
- **V1:** `just start-local` → open `/docs?doc=sprint-lifecycle` → the state-machine flowchart nodes show their labels (not empty boxes), light + dark.
- **V2:** `/docs?doc=project-owner` → the flowchart renders labels.
- **V3:** `/docs?doc=diagrams` → the three living diagrams still render + are interactive (no regression); any flowchart inside renders labels.
- **V4:** `just validate-local` green.

## 5. Out of scope
- Any change to the living-diagram HTML assets (they are self-contained HTML, not mermaid).
- Widening the DOMPurify profile to allow `<foreignObject>` (R3 forbids — the `htmlLabels: false` path avoids needing it).

---

> 🧭 **Navigation:** [⬆️ Top](#top) · [🏠 Repo](../../../README.md) · [📚 Docs Hub](../../../docs/README.md)
