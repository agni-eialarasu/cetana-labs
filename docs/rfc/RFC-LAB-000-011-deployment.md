# RFC-LAB-000-011: Deployment Architecture (Vercel + Railway)

> **⚠️ AMENDMENT (2026-09-28, Decision Journal Entry 010):** the backend host is changed **GCP VM → Railway**. Railway gives the exact model this RFC wanted — one always-on container + a persistent volume for PocketBase's single-binary+SQLite — with Vercel-like DX and none of the GCP VM ops burden (patching, firewall, manual HTTPS) this RFC had listed as risks. **Everything else stands** (Vercel frontend, dual-run→retire-Pages cutover, secrets split, custom-domain-deferred). Below, read "GCP VM" as **Railway service** and "VM env / Secret Manager" as **Railway environment variables**; the §4.1 rationale is superseded by §4.1a.
>
> **⚠️ AMENDMENT (2026-09-26, Decision Journal Entry 011 — BK-018 spike):** the M5 deploy shipped with PocketBase **pinned to 0.28.4** as a workaround, because 0.40.x broke GitHub OAuth behind Railway's proxy (`/api/realtime 400 Invalid realtime client`). The `BK-018` spike **root-caused** this (see §4.5): PocketBase 0.40's realtime handshake is incompatible with Railway's proxying of long-lived SSE, and the SDK's *popup* OAuth flow depends on that realtime channel. **Fix (chosen, not yet shipped): switch the frontend to the redirect-based `authWithOAuth2Code` flow**, which never touches `/api/realtime` — which **un-pins the backend to PocketBase 0.40+**. This ships via its own fix Spec (`fix-bk018-oauth-redirect`) through the normal gate; **prod stays 0.28.4 until then**. See new §4.5.

| Property | Value |
| :--- | :--- |
| **RFC ID** | `RFC-LAB-000-011` |
| **Title** | Production Deployment — SvelteKit on Vercel, PocketBase on Railway; retire the GitHub-Pages stopgap |
| **Author** | Eialarasu (LAB-000 Control Hub) |
| **Status** | 🟡 Proposed |
| **Date** | 2026-09-27 |
| **Backlog** | `TSK-053` (SPRINT-09) |
| **Builds On** | `RFC-LAB-000-008` (MVP — unblocks M5), `RFC-LAB-000-007` (work-env / staging placeholders), `RFC-LAB-000-003` (PocketBase), `RFC-LAB-000-001` (cloud dev) |
| **Amends** | `RFC-LAB-000-007` §2.3/§6 (staging + secret-management open questions) · `RFC-LAB-000-008` §6/§9 (M5 target + deploy sequencing) |
| **Decision Journal** | Entry 006 (deployment unblock), Entry 007 (this RFC), Entry 010 (host: GCP VM → Railway), Entry 011 (PB version: un-pin 0.28.4 → 0.40+ via redirect OAuth) |

---

## 1. Context & Problem Statement

The MVP's final phase **M5 (deploy)** was explicitly **blocked on the org-account transfer** (`RFC-LAB-000-008` §10; `RFC-LAB-000-007` staging placeholders "pending org transfer"). **That approval is now granted** for this repo. This RFC resolves the deployment architecture the prior RFCs deferred, and decides the target: **SvelteKit frontend → Vercel; PocketBase backend → GCP**. It also decides the fate of the interim **GitHub-Pages** dashboard.

This is the **decision of record** (the *what/why* + topology). The actual provisioning is **execution** — delivered afterward as M5 Kiro Spec(s) via the AIDLC lifecycle. This RFC does not deploy anything.

## 2. Decision (summary)

1. **Frontend → Vercel.** The SvelteKit static SPA (`app/web`, `adapter-static`, `ssr=false`) deploys to Vercel.
2. **PocketBase → Railway** *(amended from GCP VM)* — a single always-on service (container) with a **persistent volume** for the SQLite file. Same "one process + persistent disk" model this RFC wanted, with managed-platform DX. The containerized path (`RFC-LAB-000-007` Podman `Containerfile`) fits Railway directly and remains the **forward option** if the datastore outgrows SQLite (managed Postgres on Railway/elsewhere).
3. **Dual-run, then cut over.** Deploy to Vercel and verify *alongside* the existing GitHub-Pages dashboard; once Vercel is proven, **retire the Pages stopgap** (`docs/index.html` + `.github/workflows/deploy-pages.yml` + `scripts/generate_dashboard.py` as applicable).
4. **Secrets split by surface:** Vercel **environment variables** for the frontend (`VITE_PB_URL` → the GCP PocketBase URL); **VM environment / GCP Secret Manager** for backend secrets (PocketBase superuser, GitHub OAuth client id/secret).
5. **Custom domain deferred to branding** (`BK-013`): deploy domain-ready on Vercel's default domain now; wire the client custom domain when white-labeling lands.

## 3. Topology

```
                 ┌──────────────────────────┐         ┌─────────────────────────────┐
   Browser  ───▶ │  Vercel (frontend)       │  HTTPS  │  GCP VM (backend)            │
                 │  SvelteKit static SPA    │ ──────▶ │  PocketBase binary + SQLite  │
                 │  env: VITE_PB_URL        │  REST/  │  on a persistent disk        │
                 │  default domain (→custom │  SDK    │  env/Secret Manager:         │
                 │  when branding lands)    │         │  PB superuser, GitHub OAuth  │
                 └──────────────────────────┘         └─────────────────────────────┘
```

- The SPA already reads `VITE_PB_URL` (delivered in M1); production simply points it at the GCP PocketBase URL. The M1 snapshot fallback remains a safety net.
- GitHub OAuth (M2) is configured in the PocketBase admin UI; redirect URLs updated to the Vercel domain.

## 4. Decisions in detail (with rationale)

### 4.1a PocketBase → Railway (amended — supersedes 4.1) — for the MVP
- **Why Railway:** it delivers the exact shape §4.1 wanted — **one always-on process + a persistent volume** for PocketBase's single-binary+SQLite — as a *managed* platform. Deploy from the repo (or the `Containerfile`), attach a volume for `pb_data/`, set env vars, get HTTPS + a URL out of the box.
- **Why it's better than the GCP VM (original 4.1):** it removes the VM ops burden this RFC itself flagged as risks — **no manual patching, firewall, or reverse-proxy/Let's-Encrypt HTTPS setup** (Railway provides TLS + domain). Vercel-like DX on the backend; keeps local↔prod parity (same binary + volume).
- **Trade-off accepted:** platform lock-in + usage-based cost vs. raw-VM control — worth it at control-hub scale for the operational simplicity.
- **Forward path preserved:** the `Containerfile` (`RFC-LAB-000-007` §2.3) deploys directly on Railway; if the datastore outgrows SQLite, Railway (or elsewhere) managed **Postgres** is the documented next step — bridge intact.

### 4.1 PocketBase → small GCP VM (not Cloud Run) — ⚠️ SUPERSEDED by §4.1a (retained for history)
- **Why:** PocketBase is a **single binary + a SQLite file**; it is happiest as **one always-on process with a persistent disk**. Cloud Run's scale-to-zero + mounted-volume story adds operational complexity (cold starts, volume semantics, single-writer SQLite) for little gain at this scale.
- **Trade-off accepted:** always-on cost (an `e2-micro` is minimal) in exchange for operational simplicity and local↔prod parity.
- **Forward path preserved:** if the datastore grows (e.g. Postgres), the containerized `Containerfile` (`RFC-LAB-000-007` §2.3) + Cloud Run/managed DB is the documented next step — this RFC doesn't burn that bridge.
- *(Superseded: the always-on-process+volume goal is now met by Railway (§4.1a) without VM ops.)*

### 4.2 Frontend → Vercel, dual-run then retire Pages
- **Why Vercel:** first-class SvelteKit support, env-var management, preview deploys per PR, trivial custom-domain path later. The app is already a static SPA, so it's a near-drop-in.
- **Dual-run:** deploy Vercel, verify against live GCP PocketBase, keep Pages up as fallback during transition. **Then retire** the Pages stopgap (`index.html`, `deploy-pages.yml`, and the dashboard generator if unused elsewhere) — this completes the "retire the obsolete build artifact" decision (Entry 006).
- **Trade-off:** a brief window of two live frontends; mitigated by making Vercel authoritative and Pages clearly "legacy" during the window.

### 4.3 Secrets split by surface
- **Frontend (Vercel env vars):** only `VITE_PB_URL` (+ optional `VITE_PB_SOURCE`) — non-secret, but env-managed for per-environment config.
- **Backend (VM env / GCP Secret Manager):** PocketBase superuser credentials, GitHub OAuth client id/secret. Resolves `RFC-LAB-000-007` §6 OQ-2. Lean: VM env file for MVP simplicity, Secret Manager as the hardening step.
- **Never committed:** all real secrets stay out of the repo (`.env` gitignored; `.env.example` documents the keys only).

### 4.4 Custom domain deferred to branding
- Deploy on Vercel's default domain now (usable, HTTPS). The **custom domain is a white-labeling concern** (`BK-013`) — wiring it per-client belongs with branding, not this MVP deploy. Keeps M5 shippable without waiting on domain/DNS decisions.

### 4.5 PocketBase version: un-pin 0.28.4 → 0.40+ via redirect OAuth (amendment — BK-018 spike, Entry 011)
- **Context:** M5 shipped with PocketBase **pinned to 0.28.4** because 0.40.x failed GitHub OAuth behind Railway's HTTPS proxy: the sign-in threw `/api/realtime 400 "Invalid realtime client"` and the app 500'd. That pin was a workaround, not a decision of record — the `BK-018` spike was logged to find the real cause.
- **Root cause (confirmed by the spike):** the SDK's all-in-one **popup** OAuth (`authWithOAuth2`) receives its callback over PocketBase's **realtime channel** — a two-step handshake: `GET /api/realtime` opens an SSE stream and returns a `clientId` (this *works* through Railway), then `POST /api/realtime` registers `{clientId, subscriptions:["@oauth2"]}` against that live stream (this **fails** on 0.40: `400 "Missing or invalid client id"`). **Railway's edge proxy does not preserve the SSE connection/affinity that PocketBase 0.40 requires** to associate the POST with the live `clientId`. It is not a version-pairing bug (works locally with no proxy) and is absent on 0.28.4 (older, more tolerant realtime path). Reproduced on a throwaway 0.40 Railway instance using a bundle-verified frontend (validity established first — an earlier "non-reproduction" was an invalid test that had silently hit prod 0.28.4).
- **Decision:** switch the frontend GitHub sign-in from the popup `authWithOAuth2` to the **redirect-based `authWithOAuth2Code`** flow. It performs a plain OAuth `code` exchange and **never opens the `/api/realtime` channel**, so the proxy/SSE incompatibility structurally cannot occur. It is also PocketBase's recommended production flow. **This un-pins the backend to PocketBase 0.40+.**
- **Rejected alternative:** tuning Railway/PocketBase to make SSE realtime survive the proxy (trusted-proxy/CORS/forwarded-headers). Depends on proxy internals we don't control and would leave a fragile SSE dependency on the critical sign-in path.
- **Trade-off accepted:** OAuth UX changes from a popup to a full-page redirect — standard and more robust; acceptable.
- **Execution (not this RFC):** ships via the fix Spec **`fix-bk018-oauth-redirect`** — swap `signInWithGitHub()` in `app/web/src/lib/auth.svelte.ts`, preserve the `github_handle` hook + owner-write resolution (`RFC-LAB-000-008` M3–M4, R3), then un-pin the `Containerfile` to 0.40.x — through the normal PR + verify gate. **Prod stays 0.28.4 until that Spec merges** (no prod change from the spike).

## 5. Amendments to prior RFCs
- **`RFC-LAB-000-007`**: the staging placeholders (`/validate-staging`, `STAGING_*` env vars) and §6 OQ-2 (secret management) are **resolved** here — GCP VM backend + Vercel frontend + the §4.3 secret split.
- **`RFC-LAB-000-008`**: §6 M5 target is fixed to **Vercel + GCP VM**; §9.3 sequencing OQ resolved — **backend (GCP) first** (the frontend needs a live `VITE_PB_URL`), then frontend (Vercel), then Pages retirement.

## 6. Execution plan (delivered later as Spec(s), not in this RFC)

M5 becomes one or more Kiro Specs, run via the lifecycle (merge-first → `/spec-run` → verify → gate):
1. **Provision Railway** — a PocketBase service (repo/`Containerfile`) + a **persistent volume** mounted at `pb_data/`; Railway provides HTTPS + a URL; set backend env vars; seed via existing `pb_provision.py`/`pb_import.py` against the Railway URL.
2. **Provision Vercel** — connect repo, build the SPA, set `VITE_PB_URL` → the Railway PocketBase URL; preview + production.
3. **Wire auth (depends on M2)** — GitHub OAuth redirect URLs → Vercel domain; secrets in place.
4. **Cutover** — verify Vercel against live GCP; **retire Pages** (`index.html`, `deploy-pages.yml`, generator).

> **Dependency:** the *authenticated* deploy needs **M2 (OAuth)**; a *read-only public* deploy can precede M2. Sequencing decided at M5 Spec authoring.

## 7. Scope & Non-Goals
- **In scope:** the deployment topology, hosting choices, secret strategy, cutover plan, and the Pages retirement decision.
- **Non-goals:** the actual provisioning (execution Specs); multi-client/multi-tenant hosting; the custom domain (→ `BK-013`); CDN/caching tuning; autoscaling (single VM suffices at this scale); CI/CD beyond Vercel's native Git integration + the existing GitHub Actions.

## 8. Open Questions (resolve at M5 build)
1. **Railway region** — which region (latency to primary users). *(Decide at provisioning.)*
2. **Backend HTTPS** — **resolved by Railway** (managed TLS + domain out of the box); no reverse-proxy/Let's-Encrypt setup needed. *(This was the GCP-VM burden the amendment removes.)*
3. **Backups** — SQLite file backup cadence to GCS. *(Leaning: a simple scheduled snapshot; define at provisioning.)*
4. **Public-read-before-auth** — deploy a public read-only tier before M2 lands, or wait for auth? *(Leaning: could ship read-only early since M1 read rules are already public-tier.)*

## 9. Risks & Mitigations
| Risk | Mitigation |
| :--- | :--- |
| SQLite single-writer under load | Fine at control-hub scale; managed Postgres is the documented forward option (§4.1a). |
| Secrets leakage | §4.3 split; nothing committed; Railway env vars (backend) + Vercel env vars (frontend). |
| Platform lock-in (Railway) | Accepted for MVP simplicity; the `Containerfile` keeps the app portable to any container host. |
| Dual-run confusion (two live frontends) | Vercel authoritative; Pages explicitly legacy; retire promptly post-verify. |
| Deploy coupled to M2 auth | §6 dependency note — a public read-only deploy can precede auth. |
| VM ops burden (patching, uptime) | Minimal single instance; documented runbook in `developer-guide`; container/managed path if it grows. |
| Data loss on VM failure | §8.3 backup cadence to GCS decided at provisioning. |
| PocketBase 0.40 OAuth breaks behind Railway's SSE proxy | Root-caused (BK-018, §4.5); resolved by the redirect OAuth flow (`fix-bk018-oauth-redirect`), which un-pins 0.28.4 → 0.40+. Prod stays 0.28.4 until that Spec ships. |
