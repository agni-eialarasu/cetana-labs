# MVP M5 — Deploy (Vercel + Railway) — Design

> Companion to `requirements.md`. Provision PocketBase on Railway (container + volume), the SPA on Vercel, wire production OAuth, verify live, retire the Pages stopgap. Per `RFC-LAB-000-011` (amended: Vercel + Railway). Much of this is **human-in-console** work — the design marks agent-vs-human steps.

---

## 1. Approach: config + infra, mostly outside the repo

M5 is not app-code — it's **provisioning + wiring + a small amount of repo change** (env docs, deploy runbook, Pages retirement). The app is already deploy-ready (static SPA reading `VITE_PB_URL`; PocketBase = binary + `Containerfile`). So M5 = stand up two managed services, point them at each other, verify live, then remove the old dashboard.

**Agent vs. human split (honest):**
- **Human (console):** create the Railway service + volume, the Vercel project, set env vars/secrets, configure the GitHub OAuth app + redirect, click deploy. The agent **cannot** do these; it provides exact instructions and STOPs.
- **Agent (repo/CLI):** the `.env.example` + `developer-guide` deploy runbook, the Pages-retirement file removals, the seed commands (run against the Railway URL once it exists), verification scripting where possible.

## 2. Backend on Railway (R1)

- **Deploy source:** the existing Podman/OCI `Containerfile` (`RFC-LAB-000-007`) — Railway builds/runs it (OQ-1 leaning: container over buildpack for parity/portability).
- **Persistent volume:** mount a Railway volume at PocketBase'"'"'s `pb_data/` so SQLite + uploads survive restarts/redeploys (R1.1, V6). *This is the crux — without the volume, a redeploy wipes data.*
- **TLS/URL:** Railway provides managed HTTPS + a stable URL out of the box (R1.2) — no reverse proxy / Let'"'"'s Encrypt (the GCP-VM burden the amendment removed).
- **Provision + seed (R1.3):** run `pb_provision.py` then `pb_import.py` **against the Railway URL** (`PB_URL=<railway>` + `PB_ADMIN_*`), from local for the first seed (OQ-3). The `oauth_github_handle` hook ships in `pb_hooks/` with the image.
- **Superuser (R1.4):** set via Railway env; admin escape hatch preserved.

## 3. Frontend on Vercel (R2)

- Connect the repo; build `app/web` (SvelteKit `adapter-static`). Vercel gives production + per-PR previews.
- **`VITE_PB_URL` = the Railway PocketBase URL** (Vercel env var, per environment). The SPA already consumes it (M1); nothing app-side changes.
- Stable HTTPS Vercel URL (R2.3).

## 4. Production auth (R3)

- GitHub OAuth app **callback → `<railway-pb-url>/api/oauth2-redirect`**; enable OAuth2 on the deployed `users` collection (per `developer-guide.md` §5.1 — the v0.40 collection-scoped path).
- Secrets (OAuth client id/secret, PB superuser) live in **Railway/PocketBase config**, never the repo or frontend (R3.3).
- End-to-end (R3.2): sign in on the Vercel URL → `github_handle` populated by the hook → owner edits own status live.

## 5. RBAC in prod (R4)

The rule matrix is provisioned by `pb_provision.py` (same code as local), so deploying re-applies it. Verify on the live instance: non-owner write denied (V5), owner-writes-own, superuser retains access. Enforcement is the same server-side rule — cloud doesn'"'"'t change it.

## 6. Dual-run then retire Pages (R5)

- Keep GitHub-Pages live until Vercel is verified (Vercel authoritative).
- **Retire (agent, repo change):** remove `docs/index.html`, `.github/workflows/deploy-pages.yml`, `scripts/generate_dashboard.py` (if unused elsewhere — grep first). Update any README/docs references. Verify no dangling links (like the docs-reorg link-check).
- Do the retirement **only after** live verification (V2–V5 pass), as its own commit within the M5 PR.

## 7. Docs & config (R6)

- `.env.example` (root + `app/web`): document the prod vars (Railway PB URL, `VITE_PB_URL`) — keys/comments only.
- `developer-guide.md`: a **Deployment** section — the Railway + Vercel runbook (create service + volume, env vars, OAuth redirect, seed against Railway, deploy Vercel), reusable for re-deploy / new environments.

## 8. Verification (feeds `tasks.md` + `/verification-done`)

Maps to V1–V8 — almost entirely **live-URL, human-performed** (deployment can'"'"'t be meaningfully faked): backend live + seeded; frontend live reading Railway; prod sign-in; prod owner-write; **prod non-owner denied (security)**; **data survives redeploy (volume)**; Pages retired cleanly; local no-regress + gates.

## 9. Trade-offs

| Decision | Chosen | Rejected | Why |
| :--- | :--- | :--- | :--- |
| Backend host | Railway (container+volume) | GCP VM (superseded) | Managed TLS/domain, no VM ops; same always-on+volume model (RFC-011 §4.1a). |
| Deploy source | `Containerfile` | Railway buildpack | Parity + portability; reuses existing image. |
| First seed | local run vs Railway URL | deploy hook | Simplest for the first seed; documented in the runbook. |
| Retire Pages | after live verify, same PR | before / separate PR | No gap with no live dashboard; keeps the decision atomic. |
| Custom domain | defer (BK-013) | wire now | White-label concern; don'"'"'t gate M5 on DNS. |
