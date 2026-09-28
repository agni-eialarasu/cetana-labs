# MVP M5 — Deploy (Vercel + Railway) — Tasks

> Ordered plan for `/spec-run` (Build). **Mixed agent + human-in-console** work — steps marked **[HUMAN]** need you in the Railway/Vercel/GitHub consoles; the agent STOPs and instructs (never fabricates credentials). Do NOT merge; open a PR, emit the Human Verification Plan, STOP in `IN_VERIFICATION`.

## Execution header (self-describing — read by `/spec-run`)

| Field | Value |
| :--- | :--- |
| **Spec id** | `mvp-m5-deploy` |
| **Kickoff (IDE one-liner)** | `/spec-run mvp-m5-deploy` |
| **Surface** | Kiro **IDE** (repo + local verify) + **cloud consoles** (Railway/Vercel/GitHub — human) |
| **Branch to create** | `feat/mvp-m5-deploy` (off up-to-date `main`, per `RFC-LAB-000-004`) |
| **Base for PR** | `main` |
| **Preflight** | Requirements §0 (P1–P5; **P2 = Railway + Vercel accounts + prod OAuth app — STOP if absent**) + task **T0** |
| **Self-validation target** | `requirements.md` EARS R1–R8 |
| **Human Verification Plan** | `requirements.md` §4b (V1–V8; V5 = security, V6 = persistence) |
| **On completion** | Open PR via `gh api`, emit the Verification Plan, STOP → `/verification-done` → `/review-pr` (never merge) |
| **Executor role** | Delegated-agent / onboarded-dev (+ human console steps) |

---

- [ ] **T0 — Preflight (gate — STOP on any ❌)**
  - Surface=IDE; clean tree; branch off fresh `main`; this Spec on `main` (merge-first).
  - **[HUMAN] P2:** confirm Railway account/project, Vercel account/project, and a prod GitHub OAuth app exist. **If absent, STOP** with setup instructions — do not fabricate credentials/URLs.
  - Local baseline green (M1–M4 work; validators + `pnpm check`/`build`).
  - _Refs: §0._

- [ ] **T1 — [HUMAN] Provision PocketBase on Railway**
  - Create a Railway service from the `Containerfile`; **attach a persistent volume at `pb_data/`**; set backend env (PB superuser, later OAuth secrets). Note the Railway HTTPS URL.
  - Agent provides the exact steps + the env-var list; STOPs for the human to click.
  - _Refs: R1.1, R1.2, R1.4, design §2._

- [ ] **T2 — Provision + seed collections against Railway**
  - Run `pb_provision.py` then `pb_import.py` with `PB_URL=<railway-url>` + `PB_ADMIN_*` (first seed from local — OQ-3). Confirm 6 projects + the `oauth_github_handle` hook present.
  - _Refs: R1.3, design §2._

- [ ] **T3 — [HUMAN] Provision the SPA on Vercel**
  - Connect the repo; build `app/web`; set **`VITE_PB_URL` = the Railway URL** (Vercel env). Deploy; note the Vercel HTTPS URL.
  - Agent provides steps + the env list; STOPs for the human.
  - _Refs: R2.1, R2.2, R2.3, design §3._

- [ ] **T4 — [HUMAN] Wire production GitHub OAuth**
  - Set the OAuth app callback → `<railway-url>/api/oauth2-redirect`; enable OAuth2 on the deployed `users` collection (per `developer-guide.md` §5.1); put client id/secret in Railway/PB config.
  - _Refs: R3.1, R3.3, design §4._

- [ ] **T5 — Docs & config (agent)**
  - `.env.example` (root + `app/web`): document prod vars (keys/comments, no secrets). Add a **Deployment** runbook section to `developer-guide.md` (Railway + Vercel + OAuth redirect + seed).
  - _Refs: R6.1, R6.2, R6.3, design §7._

- [ ] **T6 — Retire the GitHub-Pages stopgap (agent) — AFTER live verify (see T8/V2–V5)**
  - Remove `docs/index.html`, `.github/workflows/deploy-pages.yml`, `scripts/generate_dashboard.py` (grep first — only if unused elsewhere). Update README/docs references; link-check for danglers. Do this as its own commit, **only once the deployed app is verified**.
  - _Refs: R5.2, R5.3, design §6._

- [ ] **T7 — Quality gates + no-regression (agent)**
  - `pnpm --dir app/web check && build && lint`; `make validate-local`. After T6, confirm **no CI job/validator references the removed workflow/script**. Local M1–M4 still work; snapshot fallback intact.
  - _Refs: R7, R8._

- [ ] **T8 — Commit, open PR, emit Human Verification Plan, STOP**
  - Branch `feat/mvp-m5-deploy`; semantic commit referencing `TSK-054` / `BK-011` M5.
  - Open PR into `main` via `gh api`; CI green; emit §4b plan (V1–V8; **V5 security, V6 persistence**); STOP in `IN_VERIFICATION`. **Never merge.**
  - Note in the PR: deployment verification is live-URL + human-performed; the Verification Log carries the evidence.
  - _Refs: R-all, `RFC-LAB-000-009` §3.2._

- [ ] **T9 — After human verification passes: `/verification-done`**
  - Human runs V1–V8 on the live URLs (esp. V5 non-owner-denied, V6 data-survives-redeploy); fixes ride the same PR; on pass, `/verification-done` writes the Verification Log → `IN_REVIEW` → `/review-pr`.
  - _Refs: `RFC-LAB-000-009` §3.2._

---

### Governance lockstep reminder (Record, after merge)
Note M5 in CHANGELOG (`TSK-054`). **This completes the MVP** (`BK-011`) — logged-in owner edits own status, deployed and usable. `/sprint-done` then closes SPRINT-09 and cuts the release (candidate `v0.11.0` / MVP milestone). The custom domain (`BK-013`) and the deferred features (settings/branding/admin-CRUD/AI) follow.
