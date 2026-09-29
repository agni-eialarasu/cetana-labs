# Spec REPORT — `spike-bk018-pb040-oauth`

> **Purpose.** The lightweight human **sign-off** artifact of the sprint lifecycle
> (`RFC-LAB-000-009` §3 Phase 5, §9). Complements — does not duplicate — the Decision
> Journal (*why*) and CHANGELOG (*what*). This is a **spike** REPORT: the deliverable is a
> documented finding, not shipped code, so §2/§4 are adapted (the "Human Verification Plan"
> is the spike's reproduction method; there is no feature PR to merge — the fix ships via a
> separate Spec).

| Property | Value |
| :--- | :--- |
| **Report for** | Spec `spike-bk018-pb040-oauth` (investigation spike) |
| **Executor role** | Lead-paired (human + AI; human drove the Railway/Vercel/browser, AI drove repo/build/analysis) |
| **Surface(s)** | IDE (reproduce, build, diagnose) |
| **Date** | 2026-09-26 |
| **Related** | RFC: `RFC-LAB-000-011` (§4.5 amendment) · Epic/Task: `BK-018` / `TSK-055` (SPRINT-10) · Decision Journal: Entry 011 (D42–D43) · Branch: `spike/bk018-pb040-oauth` (test rig — **not for merge**) |

---

## 1. Outcome (one paragraph)
The `BK-018` spike reproduced and root-caused the PocketBase-0.40-on-Railway GitHub-OAuth failure. On a genuine, bundle-verified 0.40 backend, sign-in fails at `POST /api/realtime` with `400 "Missing or invalid client id"`: PocketBase 0.40's realtime SSE handshake is incompatible with Railway's edge proxying of long-lived SSE, and the SDK's *popup* OAuth flow depends on that realtime channel to receive its callback. The chosen fix is **H1 — switch the frontend to the redirect-based `authWithOAuth2Code` flow**, which never opens `/api/realtime` and therefore **un-pins prod from 0.28.4 to 0.40+**. The finding is recorded (SPIKE.md §6, Decision Journal Entry 011, RFC-011 §4.5); the fix ships via its own Spec (`fix-bk018-oauth-redirect`). No prod change was made by the spike.

## 2. Definition of Done — met? (the spike's acceptance bar — SPIKE.md §5)

| DoD item (SPIKE.md §5) | Met? | Evidence |
| :--- | :---: | :--- |
| Root cause **confirmed** (mechanism, not symptom) | ✅ | SPIKE.md §6; reproduced `POST /api/realtime` → 400; `GET` SSE returns `PB_CONNECT`+200 but the subscribe is rejected through the proxy |
| A **fix direction chosen** with evidence, incl. can-we-un-pin | ✅ | H1 (`authWithOAuth2Code`); redirect flow avoids `/api/realtime` entirely → un-pins to 0.40+ |
| Finding **documented** (Journal + RFC-011 amendment) | ✅ | Decision Journal Entry 011 (D42–D43); RFC-011 amendment banner + §4.5 + §9 risk row |
| **Follow-on fix Spec scoped** | ✅ | `fix-bk018-oauth-redirect` scoped (swap call site, preserve `github_handle` hook + owner-write R3, un-pin Containerfile) — not yet authored |
| **No prod change from the spike** | ✅ | All testing on a throwaway Railway instance; live prod stays 0.28.4 |

**Verdict:** `DONE` — the spike's acceptance criteria are all met.

## 3. Deferred / carried forward (scope honesty)
- **The actual fix is NOT shipped** — the spike only chose the direction. Ships via `fix-bk018-oauth-redirect` (un-pins prod to 0.40+) through the normal PR + verify gate. Tracked under `BK-018` follow-through.
- **H2 (make SSE survive Railway's proxy)** not investigated in depth — deliberately rejected on design grounds (fragile dependency on the critical sign-in path); not re-opened unless H1 proves infeasible.
- **Throwaway teardown** — the throwaway Railway instance + spike Vercel preview env var can be torn down; `spike/bk018-pb040-oauth` stays unmerged.

## 4. Verification Log — spike reproduction (the "did we actually prove it" record)
> For this spike the "Human Verification Plan" is the reproduction method (SPIKE.md §4).
> Recorded honestly, including the two **invalid** attempts — the credible finding is the one
> that survived that scrutiny.

### Verification Log — 2026-09-26 (spike branch `spike/bk018-pb040-oauth`; no PR — spike)
| Plan step | Result | Finding / correction |
| :--- | :---: | :--- |
| V1 — stand up a live 0.40 Railway throwaway + GitHub OAuth | ✅ | `truthful-prosperity-staging.up.railway.app` health 200; OAuth advertised on `users`; confirmed 0.40 error-envelope shape |
| V2 — wire a frontend to the throwaway and sign in (attempt 1: Vercel preview) | ❌→✅ | **Invalid test**: preview showed 6 projects + OAuth "success" — but throwaway has **no `projects` collection** (`Missing collection context`); 6 projects only exist on prod 0.28.4 ⇒ preview had baked in the **prod** `VITE_PB_URL`. Root cause: Vercel env scoping (Prod+Preview) + Secret→Config lock + Vite build-time inlining |
| V2' — fix the wiring (attempt 2: Vercel CLI env, branch-scoped, redeploy) | ❌→✅ | CLI deploy from `app/web/` failed (Root Directory doubled); rerun from repo root promoted to **Production** (aliased `cetana-labs.vercel.app`) + Deployment Protection blocked anon verification ⇒ still couldn't prove which backend was hit |
| V3 — deterministic local build + **bundle verification** | ✅ | Built locally with `VITE_PB_URL=<throwaway>`; grep of `build/`: throwaway URL ×1, **prod URL ×0** — provably wired to 0.40 |
| V4 — sign in against the verified-0.40 build; capture `/api/realtime` | ✅ | Reproduced: `POST /api/realtime` (payload `{clientId, subscriptions:["@oauth2"]}`) → **400 Bad Request**; page → 500 |
| V5 — confirm the mechanism | ✅ | `GET /api/realtime` through Railway returns `PB_CONNECT` + `clientId` (200); manual `POST` with any clientId → `404 "Missing or invalid client id"` ⇒ proxy doesn't preserve SSE affinity 0.40 requires |

- **Iterations:** 3 (two invalid reproduction attempts before a bundle-verified valid one). No code fixups — spike produces a finding, not shipped code.
- **Verdict:** `PASS — reproduction valid, root cause confirmed, fix direction chosen.`
- **Verified by:** Agni Eialarasu · **Surface:** Kiro IDE

## 5. Human gate
- No feature PR — spike deliverable is the finding. Governance docs (SPIKE.md §6, Journal Entry 011, RFC-011 §4.5) fast-path to `main`.
- The fix (`fix-bk018-oauth-redirect`) goes through the full `/review-pr` gate when authored.
- STOP-and-hold raised: the false-negative catch (attempt 1) — held, re-tested deterministically rather than concluding "can't reproduce."

## 6. AIDLC spike notes
- **Method that worked:** clean split — AI owned repo inspection, local build, bundle verification, backend curl probes, and diagnosis; human owned the Railway service, OAuth config, Vercel, and browser sign-in. The AI's cross-check of the two backends is what caught the false negative.
- **Lesson to fold back:** *verify the artifact, not the setting.* Build-time-inlined config (Vite `VITE_*`) must be confirmed in the built bundle before trusting any live-test result — a preview can silently point at the wrong backend. Worth a note in `developer-guide.md` §9 / `BK-017` staging automation (auto-assert the baked-in URL).
- **Environment note:** this machine uses **Homebrew** node/pnpm (node 26.8.2, pnpm 10.27.0), not nvm — the `tech` steering's nvm note did not apply here.

## 7. Findings & suggestions (spike close)

**Findings**
1. **Root cause (confirmed):** PB 0.40's realtime handshake needs SSE connection affinity that Railway's edge proxy does not preserve; the `POST /api/realtime` subscribe is rejected (`400/404 "Missing or invalid client id"`). The popup OAuth flow depends on this channel, so sign-in 500s. Not a version-pairing bug (works locally, no proxy); absent on 0.28.4 (older, tolerant realtime path).
2. **The 0.28.4 pin is the *only* thing keeping prod off latest PB** — and it exists solely because of this proxy/realtime break.
3. **Two reproduction attempts were invalid** (preview silently hit prod 0.28.4) before a bundle-verified local build gave a valid test.

**Suggestions**
1. **Ship H1 (`authWithOAuth2Code` redirect flow)** as `fix-bk018-oauth-redirect`: swap `signInWithGitHub()` in `app/web/src/lib/auth.svelte.ts`, preserve the `github_handle` hook + owner-write resolution (`RFC-LAB-000-008` M3–M4, R3), then un-pin `app/pocketbase/Containerfile` to 0.40.x. Verify OAuth end-to-end on a 0.40 instance before un-pinning prod.
2. **Do not pursue H2** (proxy/SSE tuning) unless H1 proves infeasible — it leaves a fragile SSE dependency on the sign-in path.
3. **Fold the "verify the baked-in URL" check into staging automation (`BK-017`)** so a mis-scoped `VITE_PB_URL` can't produce a misleading test again.
4. **Sequence:** `BK-018` fix → then `BK-019` prod cutover (which depends on running latest PB) → `BK-017` automation can land alongside.
5. **Rotate the known test-user passwords** seeded on local/prod (`TestPass2026!`) as part of the cutover hardening (`BK-019`).

## 8. Sign-off
- **Signed:** Agni Eialarasu (Lead) — 2026-09-26
- Decision Journal entry created? **yes** — Entry 011 (D42–D43)
- Release tagged? n/a — spike; the fix Spec + `/sprint-done` handle any release.
