# Deploy Scaffold — Report

| Property | Value |
| :--- | :--- |
| **Spec ID** | `deploy-scaffold` |
| **Feature** | Implement `RFC-LAB-000-012` — CLI-first deploy scaffold, artifact-verification helper, casual→qualified runbook, + the `status.json` date-drift fix (`BK-020`) |
| **Backlog** | `TSK-056` (`BK-017`), incl. `BK-020` |
| **PR** | [#43](https://github.com/agni-eialarasu/cetana-labs/pull/43) → `main` |
| **Branch** | `feat/deploy-scaffold` |
| **Implementation commit** | `72e2aab` |

---

## Verification Log — 2026-09-29 (PR #43)

Human functional verification against the Spec's Human Verification Plan (`requirements.md` §4b), run on Kiro IDE. The agent-runnable checks were executed/confirmed programmatically; the browser and read-through checks were exercised by the human.

| Plan step | Result | Finding / correction |
| :--- | :---: | :--- |
| V1a — `generate_status_json.py --check` stable across elapsed time; time fields removed from `status.json` | ✅ | `--check` green; `grep days_ago\|is_stale data/status.json` = 0. Date-independence also proven at a mocked +400d clock (build output identical to the committed file). |
| V1b — SPA renders with no regression (R5.3) | ✅ | **Plan step corrected during verification.** As originally written ("confirm the SPA shows correct days-ago"), the step was mis-specified: investigation confirmed the SPA never rendered `days_ago`/`last_updated` in any template (before or after this change) — it was only ever consumed for sort/stale-threshold logic. The correct R5.3 claim is *no UI regression*. Screenshot confirmed all cards render correctly (health, wins, focus, owner) with no blanks or console errors. No code change (scope discipline — R5 is a drift fix + no-regression, not a new UI element). |
| V2 — artifact helper catches a wrong bundle | ✅ | Built against a wrong `VITE_PB_URL` then asserted the expected one → `verify-bundle` failed loudly and refused (non-zero). Built against the correct URL → `✅ … no forbidden URL present` (rc=0). Note: via `make`, an assertion failure surfaces as make's `Error 1` / exit **2** (make's convention); the script's own exit is **1** when run directly (`bash scripts/verify-bundle.sh`). Behavior is correct — a wrong bundle is caught. |
| V3 — `railway.json` pins the builder | ✅ | `build.builder = DOCKERFILE`, `dockerfilePath = Containerfile` (no Railpack auto-detect). |
| V4 — deploy wrapper (runnable surface) | ✅ | `scripts/deploy.sh all` with no `.env.staging` → helpful error pointing at `cp .env.staging.example .env.staging` (rc=1). `scripts/deploy.sh checklist` → prints the one-time [HUMAN] steps (login, volume at `/pb/pb_data`, OAuth, Vercel env) (rc=0). Live Railway/Vercel deploy is the documented [HUMAN]/login-gated boundary, not exercised. |
| V5 — runbook coherent | ✅ | `developer-guide.md` §9A (Deploy Operations) + `app/pocketbase/README.md` "Deploy on Railway" read as followable end-to-end. |
| V6 — no secrets committed; gates green | ✅ | `git ls-files` shows only `.env.example` / `.env.staging.example` / `app/web/.env.example` (templates); no real `.env*` tracked (`app/web/.env.local` with its `VERCEL_OIDC_TOKEN` correctly gitignored). `--check` green; `pnpm check` 0 errors; `pnpm build` OK. |

- **Iterations:** 0 (no fixups needed; all steps passed on first exercise). One *plan* correction (V1b re-scoped to no-regression per R5.3) — no code changed.
- **Verdict:** PASS — human functional verification complete.
- **Verified by:** Agni Eialarasu · **Surface:** Kiro IDE
