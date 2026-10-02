# In-App Docs View — Requirements

| Property | Value |
| :--- | :--- |
| **Spec ID** | `bk024-in-app-docs` |
| **Feature** | Surface the **consumer-facing** docs inside the deployed Sleek UI — a footer link → a `/docs` Help/About view — so leads & leadership read "how this works" without going to GitHub |
| **Backlog** | `BK-024` (Platform/DX, P3) — `TSK-TBD` |
| **Status** | 🟡 Proposed / DRAFT (authored on KiroCrew Operator; execution on Kiro IDE Executor) |
| **RFCs** | `RFC-LAB-000-005` (UI / static SPA), `RFC-LAB-000-011` (deploy: Vercel+Railway), `RFC-LAB-000-004` (branching) |
| **Pairs with** | `BK-013` (Branding & White-Labeling — footer/about placement) |
| **Executor role** | Delegated-agent / onboarded-dev |

---

## 1. Introduction

The deployed Sleek UI (`cetana-labs.vercel.app`) shows the live portfolio, but a lead or leadership member who wants to understand **how this works** must leave the app and read markdown on GitHub. The repo's docs are the single source of truth, yet none of them are reachable from the product itself.

**Fix:** add a **`/docs` Help/About view** inside the SvelteKit SPA, reachable from a **footer link**, that renders an **audience-filtered** subset of the repo docs — the ones written *for* leads/leadership. The markdown is imported at **build time** by a Vite step (git stays the single source of truth; no PocketBase changes; no DB-copy drift).

**Audience filter (authoritative — NOT all docs):**
- **INCLUDE:** `docs/guides/user-guide.md` (User Guide) + `docs/guides/project-owner-guide.md` (Project Owner Guide).
- **OPTIONAL third:** `docs/governance/ai-collaboration-model.md` (AI Collaboration Model) as a "how we build this" link.
- **EXCLUDE:** all contributor/internal docs — RFCs (`docs/rfc/*`), Decision Journal (`docs/governance/DECISION-JOURNAL.md`), project-protocol, DESIGN / design-system, capability-map, developer-guide, sprint-lifecycle.

**Caveats this Spec must handle:** the docs open with a **breadcrumb nav line** (`docs/README.md` navigation standard) and contain **relative repo links** (`../../README.md`, `../README.md`, cross-doc `.md` links) — neither resolves in-app and both must be stripped or rewritten. And a doc shown in-app **becomes a consumer surface**: a future edit now carries UX impact, which must be recorded as a governance consequence.

**This is a frontend/DX feature** — adds a `/docs` route + a build-time markdown step under `app/web/`; it touches **no** `data/`, **no** PocketBase schema, **no** migrations.

## 0. Preconditions (preflight — enforced by `tasks.md` T0)
- **P1 — Surface:** Kiro IDE/local (Executor clone `cetana-labs-kiro-ide/`); Node + pnpm on PATH (Homebrew).
- **P2 — Branch:** `feat/bk024-in-app-docs` off up-to-date `main`; clean tree; not `main`. **Created by `/spec-run`, not by the author.**
- **P3 — Merge-first:** this Spec merged to `main` before `/spec-run` (Definition of Ready, `RFC-LAB-000-010` §5).
- **P4 — Baseline green:** `pnpm --dir app/web install` + `pnpm --dir app/web build` succeeds on a clean checkout.

## 2. Current-state facts (verified)
- **Stack:** SvelteKit 5 (Runes) + pnpm + Tailwind + `@sveltejs/adapter-static` with SPA fallback (`fallback: 'index.html'`), under `app/web/` (`app/web/svelte.config.js`, `app/web/package.json`). Deployed on Vercel (`RFC-LAB-000-011`).
- **Routing:** file-based under `app/web/src/routes/`; existing routes include `/` (`+page.svelte`), `(member)/account`, `oauth/callback`. A new `/docs` route is a sibling `src/routes/docs/`.
- **Existing build-time data step precedent:** `app/web/scripts/copy-data.js` runs on `predev`/`prebuild` and copies `../../../data/*.json` into `static/data/`, warning (not failing) on a missing file. A docs-import step follows the same precedent.
- **Breadcrumb standard:** every doc under `docs/` (except `rfc/*`, `templates/*`) opens with a line like `[🏠 Cetana Labs](../../README.md) / [📚 Docs](../README.md) / <Category> / **This Doc**` (`docs/README.md` §Navigation standard). The included guides and the AI Collaboration Model all carry it.
- **Relative repo links:** the docs link to repo files via relative paths (e.g. `[`BACKLOG.md`](../../BACKLOG.md)`, `[Decision Journal](DECISION-JOURNAL.md)`). These are repo-relative and do not resolve under an app route.
- **No markdown renderer is currently a dependency** — current `dependencies` are `pocketbase` + `@fontsource/*` only. A renderer (and/or a build-time transform) is a new, scoped addition.
- There is a footer/about area owned by `BK-013` branding; this Spec adds the **link target** and a minimal link, and defers the branded footer chrome to `BK-013`.

## 3. Requirements (EARS acceptance criteria = DoD)

### R1 — The `/docs` route renders the audience-filtered doc set
- **R1.1** The SPA SHALL expose a `/docs` route that renders the **included** docs (User Guide + Project Owner Guide; AI Collaboration Model if the optional third is adopted) as HTML.
- **R1.2** WHEN a reader opens `/docs`, THEN the view SHALL present a navigable index of the included docs (a doc picker / section list) and render the selected doc's content.
- **R1.3** The route SHALL render **only** the allow-listed docs; it SHALL NOT surface any excluded contributor/internal doc (RFCs, Decision Journal, project-protocol, DESIGN, capability-map, developer-guide, sprint-lifecycle), even transitively via a link.
- **R1.4** The rendered content SHALL be styled consistently with the Sleek UI (Tailwind typography), readable on both light and dark themes.

### R2 — A footer / nav link reaches it
- **R2.1** The app SHALL present a **footer (or nav) link** labeled for a consumer audience (e.g. "Docs" / "Help" / "About") that navigates to `/docs`.
- **R2.2** WHEN a reader clicks that link from any route, THEN the app SHALL route to `/docs` via client-side navigation (no full reload beyond the SPA fallback).

### R3 — Build-time import (no runtime fetch, no PocketBase)
- **R3.1** The included markdown SHALL be imported/rendered at **build time** (a Vite mechanism — e.g. `import.meta.glob` with `?raw`, or a prebuild transform), so the content is baked into the bundle.
- **R3.2** The `/docs` view SHALL NOT perform a **runtime fetch** of the markdown and SHALL NOT read from **PocketBase**; git remains the single source of truth.
- **R3.3** The build-time import SHALL read from the repo's `docs/` tree (the canonical source), consistent with the `copy-data.js` precedent — no second hand-maintained copy of the doc bodies.

### R4 — Breadcrumb-nav + relative-repo-link stripping / rewriting
- **R4.1** WHEN a doc is prepared for in-app rendering, THEN the leading **breadcrumb line** (the `[🏠 Cetana Labs](…) / [📚 Docs](…) / … / **This Doc**` navigation standard) SHALL be stripped so it does not render in-app.
- **R4.2** WHEN a doc contains a **relative repo link** (e.g. `../../README.md`, `../README.md`, a cross-doc `*.md` link), THEN that link SHALL be either rewritten to a resolvable target (an in-app `/docs` section link for an included doc, or an absolute GitHub URL for an out-of-app target) OR rendered as plain non-broken text — it SHALL NOT render as a dead in-app `href`.
- **R4.3** A link to another **included** doc SHALL resolve to that doc's in-app `/docs` section; a link to an **excluded** or out-of-app target SHALL resolve to its canonical GitHub location (absolute URL) rather than a dead relative path.

### R5 — Graceful handling of a missing / renamed source doc at build
- **R5.1** WHEN an allow-listed source doc is missing or renamed at build time, THEN the build step SHALL **fail loudly with the offending path** (preferred for an allow-list, so a silently-dropped consumer doc is impossible) OR, if a non-fatal policy is chosen, SHALL emit a clear warning naming the missing path and omit only that doc — the chosen policy SHALL be stated in `design.md` and SHALL NOT crash the whole app render.
- **R5.2** The allow-list SHALL be a single, explicit, reviewable list (one place to add/remove a doc), so expanding the in-app doc set is a deliberate, visible change.

### R6 — "Doc is now a consumer surface" governance consequence
- **R6.1** `docs/governance/ai-collaboration-model.md` SHALL record that an in-app doc is a **consumer surface**: editing an included doc now carries UX/product impact (it changes what leads/leadership see in the product), so such edits are reviewed with that consequence in mind.
- **R6.2** The allow-list location (R5.2) SHALL carry an inline note pointing at that governance consequence, so a future contributor adding a doc sees the implication at the point of change.

### R7 — Docs & lockstep
- **R7.1** `CHANGELOG.md` `[Unreleased]` SHALL carry an entry; `BACKLOG.md` `BK-024` row and `SPRINT_TRACKER.md` SHALL be updated to reflect the Spec/track state (per structure.md lockstep).
- **R7.2** The lockstep update (CHANGELOG / SPRINT_TRACKER note) SHALL happen as part of the build task set (see `tasks.md` final task), not as an afterthought.

### R8 — No regression / scope containment
- **R8.1** The change SHALL be confined to `app/web/` (plus the lockstep doc edits in R7) — **no** `data/` change, **no** PocketBase schema/migration, **no** change to the auth flow or the public dashboard.
- **R8.2** The existing `pnpm --dir app/web build` + `pnpm --dir app/web check` SHALL remain green with the `/docs` route and the build-time step added.

## 4. Out of scope
- **Logo / branding / footer chrome UI** — that is `BK-013` (this Spec adds only the link target + a minimal link).
- **Any DB-stored copy of the docs** — no PocketBase collection, no runtime fetch (R3.2).
- **Rendering excluded/internal docs** (RFCs, Decision Journal, developer-guide, etc.) — explicitly filtered out (R1.3).
- **In-app editing of docs** — the docs remain git-authored; `/docs` is read-only.
- **Search / full-text indexing** over the docs — a possible later enhancement, not this Spec.

## 5. Human Verification Plan
*(Experiential, human-executable — kept DISTINCT from the EARS criteria above. Run on the built site, not just dev.)*

1. **Build & load** — run `pnpm --dir app/web build` then `pnpm --dir app/web preview` (or load the deployed bundle); open `/docs`. The page loads with no console error. *(exercises R1, R3)*
2. **Footer link** — from the home dashboard, click the footer "Docs/Help/About" link → lands on `/docs` without a broken navigation. *(R2)*
3. **User Guide renders clean** — open the User Guide section; confirm it renders as formatted HTML, **no breadcrumb line at the top**, and **no broken relative links** (hover a former `../../README.md`-style link → it either points at GitHub, an in-app section, or is plain text — never a dead in-app URL). *(R4)*
4. **Project Owner Guide renders** — switch to the Project Owner Guide section; it renders (including its mermaid/flow content as at least readable text, not a crash). *(R1.2)*
5. **Audience filter holds** — confirm there is **no** way to reach an RFC, the Decision Journal, or the developer-guide from `/docs`. *(R1.3)*
6. **Missing-doc behavior** — (dev check) temporarily rename an allow-listed source doc and re-run the build: confirm the build **fails loudly naming the path** (or warns + omits per the chosen policy), rather than silently shipping an empty section. Restore the file. *(R5.1)*
7. **Theme** — toggle light/dark; the docs remain readable in both. *(R1.4)*
8. **Governance note present** — confirm `ai-collaboration-model.md` now states the in-app-doc = consumer-surface consequence, and the allow-list carries the inline pointer. *(R6)*
