# Fix BK-018 — Redirect OAuth + Un-pin — Tasks

> Ordered plan for `/spec-run` (Build). Execute on **Kiro IDE** + a **throwaway 0.40 Railway** instance (bug/fix only manifest behind the proxy). Do NOT merge; open a PR, emit the Human Verification Plan, STOP in `IN_VERIFICATION`. **Prod (0.28.4) stays untouched.**

## Execution header (self-describing — read by `/spec-run`)

| Field | Value |
| :--- | :--- |
| **Spec id** | `fix-bk018-oauth-redirect` |
| **Kickoff (IDE one-liner)** | `/spec-run fix-bk018-oauth-redirect` |
| **Surface** | Kiro **IDE** (code) + throwaway **0.40 Railway** (verify) — via RFC-012 CLI + `verify-bundle` |
| **Branch to create** | `feat/fix-bk018-oauth-redirect` (off up-to-date `main`, per `RFC-LAB-000-004`) |
| **Base for PR** | `main` |
| **Preflight** | Requirements §0 (P1–P6; **P1 needs a live 0.40 Railway instance**; **P6 non-destructive — don't touch live prod**) + task **T0** |
| **Self-validation target** | `requirements.md` EARS R1–R6 |
| **Human Verification Plan** | `requirements.md` §4b (V1–V8; V1 0.40-sign-in-works + V6 bundle-verified-first + V7 prod-untouched) |
| **On completion** | Open PR via `gh api`, emit the Verification Plan, STOP → `/verification-done` → `/review-pr` (never merge) |
| **Executor role** | Delegated-agent / onboarded-dev |

---

- [ ] **T0 — Preflight (gate — STOP on any ❌)**
  - Surface=IDE; clean tree; branch off fresh `main`; this Spec on `main` (merge-first). Baseline green (validators + `pnpm check`/`build`).
  - **P1:** a throwaway/staging **0.40 Railway** instance is available (or stand one up per RFC-012) — the fix can't be verified purely locally. If absent ⇒ STOP with setup steps (don't fabricate).
  - **P6:** confirm the intent — **do NOT modify live prod (0.28.4)**; all testing on the throwaway.
  - _Refs: §0._

- [ ] **T1 — Redirect OAuth: start half (`auth.svelte.ts`)**
  - Rewrite `signInWithGitHub()` to the redirect start: `listAuthMethods()` → GitHub provider `authURL`/`codeVerifier`/`state`; stash `codeVerifier`+`state` in `sessionStorage`; `window.location.assign(authURL + redirectURL)` where `redirectURL = ${origin}/oauth/callback`.
  - _Refs: R1.1, R1.3, design §2/§3._

- [ ] **T2 — Redirect OAuth: callback half (`auth.svelte.ts` + callback route)**
  - Add `completeOAuthCallback()`: read `code`+`state`, **verify `state`** (R1.2 CSRF), `authWithOAuth2Code('github', code, codeVerifier, redirectURL)`, then reuse M2's post-auth resolve (`loginFromMeta`/`#resolve`/`#authed`/`LINK_KEY`).
  - Add `app/web/src/routes/(auth)/callback/+page.*` (client-side; not under `(member)`): on mount call it, show "signing in…", redirect to dashboard on success, clear error + retry on failure.
  - _Refs: R1.2, R1.4, R2.1, design §3/§4._

- [ ] **T3 — Preserve the M2→M4 loop (no regression)**
  - Verify `github_handle` still populates (hook fires on code exchange), account-link resolves the seeded owner, owner-write works, RBAC/guard/sign-out/persistence intact. Adjust only if the meta shape differs.
  - _Refs: R2.1–R2.4, design §5._

- [ ] **T4 — Un-pin the backend (`Containerfile`)**
  - `ARG PB_VERSION` `0.28.4` → current **0.40.x**; replace the workaround comment with the redirect-flow rationale (ref RFC-011 §4.5). Keep `pb_hooks/`.
  - _Refs: R3.1, design §5._

- [ ] **T5 — Deploy to throwaway 0.40 + bundle-verify (RFC-012 flow)**
  - Deploy PB 0.40.x to the throwaway Railway (CLI); seed. Build SPA with `VITE_PB_URL=<throwaway>`; **`make verify-bundle EXPECTED=<throwaway> FORBIDDEN=<prod>`** BEFORE any live test (the anti-false-negative gate). GitHub OAuth app callback includes `${origin}/oauth/callback` ([HUMAN] config, R4.1).
  - _Refs: R5.1, R4.1, design §6._

- [ ] **T6 — Quality gates + no-regression**
  - `pnpm --dir app/web check && build && lint`; `make validate-local`; `generate_status_json.py --check`. Local dev unaffected.
  - _Refs: R6._

- [ ] **T7 — Commit, open PR, emit Human Verification Plan, STOP**
  - Branch `feat/fix-bk018-oauth-redirect`; semantic commit referencing `TSK-055` / `BK-018`.
  - Open PR into `main` via `gh api`; CI green; emit §4b plan (V1–V8; V1/V6/V7 headline); STOP in `IN_VERIFICATION`. **Never merge; prod stays 0.28.4.**
  - _Refs: R-all, `RFC-LAB-000-009` §3.2._

- [ ] **T8 — After human verification passes: `/verification-done`**
  - Human runs V1–V8 on the throwaway 0.40 (esp. V1 sign-in works, V2 no `/api/realtime`, V6 bundle-verified-first, V7 prod-untouched); fixes ride the same PR; on pass, `/verification-done` → `IN_REVIEW` → `/review-pr`.
  - _Refs: `RFC-LAB-000-009` §3.2._

---

### Governance lockstep reminder (Record, after merge)
Note in CHANGELOG (`TSK-055`, `BK-018` fixed — redirect OAuth, PB un-pinned to 0.40+). This makes the **codebase** 0.40-ready and correct. **Cutting *live prod* over to 0.40** is the separate **`BK-019`** promotion (casual→qualified→prod), gated on its own. Prod stayed 0.28.4 throughout this Spec.
