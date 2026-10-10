# Mermaid Node Labels — Theme-Owned Colors (Option C) — Tasks

| Property | Value |
| :--- | :--- |
| **Spec ID** | `mermaid-theme-owned-colors` · **Backlog** `BK-039` |
| **Branch** | `fix/mermaid-theme-owned-colors` (cut fresh from `main` — NOT the spike branch) |
| **Executor** | Antigravity (Primary Executor). |
| **Gate** | Full gate: `/spec-run` → PR → `/review-pr` → human merge. Merge-first: Spec on `main` first. |

## Task 0 — Confirm clean base
- [x] Cut `fix/mermaid-theme-owned-colors` from `main`. Confirm `app/web/src/lib/docs/mermaid.ts` on `main` has NO `themeVariables` block (the spike did not merge). If present, remove it. Keep `htmlLabels: false`, `securityLevel: 'strict'`, and the DOMPurify SVG profile unchanged.

## Task 1 — Strip custom colors from the two flowchart sources
- [x] `docs/guides/sprint-lifecycle.md`: remove the `classDef web/ide` lines + `class B,G,D web` / `class I,V ide`. Optionally preserve the gate/step distinction via node shape or a label prefix (design §2) — NO `fill:`+`color:` on nodes.
- [x] `docs/guides/project-owner-guide.md`: remove `classDef gate/act` + `class V,GATE gate` / `class U,U3 act`. Same accent guidance.
- [x] **Verify (source):** no `classDef … color:#` or `fill:#…color:` remains in either flowchart.

## Task 2 — Build + self-validate (DoD)
- [x] `pnpm build` (adapter-static) succeeds; `just validate-local` green.
- [x] README registry byte-identical (`generate_registry.py --check`).
- [x] CHANGELOG `[Unreleased]` entry for BK-039 (correction of BK-038).
- [x] Open PR via `gh api` ([PR #104](https://github.com/agni-eialarasu/cetana-labs/pull/104)); write `REPORT.md` with the EARS R1–R6 self-check; STOP-and-hold. **Never merge.**

## Task 3 — Human visual verification (in `/verification-done` / `/review-pr`)
- [ ] V1: `/docs?doc=sprint-lifecycle` — flowchart AND `stateDiagram` nodes show labels, **light + dark**.
- [ ] V2: `/docs?doc=project-owner` — flowchart nodes show labels, light + dark.
- [ ] V3: `/docs?doc=diagrams` — living + sequence diagrams unchanged.
- [ ] V4: `just validate-local` green.

## Definition of Done
- **R1** custom `classDef`/`class` fill+color removed from both flowchart sources.
- **R2** all flowchart + state-diagram nodes show legible labels, light + dark.
- **R3** config unchanged (strict + htmlLabels:false + tight SVG profile); no spike themeVariables.
- **R4** no regression (sequence + living diagrams).
- **R5** role distinction preserved by a theme-safe means (shape/prefix/stroke) or intentionally dropped.
- **R6** validate-local + build green; lockstep recorded.

---

> 🧭 **Navigation:** [⬆️ Top](#top) · [🏠 Repo](../../../README.md) · [📚 Docs Hub](../../../docs/README.md)
