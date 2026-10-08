# UI Density & Navigation Pass — Requirements

| Property | Value |
| :--- | :--- |
| **Spec ID** | `ui-density-nav-pass` |
| **Feature** | A cohesive design-system pass over the Sleek UI: a comfortable typography scale at 100% zoom, unified header navigation (route-aware pills), and tighter vertical density across pages/cards/admin tables. Visual/UX only — no data, schema, rule, or auth-behavior change. |
| **Backlog** | `BK-032` (`TSK-072`, SPRINT-13) |
| **Work class** | **Sprint deliverable** (product UI a user exercises) → **FULL gate**: Spec → `/spec-run` → `/review-pr` scorecard → human merge. |
| **Depends on** | `BK-027` (global header/footer + empty center-nav slot — merged `#71`), `BK-031` (App Settings UI — merged `#78`), `BK-014` (admin CRUD routes + `AdminNav` — merged `#80`). |
| **RFCs** | `RFC-LAB-000-005` (Sleek UI design system). |
| **Executor role** | **Antigravity** (cost-first per `RFC-LAB-000-014`) — pure SvelteKit/Tailwind/CSS, no backend/rules/auth. |
| **Source** | Operator session 2026-10-08. **Reference implementation already built & human-verified in the Antigravity clone** (11-file diff, +243/−255); this Spec documents the proven result so `/spec-run` re-lands it on-protocol (merge-first). |

---

## 1. Introduction

The Sleek UI shipped BK-027 (header/footer), BK-031 (settings editor) and BK-014 (admin CRUD) in rapid succession. The result is correct but visually loose: the base type is small enough to invite 150% browser zoom, navigation is split between the header and a per-page `AdminNav` tab bar, and vertical padding/footer/table spacing waste screen real estate. This Spec is a single **density & nav polish pass** that makes the app comfortable and sharp at 100% zoom, consolidates navigation into the sticky header, and raises information density — without touching behavior.

This is explicitly a **cosmetics/UX pass**. The companion auth change (reactive `is_admin` + `authRefresh()` on rehydrate) is **out of scope** — it is a different risk class (auth path) and ships under its own Spec `auth-live-refresh` (`BK-033`) on the Kiro IDE executor. Keeping them separate prevents an auth change riding inside a cosmetics PR.

## 2. Current-state facts (verified 2026-10-08 on `main`)
- **`app/web/src/app.css`** — `body { font-size: 14px; line-height: 1.5 }`; no explicit `:root` font-size.
- **`app/web/tailwind.config.js`** — `theme.extend` has `fontFamily` + `maxWidth.content` but **no `fontSize` scale override** (Tailwind defaults in use).
- **`app/web/src/routes/+layout.svelte`** — sticky global header (BK-027) with an empty center-nav slot; footer with theme toggle / Docs / GitHub.
- **`app/web/src/lib/components/AdminNav.svelte`** — currently renders a System-Administration H1 + a duplicate nav tab bar (Projects/Developers/Settings) **and** the D-CRUD-1 divergence banner. The tab bar duplicates what the header should own.
- **Micro text** — `text-[10px]` / `text-[11px]` literals appear across cards, pills, badges.
- **Spacing** — pages use `py-8 lg:py-10`; footer `mt-12 py-6`; admin tables `th/td py-3.5`.

## 3. Requirements (EARS acceptance criteria = Definition of Done)

### R1 — Typography scale (comfortable at 100% zoom)
- **R1.1** `app.css` SHALL set `:root { font-size: 16px }` and `body { font-size: 15px; line-height: 1.5 }`.
- **R1.2** `tailwind.config.js` `theme.extend.fontSize` SHALL define the scale: `2xs` 0.75rem, `xs` 0.84375rem, `sm` 0.9375rem, `base` 1.03125rem, `lg` 1.1875rem, `xl` 1.375rem, `2xl` 1.625rem, `3xl` 2rem (each with its paired line-height).
- **R1.3** All `text-[10px]` / `text-[11px]` literal utilities across cards/pills/badges SHALL be replaced with the scale tokens (`text-2xs` / `text-xs`) — no hardcoded px font sizes remain in components.
- **R1.4** WHEN the app is viewed at 100% browser zoom, the UI SHALL be legible without requiring 150% zoom (verified by human in the V-plan).

### R2 — Unified navigation in the header
- **R2.1** The global header (`+layout.svelte`) SHALL own the primary navigation as route-aware pills: `📊 Portfolio`, `📁 Projects`, `👥 Developers`, `⚙️ Settings`.
- **R2.2** The active route's pill SHALL show an active state (highlight), derived from the current path.
- **R2.3** The admin nav entries (`Projects`, `Developers`, `Settings`) SHALL render **only when `auth.isAdmin`** (BK-031 behavior) — the public `Portfolio` entry always shows. For a non-admin the admin pills do not appear.
- **R2.4** `AdminNav.svelte` SHALL be reduced to **only** the D-CRUD-1 divergence banner (amber, shown when live DB state is unreconciled). The duplicate nav tab bar and the generic "System Administration" H1 SHALL be removed.
- **R2.5** No navigation target SHALL be lost in the consolidation — every route previously reachable via `AdminNav` is reachable via the header.

### R3 — Spacing & information density
- **R3.1** Vertical page padding SHALL be reduced from `py-8 lg:py-10` to `py-4 lg:py-5` across pages.
- **R3.2** Footer spacing SHALL be reduced from `mt-12 py-6` to `mt-6 py-3.5`.
- **R3.3** Admin table rows (`th`/`td`) in `/admin/projects` and `/admin/developers` SHALL tighten from `py-3.5` to `py-2.5`.
- **R3.4** The KPI bar, search controls, and card-grid gaps (`+page.svelte`, `ProjectCard.svelte`, `KpiCard.svelte`) SHALL be compacted consistently.
- **R3.5** The `/admin/settings` page SHALL replace its stacked multi-level header with a compact single-tier action bar.

### R4 — Scope floor (what this must NOT touch)
- **R4.1** This Spec SHALL NOT modify `app/web/src/lib/auth.svelte.ts` (auth behavior is `auth-live-refresh`/`BK-033`), any `data/**`, `app/pocketbase/**`, PocketBase rules, or `pb_schema.json`.
- **R4.2** No functional behavior (sign-in, CRUD, settings write, divergence detection) SHALL change — only type scale, nav layout, and spacing.

## 4. Human Verification Plan (the `/review-pr` evidence)
- **V1** — At 100% browser zoom, the whole app (portfolio, cards, admin tables) is comfortably legible; no urge to zoom to 150%. (R1)
- **V2** — Signed in as **admin**: header shows all four pills; the active route's pill is highlighted; clicking each reaches the right page. (R2.1–R2.2)
- **V3** — Signed in as a **non-admin** (or signed out): only `Portfolio` shows; no `Projects/Developers/Settings` pills; admin routes still server-gated. (R2.3)
- **V4** — On an admin page, `AdminNav` shows ONLY the divergence banner when live DB diverges from `data/`; no duplicate tab bar, no "System Administration" H1. (R2.4)
- **V5** — Pages, footer, and admin tables are visibly tighter (more content per screen) with no clipping/overlap at common widths. (R3)
- **V6** — `just validate-local` green (5 pillars + `--check` gates); `pnpm build` + `pnpm check` clean. No `auth.svelte.ts`/backend/`data/` files in the diff. (R4)
