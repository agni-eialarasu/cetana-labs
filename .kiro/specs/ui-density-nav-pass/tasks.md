# UI Density & Navigation Pass — Tasks

| Property | Value |
| :--- | :--- |
| **Spec ID** | `ui-density-nav-pass` · **Backlog** `BK-032` (`TSK-072`) · **Branch** `feat/ui-density-nav-pass` |

> Reference impl exists in the Antigravity clone (verified). Reproduce it on a clean `feat/` branch off merged-Spec `main`.

## Tasks

- [ ] **T1 — Type scale** (R1): add `theme.extend.fontSize` scale to `tailwind.config.js`; set `:root{font-size:16px}` + `body` 15px in `app.css`.
- [ ] **T2 — Micro-text sweep** (R1.3): replace every `text-[10px]`/`text-[11px]` across `ProjectCard.svelte`, `KpiCard.svelte`, and any card/pill/badge with `text-2xs`/`text-xs`. Grep `text-\[1[01]px\]` SHALL return zero after.
- [ ] **T3 — Header nav** (R2.1–R2.3): add route-aware pills (📊 Portfolio always; 📁 Projects / 👥 Developers / ⚙️ Settings `{#if auth.isAdmin}`) to `+layout.svelte` with active-state from `$page.url.pathname`.
- [ ] **T4 — Slim AdminNav** (R2.4–R2.5): reduce `AdminNav.svelte` to only the D-CRUD-1 divergence banner; remove the H1 + duplicate tab bar; confirm no route is orphaned.
- [ ] **T5 — Density sweep** (R3): page padding `py-8 lg:py-10`→`py-4 lg:py-5`; footer `mt-12 py-6`→`mt-6 py-3.5`; admin tables `py-3.5`→`py-2.5`; compact KPI bar / search / card gaps; `/admin/settings` stacked header → single-tier action bar.
- [ ] **T6 — Scope-floor check** (R4): confirm the diff touches NO `auth.svelte.ts`, `data/**`, `app/pocketbase/**`, rules, or `pb_schema.json`.
- [ ] **T7 — Self-validate**: `pnpm check` + `pnpm build` clean; `just validate-local` green (5 pillars + `--check` gates). Lockstep: CHANGELOG entry for TSK-072; keep SPRINT_TRACKER status coherent.
- [ ] **T8 — Open PR** against `main`; STOP-and-hold for `/verification-done` → `/review-pr`. Never merge.
