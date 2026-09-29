# Provision the throwaway PocketBase 0.40 env — BK-018 / TSK-055

> Working doc (not a governance artifact). Turnkey checklist to stand up the
> throwaway 0.40 staging env that `/spec-run fix-bk018-oauth-redirect` needs
> (preflight P1 halts without it). **All steps require a machine with creds +
> a browser — they cannot run in Kiro Web.** Prod (0.28.4) stays untouched (P6).

## Why a human/IDE must do this
Kiro Web is stateless and has **no Railway/Vercel CLI, no creds, no browser**.
Per developer-guide §9A.4 + PB README, the core steps are irreducibly interactive:
Railway login, volume attach (dashboard-only), GitHub OAuth app + callback (browser),
and secret entry (Railway PB admin UI). Web pre-staged `.env.staging` (gitignored)
and this checklist; the rest is a human-at-a-machine job.

## Checklist (do in order)

- [ ] **0. Login (once/machine):** `railway login` && `vercel login`.
- [ ] **1. Backend up (0.40.x):** from `app/pocketbase/`, `railway up` for a NEW throwaway
      service (`railway.json` pins `Containerfile` → builder; Containerfile PB pin is
      bumped to 0.40+ by `/spec-run` T4 — for provisioning you can deploy the 0.40 build
      on a branch, or set `PB_VERSION=0.40.x` build arg on the throwaway service).
- [ ] **2. Persistent volume (dashboard-only):** Service → Settings → Volumes → attach a
      Volume mounted at **`/pb/pb_data`**. Without it every redeploy wipes the DB.
- [ ] **3. Grab the URL:** copy the throwaway `https://<throwaway>.up.railway.app`.
- [ ] **4. GitHub OAuth app (browser):** create/point an OAuth app; Authorization callback
      URL(s) must include BOTH:
        - `<PB_URL>/api/oauth2-redirect`            (SDK server leg)
        - `<frontend-origin>/oauth/callback`        (the NEW redirect-flow leg this fix adds)
      Then set client id/secret in the throwaway **Railway PB admin** (users → OAuth2 → GitHub).
      Use **throwaway creds** (casual tier, RFC-012 §4) — no real secrets, none in git.
- [ ] **5. Fill `.env.staging`** (already created, gitignored): set `PB_URL`, `VITE_PB_URL`,
      `PB_ADMIN_*`, and `FORBIDDEN_PROD_PB_URL` = the live prod URL.
- [ ] **6. Seed (CLI):** `set -a; source .env.staging; set +a` then
      `python3 scripts/pb_provision.py --apply && python3 scripts/pb_import.py --apply`
      → creates projects/users collections (the spike's false-negative was an UNSEEDED backend).
- [ ] **7. Hand back to /spec-run:** report the throwaway `PB_URL`. Before any live sign-in,
      the IDE run does:
        `make web-build`
        `make verify-bundle EXPECTED=$VITE_PB_URL FORBIDDEN=$FORBIDDEN_PROD_PB_URL`
      (assert the bundle baked the THROWAWAY, not prod — the BK-018 false-negative guard).

## Guardrails
- **Prod (0.28.4) untouched** — this is a separate throwaway service (live cutover = BK-019).
- **No secrets in git** — `.env.staging` stays gitignored; real secrets live in Railway/Vercel vars.
- **Gated ops (RFC-012 §6):** any throwaway/spike CODE lands on a branch → PR; the finding merges.
