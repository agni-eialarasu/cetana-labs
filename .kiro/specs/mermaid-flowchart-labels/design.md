# Mermaid Flowchart Labels Fix — Design

| Property | Value |
| :--- | :--- |
| **Spec ID** | `mermaid-flowchart-labels` · **Backlog** `BK-038` |
| **Status** | Design — Operator 2026-10-10, for Antigravity `/spec-run` after merge-first. |

## 1. The change

Single edit to `app/web/src/lib/docs/mermaid.ts`, in the `mermaid.initialize(...)` call:

```
mermaid.initialize({
  startOnLoad: false,
  securityLevel: 'strict',
  flowchart: { htmlLabels: false },   // ← add: labels render as SVG <text>, survive strict + the SVG-profile sanitize
  theme
});
```

## 2. Why this fixes it (and why not the alternatives)

| Option | Verdict |
| :--- | :--- |
| **A. `flowchart: { htmlLabels: false }` (chosen)** | Flowchart labels render as native SVG `<text>` instead of `<foreignObject>` HTML. SVG `<text>` passes both `securityLevel: 'strict'` and the DOMPurify SVG profile untouched. One line, no security change, no sanitizer change. |
| B. Widen DOMPurify to `ADD_TAGS: ['foreignObject']` + allow its HTML children | Re-admits arbitrary HTML into the sanitized SVG — defeats the reason the SVG profile is tight. Rejected (R3). |
| C. Drop to `securityLevel: 'loose'` | Loosens the whole mermaid security posture for a label-rendering problem. Rejected (R3). |

`htmlLabels: false` is the mermaid-recommended path exactly for strict/sanitized environments. Native-text labels lose nothing for our content (plain-text node labels; no embedded markup in the docs' flowcharts).

## 3. Risk & verification
- **Risk:** negligible — one config flag, no new dependency, no pipeline change. Theoretical: a flowchart label that *relied* on HTML markup would lose it — but our docs' flowchart labels are plain text (verify in V1/V2).
- **Can't self-verify headless** — the DoD's V1–V3 are human visual checks (the Operator has no local render).
- Fail-soft + SSR-safety are untouched (same `try/catch`, same `onMount`/effect timing).

## 4. Files touched
- `app/web/src/lib/docs/mermaid.ts` — add `flowchart: { htmlLabels: false }`.
- `CHANGELOG.md` — lockstep entry.

---

> 🧭 **Navigation:** [⬆️ Top](#top) · [🏠 Repo](../../../README.md) · [📚 Docs Hub](../../../docs/README.md)
