# Automate Staging Deploy — Design

| Property | Value |
| :--- | :--- |
| **Spec ID** | `automate-staging-deploy` (`TSK-059` / `BK-021`) |
| **Decision of record** | Decision Journal **Entry 014** (D49–D52) |
| **Surface** | Kiro IDE (build) — workflow, skill, Makefile, docs |

---

## 1. The model (what we're encoding)

```
 idea ─brainstorm→ plan ─/plan-done(merge Spec)→ /spec-run(build) → /review-pr(gate) ─merge→ MAIN
                                                                                          │
                                                              ┌───────────────────────────┴──────────────┐
                                                              ▼ (auto, on push to main)                   ▼
                                                     Vercel (frontend)                          GitHub Actions → Railway (backend)
                                                     — existing Git integration                 — NEW, path-filtered app/pocketbase/**
                                                              └───────────────┬───────────────────────────┘
                                                                              ▼
                                                     SINGLE REFERENCE ENVIRONMENT ("staging")  ==  `done` is LIVE
```

- **The gate is the merge** (PR review + required CI checks). Everything on `main` is deployable ⇒ auto-deploy is safe.
- **`done` = the merge** (pragmatic, D50). The deploys are *consequences*; a deploy hiccup is a red workflow (ops alert), not a lifecycle failure.
- **Two tiers, symmetric:** frontend (Vercel, already wired) + backend (Railway, this Spec adds it).
- **Separate on-demand path:** `/deploy-adhoc` → any instance, for testing. Not a stage.
- **Hard boundary:** no promotion pipeline, no prod tier — that's ops (`BK-019`, out of scope).

## 2. Backend CI deploy — `deploy-backend.yml` (R1)

Shape (illustrative; executor writes the final file):
```yaml
name: Deploy Backend (Railway)
on:
  push:
    branches: [main]
    paths:
      - 'app/pocketbase/**'
      - '.github/workflows/deploy-backend.yml'
permissions:
  contents: read
concurrency:            # avoid overlapping deploys of the same env
  group: deploy-backend-main
  cancel-in-progress: false
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Railway CLI
        run: npm i -g @railway/cli    # or the official install script — verify current method
      - name: Deploy PocketBase → Railway
        working-directory: app/pocketbase
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: railway up --service <staging-service> --ci   # reuse railway.json builder pin
```
- **Token:** `secrets.RAILWAY_TOKEN` — a project/service token set once in GitHub → Settings → Secrets and variables → Actions. (One-time [HUMAN]; the enabler.)
- **Service targeting:** a project token scopes to the project; pass/link the specific staging service. Executor verifies the exact `railway up` flags for non-interactive CI against current Railway CLI docs (the CLI evolves — do not assume).
- **Failure = ops alert (R1.4):** the job goes red with logs; no rollback, no effect on the merged commit. Optionally surface via the existing notification path (out of scope to build here).
- **Path filter (R1.1, V2):** only `app/pocketbase/**` (+ the workflow file) — docs/frontend-only merges skip it.

## 3. `/deploy-adhoc` — on-demand dev tool (R3)

- **Reuse, don't rebuild:** `scripts/deploy.sh` already does backend/frontend/all against whatever `.env.*` it's pointed at. The change is a **thin parameterization**: `make deploy-adhoc ENV=<file>` sets `ENV_FILE=<file>` (the script already honors `ENV_FILE`), then runs the chosen sub-command.
- **Skill `deploy-adhoc/SKILL.md`:** frames it as a **developer testing tool** — deploy to a throwaway/other instance; NOT "release," NOT a lifecycle phase. Includes: the one-time [HUMAN] checklist (`scripts/deploy.sh checklist`), the `verify-bundle` guarantee for any frontend, and the secrets-discipline note (gitignored env file, CLI-token auth).
- **Boundary reminder in the skill:** "The staging pipeline is the *merge*. This is for ad-hoc instances only."

## 4. Makefile disambiguation (R4)

- Add `deploy-adhoc` (manual, any instance). Reconcile the existing `deploy-staging`:
  - **Option (lean):** keep `deploy-staging` as a documented **manual re-deploy of the staging env** (occasionally useful), but its `help` text states clearly that **the normal staging deploy is automatic on merge** — this target is a manual override, not "the pipeline." Add `deploy-adhoc ENV=<file>` as the ad-hoc-instance path.
- `make help` + comments reference Entry 014's two-path model. Executor picks the cleanest naming; the requirement is that "the staging pipeline is a manual make target" is no longer implied.

## 5. Placeholder refresh (R5) + docs (R6)

- **`make validate-staging`** + `status-staging`/`validate-staging` skills: replace "GCP … pending org transfer" with the Railway (backend) + Vercel (frontend) reality, or demote with a note if redundant.
- **`developer-guide.md` §9A:** add "The Deployment Model" — `main` = single reference env; merge deploys both tiers; the PR gate is the deploy gate; `done` = live (pragmatic); the two paths; the explicit ops boundary. Update the existing §9A CLI content to fit (it stays valid as the on-demand/ad-hoc mechanics).
- **`RFC-LAB-000-012`:** add a header/status note — **reference ops guidance**, not part of the lifecycle contract (Entry 014, D52). Append-style note; do not rewrite its decisions.

## 6. Secrets & gates (R7)

- `RAILWAY_TOKEN` ONLY in GitHub Actions secrets. `git grep` for token patterns must be clean.
- New workflow is additive; the required checks (`ci-validate.yml`) that gate `main` are untouched. The deploy workflow is **not** a required check (a deploy failure must not block future merges — it's an ops signal).
- Everything lands via branch → PR → `/review-pr` (`RFC-LAB-000-004`).

## 7. Open questions (resolve during build)
- **OQ-1:** exact non-interactive `railway up` invocation + service selection for CI (verify vs current Railway CLI docs — capability, not assumption).
- **OQ-2:** whether to keep `make deploy-staging` at all vs. fold entirely into `deploy-adhoc` (naming — executor's call, satisfying R4.1).
- **OQ-3:** whether the deploy-failure ops alert should notify anywhere now, or just be the red check (lean: red check only; notification is future ops).
