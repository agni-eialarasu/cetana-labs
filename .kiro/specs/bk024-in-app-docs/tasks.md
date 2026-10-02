# In-App Docs View — Tasks

| Property | Value |
| :--- | :--- |
| **Spec ID** | `bk024-in-app-docs` |
| **Branch** | `feat/bk024-in-app-docs` (self-created by `/spec-run`) |
| **Execution** | Kiro IDE Executor (clone `cetana-labs-kiro-ide/`) via `/spec-run bk024-in-app-docs` |

---

## T0 — Preflight (STOP on failure)
- [ ] Surface = Kiro IDE/local, Executor clone; Node + pnpm on PATH (Homebrew). *(P1)*
- [ ] Spec merged to `main` (merge-first, `RFC-LAB-000-010` §5). *(P3)*
- [ ] Create `feat/bk024-in-app-docs` off up-to-date `main`; clean tree; not `main`. *(P2)*
- [ ] Baseline green: `pnpm --dir app/web install` + `pnpm --dir app/web build` + `pnpm --dir app/web check`. *(P4)*

## T1 — Add the markdown renderer dependency  → R1.1, design §1.2
- [ ] Add `marked` + `dompurify` (+ `@types/dompurify` if needed) to `app/web/package.json` as **pinned** versions via `pnpm --dir app/web add`. *(matches "pin exact versions"; renderer per design recommendation)*
- [ ] Confirm the lockfile updates and `pnpm --dir app/web build` still succeeds.

## T2 — Author the allow-list + transform module  → R1.3, R3, R4, R5, R6.2
- [ ] Create `src/lib/docs/registry.ts` with the explicit `INCLUDED_DOCS` allow-list (User Guide + Project Owner Guide; optional third commented). *(R1.3, R5.2)*
- [ ] Read the raw markdown at build time via `import.meta.glob('…docs/*.md', { query: '?raw', eager: true })`; **if** the cross-root path fails under Vite `fs.allow` / Vercel context, fall back to a `scripts/build-docs.js` `prebuild` step (design §1.1). *(R3.1, R3.2, R3.3)*
- [ ] Strip the leading breadcrumb line per the breadcrumb-shape regex. *(R4.1)*
- [ ] Rewrite relative repo links: included-doc → in-app section; excluded/out-of-app → absolute GitHub URL; unresolvable → plain text (no dead in-app `href`). *(R4.2, R4.3)*
- [ ] Render markdown → sanitized HTML via `marked` + `DOMPurify`; export typed `{ slug, title, html }[]`. *(R1.1)*
- [ ] Build-time **fail-loud** (naming the path) when an allow-listed source doc is missing/renamed. *(R5.1)*
- [ ] Add the inline governance pointer comment on the allow-list (consumer-surface consequence). *(R6.2)*

## T3 — Build the `/docs` route  → R1.1, R1.2, R1.4
- [ ] Create `src/routes/docs/+page.svelte`: a doc picker (index of included docs) + renders the selected doc's `html` into a Tailwind `prose`/typography container. *(R1.2)*
- [ ] Theme-aware + readable light/dark; consistent with the Sleek UI. *(R1.4)*
- [ ] Confirm no excluded doc is reachable from the route (index or links). *(R1.3)*

## T4 — Add the footer / nav link  → R2
- [ ] Add a minimal consumer-labeled link ("Docs" / "Help" / "About") → `/docs` in the global layout (`src/routes/+layout.svelte`) or a small `Footer.svelte`. *(R2.1)*
- [ ] Confirm client-side navigation to `/docs` from any route (SPA fallback already in place). *(R2.2)*
- [ ] Keep branded footer **chrome** out — that is `BK-013`. *(R8.1, design §4)*

## T5 — Governance consequence  → R6.1
- [ ] `docs/governance/ai-collaboration-model.md`: record that an in-app doc is a **consumer surface** — editing an included doc now carries UX/product impact, reviewed as such. *(R6.1)*

## T6 — Self-validate against the EARS DoD + lockstep  → R7, R8 (final task)
- [ ] `pnpm --dir app/web build` + `pnpm --dir app/web check` + `pnpm --dir app/web lint` green with the route + build step added. *(R8.2)*
- [ ] Diff confined to `app/web/` + the R5/R6/R7 doc edits — **no** `data/`, **no** PocketBase schema/migration, **no** auth/dashboard change. *(R8.1)*
- [ ] Walk R1–R8 against the diff; record pass/gaps in `REPORT.md` (match `review-record/REPORT.md` shape: EARS DoD walk table + verification run + Verification Log).
- [ ] Run the §5 Human Verification Plan steps that are agent-executable (build, `/docs` loads, breadcrumb stripped, no broken relative links, audience filter holds, missing-doc fail-loud); leave experiential sign-off to the human.
- [ ] **Lockstep (build-time):** `CHANGELOG.md` `[Unreleased]` entry; `BACKLOG.md` `BK-024` row + `SPRINT_TRACKER.md` note updated to the Spec/track state. *(R7.1, R7.2)*

## T7 — Open PR (STOP-and-hold; never merge)
- [ ] Push `feat/bk024-in-app-docs`; open PR via `gh`/`gh api`. STOP for `/review-pr` + the human merge gate (`RFC-LAB-000-009` §4; Operator never merges).
