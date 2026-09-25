# Design System — Nexus Pulse

**Authority:** This file is the single design source of truth for visual and UI
decisions. Live tokens live in `apps/web/app/globals.css`. When a hex or spacing
value disagrees with CSS, **CSS wins**.

| Layer | File | Role |
| --- | --- | --- |
| Shell, theme, type, components | `apps/web/app/globals.css` | Canonical dark/light workspace |
| Fonts | `apps/web/app/layout.tsx` | IBM Plex Sans + IBM Plex Mono via `next/font` |
| Shell / nav | `apps/web/components/AppShell.tsx`, `SidebarNav.tsx`, `ThemeToggle.tsx` | One sidebar + grouped IA + theme switch |
| Tailwind map | `apps/web/tailwind.config.ts` | Mirrors CSS tokens for utility use |

Inspired by calm industrial ops-console craft (Zerobea R7 patterns). **Brand
accent is blue**, not purple. Do not restore teal experiments or purple/violet
gradient chrome.

---

## Product Context

- **What this is:** Governed operating intelligence for professional-services
  delivery. Exception-first answers with evidence — not a feature dump.
- **Who it's for:** Delivery, ops, and finance leaders who need trustworthy
  margin, capacity, and signal positions; demo operators running the HarborPoint
  journey.
- **Space / industry:** Delivery / PSA / FP&A-adjacent operating dashboards
  (peers: enterprise ops consoles, not marketing sites).
- **Project type:** Next.js product dashboard (`apps/web`).
- **Memorable thing:** **The numbers you can trust.** Every primary screen opens
  on a customer question; figures are governed facts with evidence. Never treat
  a LIVE signal source as “the signal is firing,” and never invent severity from
  a rate alone.

---

## Aesthetic Direction

- **Direction:** Calm industrial-utilitarian console; **blue** brand accent on
  neutral work surfaces
- **Decoration level:** Minimal. Hierarchy from type, space, and semantic color
- **Mood:** Serious software for serious work. Quiet chrome; clear readiness and
  severity signals
- **Craft:** Apple HIG foundations (accessibility, hierarchy, writing, sidebar
  grouping) on a web ops shell — principles apply; native macOS/iOS chrome does not
- **Signature:** Dark-first blue ops chrome + customer-question headline +
  evidence on every governed number

---

## Appearance

- **Default:** Dark (`data-theme="dark"` on the document root).
- **Optional switch:** Sidebar theme control for demo / ops preference.
- Both appearances must remain legible with Increase Contrast and Reduce
  Transparency in mind (solid chrome; no reliance on blur).

---

## Typography

- **UI / Body / questions:** `"IBM Plex Sans"` via `next/font` (`--font-sans`) —
  industrial ops face; Regular–Bold only (no thin weights — `typography.md`)
- **Mono / evidence / chart ticks:** `"IBM Plex Mono"` (`--font-mono`) with
  `font-variant-numeric: tabular-nums` on counts
- **Do not use** Inter / Roboto / system-ui as the primary UI face
- **Scale (match `globals.css`):**
  - Page / question title (`h1`): 30–34px / 1.2 / 650 / tracking −0.03em
  - Brand wordmark: ~16px / 600
  - Section title: 16–20px / 600
  - Body: 14px / 1.5 / 400
  - Meta / nav / controls: 12–13px
  - Eyebrow / caps: 11–12px / 700–800 / tracking ~0.1em

## Charts

- **Library:** D3 in `components/charts/`
- **Composition (Overview Financial health):** one stacked part-to-whole bar
  (cost + margin of earned revenue) with labeled legend — not a second KPI list
- **Data rule:** Only values present on the page payload — no synthetic time series
- **A11y:** `role="img"`, sentence `aria-label`, visually hidden data table; legend
  labels always accompany color swatches
- **Color:** CSS variables so theme switch updates marks; never color-only encoding
- **Motion:** brief ease-out enter; honor `prefers-reduced-motion`

---

## Color

**Approach:** Neutral surfaces + one **blue** accent + semantic readiness /
severity (always with text labels).

### Surfaces and text

| Token | Light | Dark |
| --- | --- | --- |
| `--np-bg` / `--canvas` | `#f5f7fc` | `#13151f` |
| `--np-bg-elevated` / `--panel` | `#ffffff` | `#1b1e2b` |
| `--np-bg-subtle` | `#edf0f7` | `#242839` |
| `--np-text` / `--ink` | `#202436` | `#f1f2fa` |
| `--np-text-secondary` | `#50596d` | `#c2c7d9` |
| `--np-text-muted` / `--muted` | `#667086` | `#9aa3bb` |
| `--np-border` / `--line` | `#e3e7f0` | `#2b3043` |
| `--np-border-strong` | `#cbd2e2` | `#414a63` |
| `--np-accent` / `--brand` | `#2563eb` | `#60a5fa` |
| `--np-accent-hover` | `#1d4ed8` | `#93c5fd` |
| `--np-accent-ink` / `--brand-ink` | `#1e40af` | `#bfdbfe` |
| `--np-accent-soft` / `--brand-soft` | `#eff6ff` | `#1e3a5f` |
| `--np-accent-line` / `--brand-line` | `#bfdbfe` | `#1e4a7a` |
| `--np-accent-mark` / `--brand-mark` | `#3b82f6` | `#60a5fa` |

Nav chrome (sidebar): dark elevated surface in both themes; active = soft accent
fill + accent-ink text + thin inset rail.

### Outcomes / severity

Use **text labels** with color. Never color alone (`color.md › Inclusive color`).

| Role | Soft / ink / mark |
| --- | --- |
| Live / complete / allow | `--live-soft`, `--live` |
| Warning | `--warn-soft`, `--warn-ink`, `--warn` |
| Critical / block | `--critical-soft`, `--critical` |
| Info | `--info-soft`, `--info` |

**Ink rule:** Saturated fills are for rails, large numbers, and marks. Anything
at 10–12px, and any solid fill carrying text, uses the ink / soft pair. Target
≥4.5:1 for normal text and ≥3:1 for large/bold text against its surface.

**`--np-on-accent`:** Text on accent fills — `#ffffff` in light, near-surface
dark ink in dark when accent is bright.

---

## Spacing

- **Base unit:** 4px
- **Density:** Comfortable ops density
- **Scale:** 4 / 8 / 12 / 16 / 20 / 24 / 32 / 48
- **Page padding:** ~32×38px desktop; tighten on small viewports
- **Max content width:** ~1500px (`.content`)

---

## Layout and IA

- **Shell:** One sticky sidebar (~230px) + main work area. No dual icon-rail.
- **IA groups** (match `SidebarNav.tsx`):

  | Group | Routes |
  | --- | --- |
  | **Attention** | Overview, Signals |
  | **Position** | Clients, Forecast, Workforce |
  | **Intelligence** | Scenario Planning, Ask Pulse, Onboarding, Administration |

- Narrow viewports (≤1000px): compact sticky top bar + Menu toggle; same
  Attention / Position / Intelligence groups when expanded — never hide section
  labels. Content leads; nav is progressive disclosure.
- **Radius:** controls ~8px; cards ~12–14px; avoid decorative mosaics.
- **Cards:** Elevated surface, 1px border, soft shadow. Cards for interaction and
  data grouping — never wrapping the question hero.

---

## Components

- **Primary button:** accent fill + on-accent text, radius ~8–9px
- **Secondary:** elevated surface + strong border
- **Nav active:** soft accent / deep navy fill + rail (blue)
- **Status / readiness:** Live · Rule validated · Preview — color + word
- **Signal cards:** severity text + left rail + sentence-case title
- **KPI / metrics:** tabular numbers; quality label; View evidence
- **Destructive / confirm:** in-interface patterns preferred over `window.confirm`
- **Hit targets:** desktop ~28px+; primary ~38–40px; close ≥34×34

---

## Motion

- **Approach:** Intentional / minimal-functional
- Hover lifts on journey cards ~120ms; no bounce theater
- **Respect:** `prefers-reduced-motion` → no transforms / transitions

---

## Writing

- Sentence-case signal titles (“Margin erosion”)
- Actions name the outcome: “View evidence”, “Continue demo →”
- No em dashes in UI copy
- Demo is question-led, not feature-led

---

## Anti-patterns (banned)

- Purple / violet / indigo **gradients** as content chrome
- Teal accent regressions from experimental redesigns
- Dual sidebar (icon rail + labeled nav)
- Color as the only status signal
- Decorative glass stacked on glass
- Three equal feature cards with icons-in-circles as the Overview hero
- Equating LIVE source readiness with “signal is firing”
- system-ui / Inter as the primary UI face (use IBM Plex via `next/font`)

---

## File map

- Tokens / chrome: `apps/web/app/globals.css`
- Fonts: `apps/web/app/layout.tsx`
- Shell / nav / theme: `AppShell.tsx`, `ShellFrame.tsx`, `SidebarNav.tsx`, `ThemeToggle.tsx`
- Cards: `MetricCard.tsx`, `SignalCard.tsx`, `QuestionHeader.tsx`
- Charts: `apps/web/components/charts/` (D3 horizontal bars)

---

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-09-15 | Indigo from `bef00f5` was temporary SoT | Matched then-shipped shell |
| 2026-09-16 | Blue accent + Zerobea-style console system | User: inspire from Zerobea DESIGN.md; follow blue; full UI update |
| 2026-09-16 | Dark-first + optional light switch | Ops-console default; demo preference control |
| 2026-09-16 | Soft/ink pairs for severity & brand | AA for small labels; marks stay vivid |
| 2026-09-16 | Keep Attention / Position / Intelligence IA | Shipping nav; HIG ≤2 sidebar levels |
| 2026-09-16 | CSS wins over DESIGN.md hex tables | Single runtime source of truth |
| 2026-09-16 | IBM Plex Sans / Mono replaces Inter | User: update font; industrial ops voice |
| 2026-09-16 | D3 overview charts (composition + severity) | User: add graphs with D3; Apple chart a11y |
| 2026-09-18 | Live UI aligned to DESIGN.md SoT | Tokens, IBM Plex, dark-first, grouped IA, ThemeToggle, login chrome, D3 bars |
| 2026-09-18 | Compact Menu toggle ≤1000px | Stacked full sidebar ate the fold; HIG: compact control when space is limited |
