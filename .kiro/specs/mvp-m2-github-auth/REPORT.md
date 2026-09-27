# Sprint / Spec REPORT — Spec `mvp-m2-github-auth`

> Human sign-off artifact for the AIDLC Spec run (`RFC-LAB-000-009` §3 Phase 5).
> Thin and sign-off-only; complements the Decision Journal (*why*) and CHANGELOG (*what*).

| Property | Value |
| :--- | :--- |
| **Report for** | Spec `mvp-m2-github-auth` |
| **Executor role** | Delegated-agent (full Spec — `RFC-LAB-000-009` §5) |
| **Surface(s)** | Web (Scope — Spec authored) · IDE (execute — `/spec-run`) |
| **Date** | 2026-09-27 |
| **Related** | RFC(s): `RFC-LAB-000-006` (auth/RBAC), `RFC-LAB-000-008` (MVP §6) · Epic/Task: `BK-011` / `TSK-049` · PR(s): #31 |

---

## 1. Outcome (one paragraph)
Added identity to the Sleek UI: GitHub OAuth sign-in via the PocketBase JS SDK, a reactive Svelte-5 auth store, account-linking to the seeded portfolio owner by `github_handle`, an auth-reactive header, and a route-guard pattern (`(member)` group) — all client-side on the static SPA. Sign-in only; no RBAC enforcement (M3), writes (M4), or deploy (M5). The M1 read + snapshot-fallback path is unchanged.

## 2. Definition of Done — met? (the gate summary)

| DoD item (R#) | Met? | Evidence |
| :--- | :---: | :--- |
| R1 — GitHub OAuth sign-in/out flow | ✅ | Human-verified round-trip (V1/V4) after the 403 + reactivity fixes |
| R2 — Reactive auth store + rehydrate | ✅ | Live header update (no reload) + persistence across refresh (V5) |
| R3 — Link-by-`github_handle`, no auto-provision | ✅ | Seeded owner resolves (V2); unknown login → unlinked, no row created (V3) |
| R4 — Auth-reactive UI, public never blocked | ✅ | Header reacts; dashboard renders for anon (V6) |
| R5 — Route guard + placeholder | ✅ | `(member)/account` redirects when signed out (V6) |
| R6 — Superuser path preserved | ✅ | PB admin login intact (V7) |
| R7 — Secrets in PB admin; `.env.example` keys only | ✅ | No frontend secret; docs updated |
| R8 — Gates green | ✅ | `pnpm check`/`build`/`lint` + `make validate-local`; CI green |

**Verdict:** `DONE`

## 3. Deferred / carried forward (scope honesty)
- RBAC rule enforcement / field-tiering (M3); owner write path (M4); deploy + prod OAuth redirect (M5 / `RFC-LAB-000-011`).
- Auto-provisioning pending `users` records for unknown GitHub logins (`RFC-LAB-000-006` OQ-1) — still deferred.
- Note: M2's `users.createRule=""` allows OAuth self-registration (auth record only, no ownership); M3 should revisit whether to tighten this alongside the RBAC matrix.

## 4. Corrections made during verification (append-only)

The human-verify loop found **three** issues; all fixed on this PR (Single-PR rule) and re-verified:

- **`735a16d` — OAuth 403 (blocked sign-in).** GitHub authorized, but `POST /auth-with-oauth2` returned `403 Only superusers can perform this action` — the `users` collection had `createRule=null` (superuser-only), so PB refused to create the auth record; `seed_id`/`name`/`role` were also `required`, which would reject an unlinked identity. Fixed in `pb_provision.py`: `createRule=""` (public OAuth sign-in — grants no ownership, resolved separately by handle) + the three fields optional. Also fixed the provisioner's merge to update managed field props in place (it previously only appended new fields, so the `required` change wouldn't have converged). *(Diagnosed from PB admin Logs.)*
- **`0a5ba36` — reactivity + wrong link.** (a) Header didn't update until a manual reload — the UI read `pb.authStore.isValid` directly (non-reactive); fixed by backing auth state with a reactive `$state` flag flipped on sign-in/out + `onChange`. (b) A seeded owner showed as "unlinked" — PocketBase creates a *separate* auth record per GitHub identity (empty `github_handle`), so reading the handle off that record never matched; fixed by capturing the GitHub login from the OAuth `meta` and resolving the seeded owner via a `github_handle` filter query (case-insensitive), persisted for rehydrate.
- **`c13102b` — UI alignment.** The auth control hugged the browser edge; wrapped it in a `mx-auto max-w-content` container matching the page body so it aligns to the body's right edge.

## 5. Verification Log — human functional verification

### Verification Log — 2026-09-27 (PR #31)
| Plan step | Result | Finding / correction |
| :--- | :---: | :--- |
| V1 — Sign in | ❌→✅ | First attempt failed (403, `735a16d`); after fix, GitHub OAuth returns signed-in. Header didn't update live until `0a5ba36`. |
| V2 — Linked identity | ❌→✅ | Initially showed "unlinked" for a seeded owner; fixed link-by-handle resolution (`0a5ba36`) → resolves to the `usr-eialarasu` seeded record. |
| V3 — Unlinked path | ✅ | Unknown GitHub login → authenticated-but-unlinked, clear non-error state, no new seeded row. |
| V4 — Sign out | ✅ | Reverts to anonymous live (no reload) after the reactivity fix. |
| V5 — Persistence | ✅ | Refresh while signed in → stays signed in (authStore rehydrates + link re-resolves). |
| V6 — Public never blocked / guard | ✅ | Anonymous dashboard renders fully; `(member)/account` redirects to `/` when signed out. |
| V7 — Superuser intact | ✅ | PB admin UI login still works. |
| V8 — Gates | ✅ | `pnpm check`/`build`/`lint` + `make validate-local` green; CI green. |
| *(UI)* Alignment | ✅ | Auth control aligns to the page body right edge (`c13102b`). |

- **Iterations:** 3 fixups pushed to this PR during verification: `735a16d` (OAuth 403), `0a5ba36` (reactivity + link-by-handle), `c13102b` (auth-bar alignment).
- **Verdict:** PASS — human functional verification complete.
- **Verified by:** Agni Eialarasu · **Surface:** Kiro IDE

> **Note:** OAuth is inherently human-verified (browser popup + GitHub consent) — the executing agent could not perform the round-trip itself, and the PB admin **Logs** view was the key diagnostic that pinned the 403 root cause. This is the value of the human-verify phase: three real issues (a blocking server rule, a reactivity bug, a mislink) surfaced only under live exercise, not in the agent's self-validation (which was type/build/lint green throughout).

## 6. Human gate
- PR: #31 — verification PASS recorded; state **IN_REVIEW**, ready for `/review-pr 31` · CI green (Validate Portfolio ✅, Build Sleek UI ✅) · squash-merged: no (awaiting gate).

## 7. Sign-off
- **Signed:** Agni Eialarasu (Lead) — 2026-09-27 — human functional verification PASS (V1–V8).
- Release tagged? n/a — `/sprint-done` (SPRINT-09) will tag at sprint close.
- Note: M2 unblocks M3 (RBAC enforcement), M4 (owner writes), M5 (authenticated deploy).
