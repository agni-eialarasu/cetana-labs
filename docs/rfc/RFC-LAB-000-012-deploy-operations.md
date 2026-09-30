# RFC-LAB-000-012: Deploy Operations & Environment Promotion

| Property | Value |
| :--- | :--- |
| **RFC ID** | `RFC-LAB-000-012` |
| **Title** | Deploy Operations — CLI-first deploys, casual→qualified environment promotion, artifact verification |
| **Author** | Eialarasu (LAB-000 Control Hub) |
| **Status** | 🟡 Proposed |
| **Backlog** | `BK-017` (this RFC is its decision of record); `SPRINT-10` |
| **Builds On** | `RFC-LAB-000-011` (deployment architecture — Vercel + Railway), `RFC-LAB-000-007` (work-env / secrets), `RFC-LAB-000-009` (lifecycle — gates apply to spikes too) |
| **Decision Journal** | Entry 012 (D45 — the motivating pain), Entry 013 (this RFC), Entry 014 (D52 — reframed as reference ops guidance) |

---

> **Scoping note (Decision Journal Entry 014, D52) — added after `automate-staging-deploy`.**
> This RFC is now **optional reference ops guidance**, *not* part of the lifecycle contract.
> The lifecycle contract is: **`done` = the gated merge to `main`**, which auto-deploys both
> tiers to the **single reference environment** (frontend via Vercel; backend via
> `.github/workflows/deploy-backend.yml`). The casual→qualified promotion and any
> staging→prod hardening described below are **out-of-scope ops** (`BK-019`) — useful when a
> real prod tier is eventually stood up, but not a gate any feature passes through today.
> The CLI-first mechanics here remain the basis of the on-demand `/deploy-adhoc` dev tool.
> *(This is an append-only scoping note; the decisions below are unchanged.)*

---

## 1. Context & Problem Statement

`RFC-LAB-000-011` decided *what* we deploy to (Vercel + Railway). It did **not** decide *how we operate deploys* — and the M5 deploy + the BK-018 spike exposed that gap as real, repeated pain (Decision Journal Entry 012):

- **UI-driven deploys are fragile and opaque.** Vercel env scoping (Prod vs Preview), Secret→Config locks, Root-Directory doubling, and Vite'"'"'s **build-time inlining** silently pointed a "verification" build at the **wrong (prod) backend** — a false negative that nearly derailed the BK-018 diagnosis. "Understanding each UI" was cited as the core friction.
- **First-time staging/prod setup is treated too preciously.** Wrestling real secrets/passwords through consoles on the *first* attempt makes standing up a new environment miserable — when what'"'"'s actually wanted is to get it *working* casually first, then harden.
- **Governance discipline is easy to lose during ops work.** The BK-018 spike bypassed the gate (committed straight to `main`) partly because the ops flow was ad-hoc.

This RFC standardizes **deploy operations** so any environment (local → staging → prod) is stood up the same casual, reproducible, scriptable way — then *qualified* and hardened. Blueprint-grade: copyable to any repo using the model.

## 2. Decision (summary)

1. **CLI-first deploys** — use the **Railway CLI** and **Vercel CLI** for all ad-hoc/iterative deploys, with **repo-committed config** (`vercel.json`, `railway.json`, `.env.*.example`). UIs are for one-time linking + inspection/verification, not the iteration loop.
2. **Casual → qualified environment promotion** — treat a new staging/prod **like local**: throwaway credentials, get it working, verify — **then** *qualify* the environment and rotate real secrets via the UI. Environments have an explicit lifecycle state.
3. **Verify the artifact, not the setting** — for build-time-inlined config (Vite `VITE_*`), **assert the value in the built bundle** before trusting any live test.
4. **Gates apply to ops too** — deploy/spike/ops work follows the same branch → PR → gate discipline (`RFC-LAB-000-009`); nothing ad-hoc to `main`.
5. **Secrets never in git** — ever, throwaway or real; env files stay gitignored. "Casual" means shared *throwaway* creds in a *throwaway* instance, not secrets in the repo.

## 3. CLI-first deploys (Decision 1)

| Task | Tool | Committed config |
| :--- | :--- | :--- |
| Frontend deploy | **Vercel CLI** (`vercel`, `vercel --prod`) | `app/web/vercel.json` (build/output — already landed) |
| Backend deploy | **Railway CLI** (`railway up`, `railway deploy`) | `railway.json` (builder = the `Containerfile`; volume config) |
| Env vars | CLI (`vercel env`, `railway variables`) — never committed | `.env.staging.example` (keys/comments only) |
| Verify | Railway / Vercel **UI** (inspect deploy, logs, env) | — |

- **One-time UI setup** (link the project, connect the repo) is fine; the **iteration loop is CLI** — reproducible, scriptable, greppable.
- The intended scaffold (`railway.json`, `.env.staging.example`, a `make deploy-staging` / `scripts/deploy.sh`) is a **follow-on Spec** (§7), not this RFC.

## 4. Casual → qualified environment promotion (Decision 2)

Every deployed environment has a lifecycle state — mirroring how we already treat *local*:

```
CASUAL (get it working)  ──verify──▶  QUALIFIED (hardened)  ──▶  (prod use)
throwaway creds/secrets,             real secrets rotated via UI,
throwaway instance, iterate          access locked down, treated as real
freely; DON'T sweat secrets          from here on
```

- **CASUAL:** stand up the environment with **throwaway credentials** (shared, low-stakes), deploy freely via CLI, iterate. Don'"'"'t wrestle real secrets yet. This is the mode the first-time setup pain lives in — so make it *casual*.
- **Qualification (the gate to QUALIFIED):** the environment is verified working end-to-end (the app'"'"'s Human Verification Plan passes against it) → **then** rotate to **real secrets** via the UI, lock down access, and mark it qualified. From here it'"'"'s treated as real (prod discipline).
- **Guardrail:** casual ≠ careless with git — **no secrets in the repo at any stage** (Decision 5). Throwaway creds live in the throwaway instance / CLI-set env vars, never committed.

## 5. Verify the artifact, not the setting (Decision 3)

The BK-018 false negative (Entry 011/012): a Vercel *preview* looked correct but had **baked in the prod `VITE_PB_URL`** — because Vite inlines `VITE_*` at **build time**, so the *setting* in the console said one thing while the *bundle* contained another.

**Rule:** before trusting any live test of a build-time-configured frontend, **assert the baked-in value in the built artifact** (e.g. `grep <expected-backend-url> build/ && ! grep <other-backend-url> build/`). The scaffold Spec (§7) should provide this as a helper (auto-assert the baked-in backend URL on deploy).

## 6. Gates apply to ops & spikes too (Decision 4)

`RFC-LAB-000-009`'"'"'s branch → PR → human-gate discipline applies to **deploy/ops/spike work**, not just features. Even throwaway spike *code* commits on a branch (never `main`); the spike'"'"'s *finding* is what merges. (Entry 012'"'"'s lesson, codified.)

## 7. Deliverables

- **This RFC** (decision of record; `BK-017`).
- (Follow-on Kiro Spec, merge-first): the **deploy scaffold** — `railway.json`, `.env.staging.example`, a `make deploy-staging`/`scripts/deploy.sh` CLI wrapper, the **artifact-assertion helper** (§5), and a `developer-guide.md` §Deployment update (CLI runbook + the casual→qualified model).
- **Fold-in DX fix:** the recurring **`data/status.json` time-drift** (5 CI failures across unrelated PRs — `days_ago` is date-relative, so any branch goes stale by time passing). Make the status-sync check **date-tolerant** (ignore `days_ago`, or compute it at read-time) so it stops blocking unrelated PRs. Tracked as **`BK-020`**; fixed in the scaffold Spec.

## 8. Scope & Non-Goals
- **In:** the deploy operations model (CLI-first, casual→qualified, artifact verification, gated ops), and the status-drift DX fix.
- **Non-goals:** the deployment *architecture* (that'"'"'s `RFC-LAB-000-011`); the BK-018 OAuth *fix* (its own Spec, deferred until this DX exists); CI/CD pipeline automation beyond the CLI wrappers; multi-tenant/multi-client env management.

## 9. Open Questions
1. **`make` vs `scripts/`** for the CLI wrappers — a `make deploy-staging` target vs. a `scripts/deploy.sh`. *(Leaning: `make` target delegating to a script, consistent with the existing Makefile cheat-sheet.)*
2. **Qualification checklist** — how formal is the CASUAL→QUALIFIED gate (a documented checklist vs. a skill)? *(Leaning: a checklist in `developer-guide.md` now; a skill only if it earns it.)*
3. **status.json fix approach** — drop `days_ago` from the sync-check comparison, vs. compute `days_ago` at read-time (so it'"'"'s never stored/stale). *(Leaning: compute-at-read — removes the drift class entirely; decide in the scaffold Spec.)*

## 10. Risks & Mitigations
| Risk | Mitigation |
| :--- | :--- |
| CLI drift from UI state | Repo-committed config (`vercel.json`/`railway.json`) is the source of truth; UI for inspection only. |
| Casual creds leaking to prod | Explicit qualification gate rotates to real secrets before an env is treated as real; no secrets in git ever (Decision 5). |
| Build-time-config false negatives | §5 artifact-assertion rule + a helper in the scaffold. |
| Ops work bypassing the gate (again) | §6 codifies gated ops; Entry 012 is the cautionary record. |
| status-drift keeps blocking PRs | §7 fold-in fix (`BK-020`) makes the check date-tolerant. |
