# Spike — PocketBase 0.40 OAuth-through-Railway-proxy (BK-018)

| Property | Value |
| :--- | :--- |
| **Spike ID** | `spike-bk018-pb040-oauth` |
| **Backlog** | `TSK-055` (`BK-018`, SPRINT-10) |
| **Type** | **Investigation spike** — confirm a root cause + choose a fix; **not** a build (progressive formality, `RFC-LAB-000-009` §5) |
| **Status** | 🔬 Proposed |
| **Deliverable** | A **documented finding** (Decision Journal entry + likely an `RFC-LAB-000-011` amendment) → *then* a focused fix Spec |
| **Related** | `RFC-LAB-000-011` (deployment; PB pinned 0.28.4), `RFC-LAB-000-006`/`-008` (OAuth), M5 REPORT (`mvp-m5-deploy`) |

---

## 1. Why this is a spike, not a Spec

The **symptom** is known but the **root cause is unconfirmed**, so writing EARS acceptance criteria for a fix now would be guessing. This spike's job is to **confirm the diagnosis and choose the fix**; the fix itself becomes a small Spec afterward, grounded in evidence. Lightweight by design — the output is a *finding*, not shipped code (a throwaway test branch is fine; nothing merges to prod from the spike itself).

## 2. What we know (from the M5 REPORT — of record)

- **Symptom:** on **PocketBase 0.40.x behind Railway's HTTPS proxy**, the SDK's all-in-one OAuth2 popup fails: `/api/realtime 400 Invalid realtime client`.
- **Does NOT reproduce locally** — local also runs 0.40.4 and OAuth works. ⇒ **not** a simple SDK↔server version gap.
- **Suspected trigger:** 0.40's realtime/OAuth handshake through a **cross-origin, proxied** deploy (the all-in-one flow opens an SSE `/api/realtime` channel to receive the OAuth result; something about Railway's proxy + cross-origin breaks it).
- **Current workaround:** prod pinned to **0.28.4** (proven-good; the older flow doesn't hit this).
- **Leading fix hypothesis (H1):** switch to the **redirect-based `authWithOAuth2Code` flow**, which does **not** need the realtime SSE channel — so the proxy/CORS issue can't bite.

## 3. Hypotheses to test (in order)

- **H1 (leading) — Redirect flow fixes it:** replacing the all-in-one `authWithOAuth2({provider})` popup with the **redirect-based `authWithOAuth2Code`** flow lets OAuth complete on 0.40 through Railway (no SSE channel). *If confirmed → the fix is "switch the flow + un-pin to 0.40."*
- **H2 — Proxy/realtime config:** the realtime SSE channel *can* be made to work through Railway (a Railway proxy setting, a PocketBase CORS/`trustedProxy`/`X-Forwarded-*` setting, or the SDK's `realtime` origin). *If trivial → keep the popup flow, fix config.*
- **H3 — Genuine 0.40 regression/incompat:** if neither, characterize it precisely (is it 0.40-specific? which sub-version introduced it?) and decide: stay pinned (document why) or report upstream.

## 4. Method (the investigation)

1. **Reproduce (precondition — needs a live 0.40 Railway instance):** deploy PocketBase **0.40.4** on Railway (the M5 stack, un-pinned), confirm the `/api/realtime 400 Invalid realtime client` on OAuth sign-in from the Vercel app. *Establish the failing baseline.*
2. **Confirm the mechanism:** inspect the failing request — is it the SSE `/api/realtime` subscribe that 400s? cross-origin? Check PocketBase logs + browser network. Pin down *why* the realtime client is "invalid" through the proxy (origin mismatch? missing forwarded headers? SSE buffering?).
3. **Test H1:** implement the redirect-based `authWithOAuth2Code` flow in a throwaway branch; deploy to the 0.40 Railway instance; verify sign-in completes end-to-end (incl. the `github_handle` hook + owner-write path still work).
4. **If H1 fails → test H2:** try the proxy/CORS/realtime config route; note effort.
5. **Record the finding** (§6) regardless of outcome.

## 5. Acceptance (spike is "done" when)

- The **root cause is confirmed** (not just the symptom) — a one-paragraph mechanism explanation backed by the reproduction.
- A **fix direction is chosen** (H1 / H2 / H3) with evidence, including whether it lets prod move **off 0.28.4 to 0.40+**.
- The **finding is documented**: a Decision Journal entry + (if it changes the deployment decision) an `RFC-LAB-000-011` amendment, and a **follow-on fix Spec is scoped** (or, for H3, a documented decision to stay pinned).
- **No prod change from the spike** — the fix ships via its own Spec through the normal gate.

## 6. Deliverable (the finding — fill at spike end)
- **Root cause:** ⟨confirmed mechanism⟩
- **Chosen fix:** ⟨H1 / H2 / H3⟩ — ⟨rationale + evidence⟩
- **Prod impact:** ⟨can we un-pin to 0.40? how?⟩
- **Next:** ⟨fix Spec id/scope, or "stay pinned" decision⟩ · Journal entry · RFC-011 amendment (if applicable)

## 7. Scope & guardrails
- **In:** reproduce, diagnose, validate a fix direction, document.
- **Out:** shipping the fix to prod (that's the follow-on Spec, human-gated); refactoring OAuth beyond what the diagnosis requires; touching RBAC/writes (M3–M4, done).
- **Precondition:** a live **0.40 Railway** instance (the bug doesn't reproduce locally) — spike can't be completed purely locally.
- **Non-destructive:** use a throwaway/staging instance; do **not** un-pin the *live* prod backend until the fix Spec ships.

## 8. Open questions
1. **Staging vs. touching prod:** stand up a *separate* 0.40 Railway instance for the spike, or a throwaway on the same project? *(Leaning: separate/throwaway — never destabilize live prod for an experiment; ties to `BK-017` staging automation.)*
2. **Redirect-flow UX:** `authWithOAuth2Code` implies a full-page redirect vs. the popup — acceptable UX change? *(Leaning: yes, redirect is standard + more robust; confirm at fix-Spec time.)*
