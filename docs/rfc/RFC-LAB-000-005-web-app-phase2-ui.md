# RFC-LAB-000-005: Web App Phase 2 — Sleek UI (Read Parity) Scoping

| Property | Value |
| :--- | :--- |
| **RFC ID** | `RFC-LAB-000-005` |
| **Title** | Control Hub Web App — Phase 2 Frontend ("Sleek UI") Scoping |
| **Author** | Eialarasu (LAB-000 Control Hub) |
| **Status** | ✅ Accepted (Scoping — `BK-008` Phase 2; open questions resolved §9) |
| **Date** | 2026-09-24 |
| **Builds On** | `RFC-LAB-000-003` (PocketBase web app, §7 P2), `RFC-LAB-000-002` (data layer), `RFC-LAB-000-004` (branch model) |
| **Precedes** | Phase 3 (Auth & RBAC / `BK-007`) |

---

## 1. Purpose & Scope

Scope the **Phase 2** frontend: a **"Sleek UI" single-page app** that reaches **read-only feature parity** with the current static dashboard (`docs/index.html`) but is driven by the **PocketBase** backend stood up in Phase 1 (`app/pocketbase/`), instead of build-time-generated HTML.

**In scope:** frontend framework decision, app architecture, data-access pattern against PocketBase, parity checklist, dual-run/deploy story, project structure, phased build steps.
**Out of scope (this RFC / phase):** authentication & RBAC (Phase 3), any write/edit path (Phase 4), telemetry charts (Phase 5).

## 2. Decision Summary

1. **Framework: SvelteKit in static-SPA mode** (`@sveltejs/adapter-static`, `ssr = false`).
2. **Data access: client-side via the official PocketBase JS SDK** — PocketBase is explicitly designed to be consumed directly from a browser SPA; server-side rendering is avoided in Phase 2 to sidestep shared-instance, OAuth2, and realtime-proxying complexity flagged by the PocketBase team. _Content was rephrased for compliance with licensing restrictions._
3. **Deployment: static build served from PocketBase's `pb_public/`** (single binary serves API + UI), with the same build also deployable to GitHub Pages during dual-run.
4. **Scope: read-only parity** with `docs/index.html`; no auth gate yet (public read, matching today's public dashboard).

## 3. Framework Rationale

Evaluated SvelteKit, React (Vite), and Vue for a **small, single-view executive dashboard**.

| Criterion | SvelteKit (static) ✅ | React + Vite | Vue + Vite |
| :--- | :---: | :---: | :---: |
| Bundle size / cold-load (exec dashboard) | **Smallest** (compiler, no VDOM) | Larger | Medium |
| Fit for a compact SPA | **Excellent** | Good (heavier) | Good |
| PocketBase integration maturity | **Strong** (multiple current starters/stores) | Strong | Good |
| Static hosting parity with today's model | **Native** (`adapter-static`) | Native | Native |
| Keeps "cheap static file" property | **Yes** | Yes | Yes |

**Why SvelteKit:** the current dashboard's core value is a fast, lightweight, static, single-view executive page. Svelte's compile-to-vanilla-JS model produces the smallest, fastest bundle for that profile, and its PocketBase ecosystem is well-trodden. It also preserves the property we already rely on — a cheap static artifact that can sit on GitHub Pages or in `pb_public/`. React/Vue are fine but heavier than this problem warrants.

> **Not a lock-in risk:** the app is a thin read client over PocketBase's REST API; the data contract (collections from `RFC-LAB-000-002`) is framework-agnostic, so a future reskin is low-cost.

## 4. Architecture

```text
┌───────────────────────────────────────────────┐
│  SvelteKit static SPA  (app/web/)               │
│   • PocketBase JS SDK (client-side)             │
│   • routes: / (dashboard)                       │
│   • components: KPI bar, filters, project cards │
│   • theme toggle (System/Light/Dark) — ported   │
└───────────────────────────────────────────────┘
        │  REST (list/filter/expand relations)
        ▼
┌───────────────────────────────────────────────┐
│  PocketBase (Phase 1)  — projects, users,       │
│  memberships;  serves pb_public/ static build   │
└───────────────────────────────────────────────┘
```

- **`app/web/`** — SvelteKit project (sibling to `app/pocketbase/`).
- **Data:** `pb.collection('projects').getFullList({ expand: 'owner' })` etc.; owner name via the `expand` on the relation (no more regex). Realtime subscriptions are available but **deferred** (not needed for read parity).
- **No secrets in the client** — Phase 2 reads public collections only; the auth gate arrives in Phase 3.

## 5. Read-Parity Checklist (vs. `docs/index.html`)

The Phase 2 UI must replicate, from PocketBase data:
- [ ] KPI bar (Active / Hard Blockers / Onboarding / Completed / Total)
- [ ] Tab filters (Active / All / Onboarding / Completed / Control Hub)
- [ ] Executive-priority sort + Recently-Updated + Project ID sort
- [ ] Text search (name, owner, id)
- [ ] Project cards: **owner pill** (top-left), health pill, archetype, pitch, wins/focus, blocker banner
- [ ] Onboarding-pending alert + On-board Prompt copy
- [ ] Copy WhatsApp digest / per-project briefing
- [ ] System / Light / Dark theme toggle (ported palette)

> **Data dependency:** cards' *live* fields (health, wins, focus, blockers) still originate from `STATUS.md` until Phase 4. For Phase 2, these are served via a read endpoint that surfaces the current `data/` + parsed status (interim), or a lightweight `status_snapshots` seed — decided at build start (§7 step 2).

## 6. Deployment & Dual-Run

- **Primary:** `npm run build` → static assets copied into PocketBase `pb_public/`; the single binary serves both UI and API (idiomatic PocketBase).
- **Dual-run:** the existing generated `docs/index.html` (from `generate_dashboard.py`) remains the public GitHub Pages dashboard until the SvelteKit app reaches parity and a host is chosen (`RFC-LAB-000-003` §6). No hard cutover.
- **CI:** add a build/lint job for `app/web/` to the `pull_request` workflow (Node); keep it separate from the Python validators. App code lands via PRs per `RFC-LAB-000-004`.

## 7. Phased Build Steps (Phase 2)

1. **Scaffold** `app/web/` — SvelteKit + `adapter-static`, PocketBase JS SDK, base layout & theme tokens ported from `docs/index.html`.
2. **Data access** — decide the read source for live status fields (interim status endpoint vs. seed `status_snapshots`); implement a typed `pb` client + fetch layer.
3. **Components** — KPI bar, filter tabs, sort, search, project card (owner pill parity).
4. **Parity pass** — tick the §5 checklist against the current dashboard.
5. **Build → `pb_public/`**; add the Node CI job; open PR.

## 8. Risks & Mitigations

| Risk | Mitigation |
| :--- | :--- |
| New Node toolchain in a Python-centric repo | Isolate under `app/web/`; separate CI job; Python validators untouched. |
| Live status fields not yet in DB (pre-Phase 4) | Interim read source (§6/§7 step 2); full migration is Phase 4. |
| Framework second-guessing later | Thin read client over a framework-agnostic REST contract; low reskin cost. |
| Scope creep into auth/write | Hard phase boundary: Phase 2 is **read-only, no auth**. |

## 9. Resolved Decisions (open questions closed)

1. **Live-status read source → interim `data/status.json` export.** A script reuses the existing `generate_status.py` parser to emit a committed `data/status.json` snapshot; the SPA reads structural data from PocketBase and live status (health/wins/focus/blockers/metrics) from `status.json`. `STATUS.md` remains canonical until Phase 4; the JSON shape previews the future `status_snapshots` collection.
2. **Hosting → split hosting (committed target).** SvelteKit static UI on **GitHub Pages** (free, public, unchanged); **PocketBase on a lightweight container host** (Fly/Railway/Render-class) with a persistent SQLite volume. Requires CORS config (UI origin → PB origin). Phase 2 dev runs against Codespaces/local PocketBase; the container host is finalized at deploy time.
3. **Framework version → Svelte 5 (Runes) + pnpm.** Greenfield app on the current, on-default SvelteKit (`$state`/`$derived` suit the filter/sort/search state); **pnpm** is the package manager (`pnpm-lock.yaml` committed; CI uses `pnpm install --frozen-lockfile`).
4. **Styling → adopt the org design system (Nexus Pulse), Tailwind-based.** [`docs/DESIGN.md`](../DESIGN.md) is the authoritative visual SoT (verbatim); [`docs/design-system-lab000.md`](../design-system-lab000.md) maps it to SvelteKit + Tailwind. Blue accent, IBM Plex Sans/Mono, dark-first, `--np-*` tokens, sm/md/lg responsive; banned anti-patterns enforced.

> These supersede the framework-agnostic styling assumption in §2/§3; the SvelteKit static-SPA + client-side PocketBase SDK decisions stand, now styled by the org design system with Tailwind mapping the `--np-*` tokens.
