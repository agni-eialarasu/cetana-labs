# Mermaid Flowchart Labels Fix — Tasks

| Property | Value |
| :--- | :--- |
| **Spec ID** | `mermaid-flowchart-labels` · **Backlog** `BK-038` |
| **Branch** | `fix/mermaid-flowchart-labels` |
| **Executor** | Antigravity (Primary Executor). |
| **Gate** | Full gate: `/spec-run` → PR → `/review-pr` → human merge. Merge-first: this Spec on `main` before build. |

## Task 1 — Config fix
- [ ] In `app/web/src/lib/docs/mermaid.ts`, add `flowchart: { htmlLabels: false }` to the `mermaid.initialize({...})` object (keep `securityLevel: 'strict'`, keep `theme`, keep the DOMPurify SVG-profile sanitize unchanged).
- **Verify (code):** no other change to the render/sanitize/fail-soft logic; `svelte-check` + typecheck clean.

## Task 2 — Build + self-validate (DoD)
- [ ] `pnpm build` (adapter-static) succeeds.
- [ ] `just validate-local` green (R6).
- [ ] README registry byte-identical (`generate_registry.py --check`).
- [ ] CHANGELOG `[Unreleased]` entry for BK-038.
- [ ] Open PR via `gh api`; write `REPORT.md` with the EARS R1–R6 self-check; STOP-and-hold. **Never merge.**

## Task 3 — Human visual verification (in `/review-pr` / `/verification-done`)
- [ ] V1: `/docs?doc=sprint-lifecycle` flowchart labels render (light + dark).
- [ ] V2: `/docs?doc=project-owner` flowchart labels render.
- [ ] V3: `/docs?doc=diagrams` living diagrams + any flowchart render, no regression; sequence diagrams unaffected.
- [ ] V4: `just validate-local` green.

## Definition of Done
- **R1–R2** `flowchart: { htmlLabels: false }` set; flowchart node labels render (no empty boxes), light + dark.
- **R3** security unchanged — strict + tight SVG profile retained.
- **R4–R5** no regression to sequence diagrams / living diagrams; fail-soft + SSR-safety preserved.
- **R6** validate-local + static build green; lockstep recorded.

---

> 🧭 **Navigation:** [⬆️ Top](#top) · [🏠 Repo](../../../README.md) · [📚 Docs Hub](../../../docs/README.md)
