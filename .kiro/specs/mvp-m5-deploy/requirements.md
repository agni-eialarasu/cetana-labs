# MVP M5 — Deploy (Vercel + Railway) — Requirements

| Property | Value |
| :--- | :--- |
| **Spec ID** | `mvp-m5-deploy` |
| **Feature** | MVP Phase M5 — deploy the authenticated app: SvelteKit → Vercel, PocketBase → Railway; retire the GitHub-Pages stopgap |
| **Backlog** | `TSK-054` (SPRINT-09), epic `BK-011` |
| **Status** | 🟡 Proposed (contract authored on Kiro Web; execution on Kiro IDE + cloud consoles) |
| **RFCs** | `RFC-LAB-000-011` (deployment — **amended: Vercel + Railway**, Entry 010), `RFC-LAB-000-008` (MVP §6 M5), `RFC-LAB-000-006` (OAuth) |
| **Executor role** | Delegated-agent / onboarded-dev (full Spec) — **with human-performed cloud provisioning steps** (see §0) |

---

## 1. Introduction

M1–M4 completed the MVP's **local** loop (read live PB, OAuth sign-in, minimum RBAC, owner-writes-own). **M5 makes it real:** deploy the frontend to **Vercel** and PocketBase to **Railway**, wire production auth, verify end-to-end on live URLs, and **retire the GitHub-Pages classic dashboard** — completing the MVP.

Per `RFC-LAB-000-011` (as amended): **Vercel (frontend) + Railway (PocketBase: container + persistent volume, managed TLS/domain)**; **dual-run then retire Pages**; **secrets split** (Railway env + Vercel env); **custom domain deferred** to branding (`BK-013`).

**Honest nature of this Spec:** M5 is **infra + configuration**, much of it in **cloud consoles the agent cannot fully drive** (Railway/Vercel dashboards, GitHub OAuth app, secrets). So this Spec is **part agent-executable, part human-performed** — it explicitly marks which steps are which, and STOPs for the human on the console steps rather than fabricating credentials.

## 0. Preconditions (preflight — verify BEFORE any change; enforced by `tasks.md` T0)

- **P1 — Surface:** Kiro **IDE / local** for repo edits + local verification; **cloud consoles (human)** for provisioning.
- **P2 — Accounts/prereqs (HUMAN — STOP if absent, do not fabricate):**
  - A **Railway** account/project (can host a container + a persistent volume).
  - A **Vercel** account/project (can build the SvelteKit SPA from the repo).
  - A **production GitHub OAuth app** (or the dev one reconfigured) with callback = the **Railway PocketBase** `/api/oauth2-redirect`.
- **P3 — Local baseline green:** M1–M4 work locally; three validators + `pnpm --dir app/web check && build` pass.
- **P4 — Merge-first:** this Spec merged to `main` before `/spec-run`.
- **P5 — M2/M3/M4 merged** (this deploys the authenticated app; the owner-write loop must exist).

## 2. Current-state facts (of record)

- **Frontend:** SvelteKit static SPA (`adapter-static`, `ssr=false`), reads `VITE_PB_URL` (M1). Snapshot fallback exists (never blanks).
- **Backend:** PocketBase — single binary + SQLite (`pb_data/`), provisioned by `pb_provision.py`, seeded by `pb_import.py`; a `pb_hooks/oauth_github_handle.pb.js` hook (M3–M4) populates `github_handle` on OAuth; a Podman `Containerfile` exists (`RFC-LAB-000-007`).
- **Interim dashboard:** GitHub-Pages classic dashboard = `docs/index.html` + `.github/workflows/deploy-pages.yml` + `scripts/generate_dashboard.py`. **To be retired** post-cutover.
- **Sequencing (RFC-011 §5, amended):** **backend (Railway) first** → frontend (Vercel) → Pages retirement.

## 3. Requirements (EARS acceptance criteria = Definition of Done)

### R1 — PocketBase deployed on Railway
- **R1.1** PocketBase SHALL run on **Railway** as a service (from the `Containerfile` or a supported deploy) with a **persistent volume** mounted for `pb_data/` (SQLite survives restarts/redeploys).
- **R1.2** Railway SHALL serve it over **HTTPS at a stable URL** (managed TLS/domain — no manual reverse proxy).
- **R1.3** Collections SHALL be provisioned (`pb_provision.py`) and seeded (`pb_import.py`) against the Railway instance; the `oauth_github_handle` hook SHALL be present.
- **R1.4** The PocketBase **superuser** SHALL be set (admin escape hatch) with credentials in Railway env, not committed.

### R2 — Frontend deployed on Vercel
- **R2.1** The SvelteKit SPA SHALL build + deploy on **Vercel** from the repo (production + PR previews).
- **R2.2** `VITE_PB_URL` SHALL be set (Vercel env var) to the **Railway PocketBase URL**; the deployed app reads live data from it.
- **R2.3** The deployed frontend SHALL be reachable at a stable **HTTPS Vercel URL**.

### R3 — Production auth wired
- **R3.1** The GitHub OAuth app'"'"'s callback SHALL point to the **Railway** PocketBase OAuth2 redirect; OAuth2 SHALL be enabled on the `users` collection in the deployed instance (per `developer-guide.md` §5.1).
- **R3.2** A user SHALL be able to **sign in with GitHub on the deployed Vercel URL**, link by `github_handle`, and an owner SHALL edit their own project status **in production** (M2–M4 working end-to-end live).
- **R3.3** OAuth secrets SHALL live in the deployed PocketBase config (Railway), never in the repo or the frontend.

### R4 — Minimum RBAC holds in production
- **R4.1** The §4 rule matrix SHALL hold on the deployed instance: public read; owner-writes-own; **non-owner write denied**; superuser retains access.

### R5 — Dual-run, then retire the Pages stopgap
- **R5.1** During transition, the Vercel app and the GitHub-Pages dashboard MAY both be live (Vercel authoritative).
- **R5.2** AFTER the deployed app is verified, the Pages stopgap SHALL be retired: remove `docs/index.html`, `.github/workflows/deploy-pages.yml`, and `scripts/generate_dashboard.py` (if unused elsewhere) — completing the retirement decision (Entry 006/RFC-011).
- **R5.3** Retirement SHALL NOT break the docs site or README links (verify no dangling references to the removed dashboard).

### R6 — Config, secrets, docs
- **R6.1** `.env.example` (root + `app/web`) SHALL document the production vars (Railway PB URL, `VITE_PB_URL`) as environment-configured (keys/comments only; no secrets).
- **R6.2** `developer-guide.md` SHALL gain a **Deployment** section: how the Railway + Vercel deploy is wired (a runbook for re-deploy / new environments), including the OAuth-redirect step.
- **R6.3** No secret SHALL be committed.

### R7 — No regression
- **R7.1** Local dev (M1–M4) SHALL still work unchanged; the M1 snapshot fallback SHALL remain.

### R8 — Quality gates green
- **R8.1** `pnpm --dir app/web check && build && lint` and `make validate-local` SHALL pass; after Pages retirement, no validator/CI job SHALL reference the removed dashboard workflow/script.

## 4b. Human Verification Plan (emitted by `/spec-run`; recorded by `/verification-done`)

Against the **live deployed URLs** (mostly human — deployment is inherently hands-on):
- **V1 — Backend live:** the Railway PocketBase URL responds over HTTPS; admin UI reachable; collections seeded (6 projects).
- **V2 — Frontend live:** the Vercel URL loads the dashboard, reading **live data from Railway** (not the snapshot — confirm by editing a record in PB admin, refresh, see it).
- **V3 — Sign in (prod):** GitHub OAuth on the Vercel URL → signed in; linked by `github_handle`.
- **V4 — Owner write (prod):** as an owner, edit your project status on the live app → persists to Railway PB.
- **V5 — RBAC (prod, SECURITY):** a non-owner write is **denied** on the deployed instance (rule-enforced), with owner-write as the positive control.
- **V6 — Persistence:** restart/redeploy the Railway service → data survives (persistent volume).
- **V7 — Pages retired cleanly:** the old GitHub-Pages dashboard is gone; no dangling links; the docs site (if any) still resolves.
- **V8 — Gates + no regression:** local M1–M4 still work; `make validate-local` green; no CI job references the removed workflow.

**Verdict rule:** V1–V8 pass before `/verification-done`. V5 is the security check; V6 the persistence check (the whole point of the volume).

## 5. Out of Scope (deferred)
- **Custom domain / white-label** (→ `BK-013`) — deploy on default Vercel/Railway domains.
- Multi-tenant / multi-client hosting; CDN/caching tuning; autoscaling; managed Postgres migration (SQLite forward-path, `RFC-LAB-000-011` §4.1a).
- Backups hardening beyond a basic volume-snapshot/export note (define at provisioning — OQ).
- The full 5-role `memberships` model; audit trail.

## 6. Open Questions (resolve at build start)
1. **Railway deploy source:** the `Containerfile` vs. a Railway-native buildpack for PocketBase. *(Leaning: `Containerfile` — reuses the existing image, keeps parity/portability.)*
2. **Backup cadence:** Railway volume snapshot vs. a scheduled `pb_data` export to object storage. *(Leaning: start with Railway volume snapshots; scheduled export as hardening.)*
3. **Seeding prod:** run `pb_provision.py`/`pb_import.py` from local against the Railway URL, or a one-off deploy hook. *(Leaning: local run against the Railway URL for the first seed; document in the runbook.)*
4. **Public-read-before-auth:** the M1 public tier is already open — the deployed app is publicly readable immediately; confirm that'"'"'s intended for launch.
