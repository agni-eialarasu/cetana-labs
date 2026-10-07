# Header/Footer Standardization — Requirements

| Property | Value |
| :--- | :--- |
| **Spec ID** | `header-footer-standard` |
| **Feature** | Consolidate the app chrome to a standard webapp **header + footer**: branding + a center-nav slot + auth in the header; theme toggle + public Docs + GitHub in the footer. Remove the duplicate branding "second row" from the dashboard page. |
| **Backlog** | `BK-027` (`TSK-068`, SPRINT-13) |
| **Work class** | **Sprint deliverable** (product UI a user exercises) → **FULL gate**: Spec → `/spec-run` → `/review-pr` scorecard → human merge. |
| **RFCs** | `RFC-LAB-000-013` (settings — drives name/desc/logo), `BK-024` (public `/docs` view), `RFC-LAB-000-008` (auth state) |
| **Consumes** | `BK-012`/`BK-013` settings + `SettingsAccessor` (name/desc/logo getters), the existing `ThemeToggle` + `AuthControl` components |
| **Executor role** | Default **Antigravity** (cost-first per `RFC-LAB-000-014`) — SvelteKit layout/markup refactor, no new backend/data; escalate to Kiro IDE only if the theme/auth wiring proves deeper (record why). |
| **Source** | Operator session 2026-10-07 — user-reported UI cleanup after local testing of v0.14.0. |

---

## 1. Introduction

The current chrome duplicates branding and scatters controls. The global header (`+layout.svelte`) renders logo + app name; the dashboard page (`+page.svelte`) renders a **second** block repeating the name + description, **plus** a theme toggle and a GitHub link that is *also* in the footer. The result is a redundant "second row" and controls in inconsistent places (the theme toggle lives on `+page.svelte` AND `docs/+page.svelte`, not globally).

This Spec standardizes to conventional webapp **header + footer**:
- **Header (global, `+layout.svelte`):** app **name + description** (left) · a **center navigation slot** (empty now; ready for future web-app routes) · **auth control** (right).
- **Footer (global, `+layout.svelte`):** the **theme toggle** (moved here, global/single) · **Docs** (public) · **GitHub**.
- **Dashboard page (`+page.svelte`):** the duplicate branding/theme/GitHub "second row" is **removed**; only the dashboard content (stat cards, tabs, project grid) remains.

**Decisions (recorded):**
- **D-HF-1 — Docs stays PUBLIC.** The Docs link remains reachable pre-login, honoring `BK-024`'s consumer-facing intent and standard practice (docs are the one surface you want reachable without auth). *(An earlier idea to gate Docs behind login was considered and rejected — it would reverse BK-024 and is non-standard.)*
- **D-HF-2 — Theme toggle is GLOBAL (footer), single instance.** Removes the two per-page copies (`+page.svelte`, `docs/+page.svelte`) in favour of one in the shared footer.
- **D-HF-3 — Center-nav slot ships EMPTY.** No links wired until real web-app routes exist. The chat-only `/rgs` skill is NOT linked here (it would 404 in the browser).

## 0. Preconditions (preflight — enforced by `tasks.md` T0)
- **P1 — Surface/toolchain:** an Executor clone; local PocketBase + SvelteKit for verification (`just start-local`); Node/pnpm.
- **P2 — Branch:** `feat/header-footer-standard` off up-to-date `main`; clean tree; not `main`.
- **P3 — Merge-first:** this Spec merged to `main` before `/spec-run`.
- **P4 — Baseline green:** `pnpm --dir app/web check && build` + the 5 validators.
- **P5 — Depends on merged `BK-012`/`BK-013`:** the `SettingsAccessor` name/desc/logo getters exist (they do, PR #64/#66).

## 2. Current-state facts (verified 2026-10-07 on `main`)
- `+layout.svelte` header: `<a>` with logo (`logoSmallUrl`‖`logoIconUrl`) + `{appName()}` (left), `<AuthControl/>` (right). Footer: logo+name, Docs link, GitHub link.
- `+page.svelte` masthead (`~line 53–78`): logo + `<h1>{appName()}</h1>` + `<p>{appDescription()}</p>`, then `<ThemeToggle/>` + a GitHub `<a>`.
- `ThemeToggle` imported in BOTH `+page.svelte:70` and `docs/+page.svelte:32`.
- Branding getters: `settings.appName()`, `settings.appDescription()`, `settings.logoSmallUrl()/logoIconUrl()/logoMediumUrl()`.

## 3. Requirements (EARS acceptance criteria = Definition of Done)

### R1 — Header: branding + center nav + auth (`+layout.svelte`)
- **R1.1** The header SHALL render, left-aligned: the logo (when a logo URL is set) + `settings.appName()` + `settings.appDescription()` (description as a muted inline/subtitle beside or under the name). It links to `base/`.
- **R1.2** The header SHALL include a **center navigation region** (a `<nav>`), **empty of links in this Spec** but structurally present + styled, so future routes drop in without a re-layout.
- **R1.3** The header SHALL keep `<AuthControl/>` right-aligned.
- **R1.4** The header SHALL be the ONLY place app name + description render in the global chrome (no duplication on the page).

### R2 — Remove the duplicate "second row" (`+page.svelte`)
- **R2.1** The dashboard masthead SHALL NOT render the app name, description, or logo (those live in the header now, R1.4). The portfolio content (stat cards, tabs, filters, grid) is unchanged.
- **R2.2** The GitHub link SHALL be removed from `+page.svelte` (it lives in the footer only, R3.2).
- **R2.3** The `<ThemeToggle/>` SHALL be removed from `+page.svelte` (moved to the footer, R3.1).

### R3 — Footer: theme + public docs + GitHub (`+layout.svelte`)
- **R3.1** The footer SHALL contain the **single global** `<ThemeToggle/>`, removed from both `+page.svelte` and `docs/+page.svelte` (D-HF-2).
- **R3.2** The footer SHALL contain a **Docs** link (`base/docs`) that is **public** (always shown, no auth gate — D-HF-1) and a **GitHub** link (footer is the only place GitHub appears).
- **R3.3** The footer SHALL keep lightweight branding (small logo + name) consistent with current.

### R4 — No regression / consistency
- **R4.1** With a logo set (BK-013), the logo still renders in the header; with none, text-only — no broken image, no layout shift.
- **R4.2** `settings.appName()`/`appDescription()` still drive all branding text (no hardcoding).
- **R4.3** Theme switching still works from the footer across all routes (dashboard + `/docs`); the chosen theme persists (existing `theme.svelte` behavior unchanged).
- **R4.4** `docs/+page.svelte` SHALL still function with its ThemeToggle removed (relies on the global footer toggle).

### R5 — Quality gates / scope floor
- **R5.1** `pnpm --dir app/web check && build`, `just validate-local`, 5 validators green.
- **R5.2** Scope floor: `+layout.svelte`, `+page.svelte`, `docs/+page.svelte` (ThemeToggle removal) ONLY. **No** backend/`data/`/schema change, **no** new settings keys, **no** auth-logic change.

## 4. Out of scope
Actual nav links / new routes (the slot ships empty); any Stage B RGS UI; restyling the dashboard content itself; new settings; auth changes.

## 4b. Human Verification Plan (emitted by `/spec-run`; recorded by `/verification-done`)
On the local stack (`just start-local`):
- **V1 — single branding:** app name + description appear ONLY in the header; the dashboard page shows no duplicate name/desc/logo block (R1.4/R2.1).
- **V2 — header layout:** name+desc left, empty center-nav region present, auth right; renders cleanly at desktop + narrow widths (R1).
- **V3 — footer theme:** the theme toggle is in the footer, switches theme, and works on BOTH the dashboard and `/docs` (R3.1/R4.3/R4.4).
- **V4 — Docs public:** the Docs link shows and resolves **while signed out** (R3.2/D-HF-1).
- **V5 — GitHub single:** GitHub link appears only in the footer, not the page body (R2.2/R3.2).
- **V6 — logo/no-logo:** with a logo set it renders in the header; with none, text-only, no layout shift (R4.1).
- **V7 — gates:** `pnpm check && build` + validators green (R5.1).
