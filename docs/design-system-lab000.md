# Design System — LAB-000 Adaptation (SvelteKit)

> **Relationship to the org design system:** [`DESIGN.md`](DESIGN.md) is the
> **authoritative visual source of truth** (the Nexus Pulse Design System). This
> file does **not** override it — it **translates** that system from its native
> Next.js / React / Tailwind stack to the Cetana Labs Control Hub web app
> (`LAB-000`), which is built on **SvelteKit + Tailwind** per
> [`RFC-LAB-000-005`](rfc/RFC-LAB-000-005-web-app-phase2-ui.md).
>
> **Rule of precedence:** tokens/colors/type/spacing/anti-patterns in `DESIGN.md`
> are binding. Where `DESIGN.md` references a **Next.js file** (`layout.tsx`,
> `globals.css`, `tailwind.config.ts`, `.tsx` components), read the SvelteKit
> equivalent from the mapping below. Consistent with `DESIGN.md`, **CSS tokens win**
> as the runtime source of truth.

---

## 1. Adopt Verbatim (framework-agnostic — binding)

These carry over **unchanged** from `DESIGN.md`:

- **Color tokens** — the full `--np-*` light/dark table. **Blue accent** (`#2563eb` light / `#60a5fa` dark). Never purple/violet/indigo gradients or teal.
- **Typography** — **IBM Plex Sans** (UI/body) + **IBM Plex Mono** (numbers/evidence, `tabular-nums`). Never Inter / system-ui as the primary face. The type scale (h1 30–34px/650, body 14px, meta 12–13px, eyebrow 11–12px).
- **Spacing** — 4px base; scale 4/8/12/16/20/24/32/48; ~1500px max content width.
- **Appearance** — **dark-first** (`data-theme="dark"` on root) + optional light switch; legible under Increase Contrast / Reduce Transparency (solid chrome, no blur reliance).
- **Severity = color + word** (never color alone); soft/ink pairs for small labels; AA contrast (≥4.5:1 text, ≥3:1 large).
- **Motion** — intentional/minimal; honor `prefers-reduced-motion`.
- **Writing** — sentence-case titles; actions name the outcome; no em dashes in UI copy.
- **The banned anti-patterns list** — applies in full.

---

## 2. Framework Mapping (Next.js → SvelteKit)

| `DESIGN.md` reference | LAB-000 SvelteKit equivalent |
| :--- | :--- |
| `apps/web/` | `app/web/` (sibling to `app/pocketbase/`) |
| `app/globals.css` (tokens/chrome) | `app/web/src/app.css` (canonical `--np-*` tokens) |
| `app/layout.tsx` + `next/font` | `app/web/src/routes/+layout.svelte` + fonts via `@fontsource/ibm-plex-sans` & `@fontsource/ibm-plex-mono` (self-hosted; **not** `next/font`) |
| `tailwind.config.ts` (token mirror) | `app/web/tailwind.config.js` mirroring the same `--np-*` tokens |
| `AppShell.tsx`, `ShellFrame.tsx` | `AppShell.svelte`, `ShellFrame.svelte` |
| `SidebarNav.tsx` | `SidebarNav.svelte` (**LAB-000 IA — see §4, not Nexus Pulse routes**) |
| `ThemeToggle.tsx` | `ThemeToggle.svelte` |
| `MetricCard.tsx`, `SignalCard.tsx`, `QuestionHeader.tsx` | `MetricCard.svelte`, `ProjectCard.svelte`, `PageHeader.svelte` |
| `components/charts/` (D3) | `app/web/src/lib/charts/` (D3) — deferred to Phase 5 telemetry |
| Fonts via `next/font` | `@fontsource/*` imports in `+layout.svelte` (Svelte 5 + pnpm) |

**Tailwind:** adopt Tailwind in the SvelteKit app (`RFC-LAB-000-005` Q4), with
`tailwind.config.js` mapping the `--np-*` CSS variables to utility names (e.g.
`bg-panel`, `text-ink`, `text-muted`, `border-line`, `bg-brand`, `text-on-accent`).
Utilities are conveniences; the CSS custom properties remain the runtime SoT.

---

## 3. Responsive Targets (small / medium / large)

Per the request for a responsive UI across device sizes, formalize Tailwind
breakpoints (aligned with the `DESIGN.md` ≤1000px rule):

| Tier | Range | Layout behavior |
| :--- | :--- | :--- |
| **Small** (mobile) | `< 640px` | Single-column cards; compact sticky top bar + **Menu toggle**; page padding tightened (~16px); KPI bar wraps/scrolls. |
| **Medium** (tablet) | `640–1024px` | 2-column card grid; sidebar collapses to the compact top-bar + Menu toggle at **≤1000px** (per `DESIGN.md`); never hide section labels when expanded. |
| **Large** (desktop) | `≥ 1024px` | Sticky ~230px sidebar + main work area; multi-column card grid; page padding ~32×38px; content max-width ~1500px. |

Tailwind mapping: `sm:640px` · `md:768px` · `lg:1024px` · `xl:1280px` (the
sidebar/top-bar switch keys off the ~1000px rule, implemented at the `lg` boundary).
Cards use `radius ~12–14px`; controls `~8px`. Honor `prefers-reduced-motion`.

---

## 4. LAB-000 Information Architecture (not Nexus Pulse's)

`DESIGN.md`'s Attention / Position / Intelligence nav is **Nexus Pulse's** IA and
does **not** transfer. The Control Hub dashboard applies the *design system* to its
own IA (the read-parity view from `RFC-LAB-000-005` §5):

- **Header/shell**: brand wordmark, theme toggle, primary actions (Copy Executive Digest, GitHub link).
- **KPI bar**: Active · Hard Blockers · Onboarding · Completed · Total (tabular numbers; severity = color + word).
- **Controls**: filter tabs (Active/All/Onboarding/Completed/Control Hub), sort (Executive Priority / Recently Updated / Project ID), text search.
- **Project cards**: owner pill (top-left), health pill (color + word), archetype, pitch, wins/focus, blocker banner (severity rail + label).

A sidebar is optional for LAB-000's single-view dashboard; if introduced later
(Phases 3–5), it follows the `DESIGN.md` single-sidebar rule (no dual icon-rail).

---

## 5. Health/Severity Token Mapping

Map the existing Cetana health badges onto the `DESIGN.md` severity roles:

| Cetana health | DESIGN role | Tokens |
| :--- | :--- | :--- |
| 🟢 On Track / ✅ Completed | Live / complete | `--live-soft` / `--live` |
| 🟡 At Risk / ⏳ Onboarding Pending | Warning | `--warn-soft` / `--warn-ink` / `--warn` |
| 🔴 Blocked (has blocker) | Critical / block | `--critical-soft` / `--critical` |
| ⏸️ Paused / informational | Info | `--info-soft` / `--info` |

Always render the **word** alongside the color (e.g. "On Track", "Blocked").
