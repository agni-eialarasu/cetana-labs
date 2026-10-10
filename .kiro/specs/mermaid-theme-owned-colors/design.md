# Mermaid Node Labels — Theme-Owned Colors (Option C) — Design

| Property | Value |
| :--- | :--- |
| **Spec ID** | `mermaid-theme-owned-colors` · **Backlog** `BK-039` |
| **Status** | Design — Operator 2026-10-10, for Antigravity `/spec-run` after merge-first. Corrects BK-038 (#102). |

## 1. The change — two doc sources, config untouched

The fix lives in the **diagram sources**, not the render pipeline. `mermaid.ts` stays as BK-038 left it (`htmlLabels: false`, `securityLevel: 'strict'`, tight SVG profile) — **except** removing the spike `themeVariables` block if it rode in (it did not merge; confirm it is absent on `main`).

### 1a. `docs/guides/sprint-lifecycle.md` (flowchart, lines ~24-38)
Remove:
```
classDef web fill:#1e3a5f,stroke:#3b82f6,color:#fff;
classDef ide fill:#0f2a1e,stroke:#22c55e,color:#fff;
class B,G,D web;
class I,V ide;
```
Nodes then use the mermaid theme's default fill + auto-contrast label color (SVG `<text>`). The `stateDiagram-v2` in the same file has no classDef — it is already theme-governed and is fixed by the same theme-owns-colors principle (no edit needed beyond confirming it renders).

### 1b. `docs/guides/project-owner-guide.md` (flowchart, lines ~17-38)
Remove:
```
classDef gate fill:#1e3a5f,stroke:#3b82f6,color:#fff;
classDef act fill:#0f2a1e,stroke:#22c55e,color:#fff;
class V,GATE gate;
class U,U3 act;
```

## 2. Preserving the semantic accent (R5) — theme-safe options

The custom fills marked "gate/action" vs "web/ide" node roles. To keep that signal without breaking label contrast, prefer (in order):
1. **Node shape** — mermaid flowchart shapes already differ (`{...}` diamond for gates, `[...]` rect for steps). Often the shape alone carries it → drop color entirely (simplest, chosen default).
2. **Label prefix** — a short emoji/text in the node label (e.g. `GATE 1 ✋`, `🤖 …`) — theme-independent, always legible.
3. **Stroke-only accent** — `classDef gate stroke:#3b82f6,stroke-width:2px;` with **no `fill`, no `color`** — a colored border, theme-owned fill/text. Use only if a color cue is genuinely needed.

**Do NOT** reintroduce `fill:` + `color:` on a node — that is the exact coupling that caused the bug.

## 3. Why this is the right fix (vs A/B)
- **No sanitizer change** — the tight SVG profile BK-038 established is preserved (security posture intact).
- **No per-node color coupling** — the fragile `color:#fff`-on-custom-fill idiom (HTML-label-only) is removed, so it cannot silently break again when the render path changes.
- **Light + dark both work** — mermaid's theme computes label contrast against its own fills in each theme; a global override (spike B) could not.
- Trade: the diagrams lose their hand-picked navy/green fills, gaining mermaid-theme fills. Acceptable — legible labels > custom palette, and R5 keeps the role distinction by shape/prefix.

## 4. Files touched
- `docs/guides/sprint-lifecycle.md` — strip flowchart classDef/class (+ optional shape/prefix accents).
- `docs/guides/project-owner-guide.md` — same.
- `app/web/src/lib/docs/mermaid.ts` — only if the spike `themeVariables` is present on the build branch; otherwise untouched.
- `CHANGELOG.md` — lockstep.

## 5. Risk & verification
- **Risk:** low — doc-source edits + a config confirm. Could not self-verify rendering (headless) → the DoD V1–V3 are **human visual** checks (dark + light, nodes + state diagram).
- The spike branch `spike/mermaid-node-text-color` is **not** the build branch — it is deleted; the build cuts fresh from `main`.

---

> 🧭 **Navigation:** [⬆️ Top](#top) · [🏠 Repo](../../../README.md) · [📚 Docs Hub](../../../docs/README.md)
