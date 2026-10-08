# UI Density & Navigation Pass — Design

| Property | Value |
| :--- | :--- |
| **Spec ID** | `ui-density-nav-pass` |
| **Backlog** | `BK-032` (`TSK-072`) |
| **Branch** | `feat/ui-density-nav-pass` |

## 1. Approach

Reference-implementation-first: the Antigravity session already produced and human-verified the target result (11-file diff, +243/−255 — net simplification from removing the duplicate nav). This design documents that proven shape so `/spec-run` reproduces it cleanly on a `feat/` branch off merged-Spec `main`, re-landing it on-protocol (the original build skipped merge-first).

Three cohesive, entangled changes shipped as ONE pass (they touch the same layout files, so splitting would create merge churn):

1. **Type scale** — a central Tailwind `fontSize` override + a 15px body / 16px root, then sweep component px-literals onto the tokens.
2. **Nav consolidation** — the header becomes the single nav owner (route-aware pills); `AdminNav` collapses to just the divergence banner.
3. **Density** — a consistent reduction of vertical padding, footer, table rows, and grid gaps.

## 2. File-by-file (matches the verified reference impl)

| File | Change |
| :--- | :--- |
| `app/web/src/app.css` | `:root{font-size:16px}`; `body` font-size 14→15px. |
| `app/web/tailwind.config.js` | Add `theme.extend.fontSize` scale (`2xs`…`3xl`, R1.2). |
| `app/web/src/routes/+layout.svelte` | Header owns route-aware nav pills (Portfolio always; Projects/Developers/Settings `{#if auth.isAdmin}`); active-state via `$page.url.pathname`. |
| `app/web/src/lib/components/AdminNav.svelte` | Strip the H1 + duplicate tab bar; keep ONLY the amber D-CRUD-1 divergence banner (−~160 lines). |
| `app/web/src/routes/+page.svelte` | Compact KPI bar / search / card-grid gaps; `py-8 lg:py-10`→`py-4 lg:py-5`. |
| `app/web/src/lib/components/ProjectCard.svelte` | Tighten internal spacing; micro-text `text-[10px/11px]`→`text-2xs/text-xs`. |
| `app/web/src/lib/components/KpiCard.svelte` | Same micro-text + spacing sweep. |
| `app/web/src/routes/admin/projects/+page.svelte` | Table `th/td py-3.5`→`py-2.5`. |
| `app/web/src/routes/admin/developers/+page.svelte` | Same table tightening. |
| `app/web/src/routes/admin/settings/+page.svelte` | Stacked multi-level header → compact single-tier action bar. |

## 3. Active-nav derivation

Active state is derived from `$page.url.pathname` (SvelteKit store) against each pill's `href` — a pill is active when the path matches its route (exact for `/`, prefix for admin sub-routes). No new store; purely layout-local.

## 4. Non-goals / risks

- **No auth change** — `auth.isAdmin` is *consumed* for the `{#if}` guards but NOT modified here (that's `BK-033`). The reference-impl's `auth.svelte.ts` edit is carved out into the separate Spec.
- **Risk: micro-text sweep misses a literal** — mitigated by a repo grep for `text-\[1[01]px\]` returning zero after the pass (part of V-plan/DoD).
- **Risk: active-pill logic mis-highlights nested routes** — mitigated by V2 clicking each route.

## 5. Executor

Antigravity (cost-first, pure frontend). The build reproduces the reference diff; it does not re-invent the layout.
