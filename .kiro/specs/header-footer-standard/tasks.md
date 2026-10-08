# Header/Footer Standardization — Tasks

| Property | Value |
| :--- | :--- |
| **Spec ID** | `header-footer-standard` |
| **Branch** | `feat/header-footer-standard` (self-created by the build; off up-to-date `main`) |
| **Work class** | **Sprint deliverable → FULL gate** (Spec → `/spec-run` → `/review-pr` scorecard → human merge). |
| **Execution** | **Antigravity Executor** (clone `cetana-labs-antigravity/`) — SvelteKit layout/markup refactor, cost-first default per `RFC-LAB-000-014`. Escalate to Kiro IDE only if theme/auth wiring proves deeper (record why). |
| **Kickoff** | `/spec-run header-footer-standard` |
| **EARS target** | R1–R5 in `requirements.md`; DoD = the V1–V7 Human Verification Plan. |

---

## T0 — Preflight + baseline (STOP on failure) → P1–P5
- [x] Surface = an Executor clone; `just start-local` brings up PocketBase + SvelteKit; Node/pnpm on PATH. *(P1)*
- [x] This Spec merged to `main` (merge-first). *(P3)*
- [x] `BK-012`/`BK-013` present on `main` — `SettingsAccessor` name/desc/logo getters exist. *(P5)*
- [x] Create `feat/header-footer-standard` off up-to-date `main`; clean tree; not `main`. *(P2)*
- [x] Baseline: `pnpm --dir app/web check && build` + 5 validators green. *(P4)*

## T1 — Header: branding + center-nav slot + auth → R1
- [x] In `+layout.svelte` header, render left: logo (guarded) + `settings.appName()` + a muted `settings.appDescription()` (`hidden sm:inline`). *(R1.1)*
- [x] Add an empty, styled center `<nav aria-label="Primary">` region (no links yet). *(R1.2)*
- [x] Keep `<AuthControl/>` right. *(R1.3)*

## T2 — Remove the duplicate "second row" → R2
- [x] In `+page.svelte`, remove the masthead branding block (logo + `<h1>` name + `<p>` description). *(R2.1)*
- [x] Remove the GitHub `<a>` from `+page.svelte`. *(R2.2)*
- [x] Remove `<ThemeToggle/>` + its import from `+page.svelte`. *(R2.3)*
- [x] Leave all dashboard content (stat cards, tabs, sort/search, grid) untouched.

## T3 — Footer: global theme + public Docs + GitHub → R3
- [x] Move `<ThemeToggle/>` into the `+layout.svelte` footer (single global instance); add its import there. *(R3.1)*
- [x] Keep the **Docs** link public (always shown, no auth gate) + the **GitHub** link (footer-only). *(R3.2 / D-HF-1)*
- [x] Keep lightweight footer branding (small logo + name). *(R3.3)*

## T4 — docs route cleanup → R4.4
- [x] Remove `<ThemeToggle/>` + its import from `docs/+page.svelte`; rely on the global footer toggle.

## T5 — Gates, lockstep, PR → R5
- [x] `pnpm --dir app/web check && build`, `just validate-local`, 5 validators green. *(R5.1)*
- [x] Scope floor held: only `+layout.svelte`, `+page.svelte`, `docs/+page.svelte`; no backend/`data`/schema/auth change. *(R5.2)*
- [x] Lockstep: `CHANGELOG.md` `[Unreleased]` entry (BK-027/TSK-068); flip `SPRINT_TRACKER.md` TSK-068 at build.
- [x] Append `REPORT.md` (summary + the V1–V7 Human Verification Plan, left for `/verification-done`).
- [x] Open PR `feat/header-footer-standard → main`; self-validate vs EARS DoD; STOP-and-hold (never merge).

## Post-build (back on the Operator)
- `/verification-done` (Executor) records V1–V7 PASS → IN_REVIEW.
- `/review-pr` (Operator) → FULL scorecard (sprint deliverable) → human squash-merge → BK-027 Done.
