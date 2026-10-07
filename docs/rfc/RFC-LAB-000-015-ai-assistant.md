# RFC-LAB-000-015: AI Assistant — "Ask-the-Portfolio"

| Property | Value |
| :--- | :--- |
| **RFC ID** | `RFC-LAB-000-015` |
| **Title** | A grounded natural-language assistant to ask about a project / the portfolio |
| **Author** | Agni Eialarasu (LAB-000 Control Hub) |
| **Status** | 🟡 **Proposed** — RFC + feasibility spike only (`BK-015` / `TSK-061`); **no build this sprint** |
| **Date** | 2026-10-07 |
| **Backlog** | `BK-015` (flagship; P1), SPRINT-12 `TSK-061` (RFC + spike scope) |
| **Builds On** | `RFC-LAB-000-002`/`-003` (relational `data/` masters — the ground truth), `RFC-LAB-000-006`/`-008` (auth / RBAC — data boundaries), `RFC-LAB-000-011` (runtime infra: SvelteKit→Vercel, PocketBase→Railway), `RFC-LAB-000-013` (app-level settings) |
| **Decision Journal** | (to be added if accepted) |

---

## 1. Context & problem statement

`BK-015` is the flagship: let a CTO / Project Owner ask **casual natural-language questions** about a project or the whole portfolio — "how many projects are active?", "which are at risk?", "what shipped in Cetana last sprint?", "who owns LAB-003?" — and get an answer **grounded in the real `data/` masters + repo docs**, not a hallucination.

This RFC does **not** build it. It exists to **de-risk the flagship before any build** by resolving five questions the backlog row names — **index strategy, model, cost, data boundaries, and where it runs** — and to define a **feasibility spike** that proves (or kills) the chosen approach cheaply. Highest value, highest effort ⟹ decide the architecture first.

## 2. The ground truth (verified 2026-10-07 — do not assume)

- **Corpus is small.** The answerable corpus today = **5 `data/` JSON masters** (`portfolio.json` = 6 projects, `users.json`, `memberships.json`, `status.json`, `settings.json`) + **26 markdown docs (~49k words)** + per-project `STATUS.md`/`journal.md`. This is **kilobytes-to-low-megabytes**, not a large corpus — materially simplifies the index decision (see §5.1).
- **`portfolio.json` is structured + typed** (`id`, `slug`, `name`, `archetype`, `owner_id`, `repo_url`, `dev_environment`, `status_source`). Many "portfolio" questions are **structured queries**, not semantic search.
- **The frontend is a pure static SPA.** SvelteKit + `adapter-static` on Vercel — **there is no SvelteKit server runtime** in production. A browser-side LLM call would expose the model key. ⟹ the assistant **cannot** run purely in the frontend.
- **PocketBase can host a custom server route.** `app/pocketbase/pb_hooks/` already runs custom JS (`oauth_github_handle.pb.js`). PocketBase (Go + embedded SQLite, on Railway) is the **only server runtime** we have — and it can hold a secret + expose a custom endpoint. This is the key feasibility unlock for "where does it run."
- **Auth/RBAC exists** (`RFC-LAB-000-006`/`-008`): public read on portfolio data; superuser-only writes. Data boundaries for the assistant inherit this.

## 3. Goals / non-goals

**Goals:** (G1) decide the five architecture questions; (G2) define a cheap, falsifiable **feasibility spike**; (G3) keep the flagship honest — grounded, cited, fail-closed on facts (same governance thesis as the portfolio-QA work in Nexus INTAKE-001).
**Non-goals (this RFC):** building the assistant, any UI, any deploy, choosing a final model vendor contract. Those follow a future Spec **after** the spike.

## 4. The five questions (proposed decisions — ratified/revised by the spike)

### 4.1 Where it runs *(the load-bearing decision)*
**Proposed: a PocketBase custom route (`pb_hooks`) is the assistant's server.** The static SPA calls `POST /api/ask` on PocketBase; the hook does retrieval + the LLM call server-side and returns a grounded, cited answer. Rationale: it is the **only** runtime we have that can hold the model key and run logic; it already hosts custom JS; it keeps the "no second service, no new infra" posture (`RFC-LAB-000-011`). *(Alternative considered: a serverless function on Vercel — adds a second runtime + a second place for secrets/CORS; rejected unless the spike shows PocketBase hooks can't carry it.)*

### 4.2 Index / retrieval strategy
**Proposed: structured-query-first, with light retrieval over docs — NOT a vector DB (yet).** Because the corpus is tiny (§2):
- **Structured questions** ("how many active", "which at risk", "who owns X") → answered **deterministically** from `data/*.json` (fail-closed, cited to the row) — no LLM needed for the fact, only for phrasing.
- **Narrative questions** ("what shipped last sprint", "what's this project about") → light retrieval: the whole relevant doc set is small enough to **keyword-select + stuff into context** (or a trivial embedding over ~26 docs if needed). A heavyweight vector store is **premature** at this corpus size.
- The spike decides whether even that light retrieval is needed or whether structured + a few whole-doc injections suffice.

### 4.3 Model
**Proposed: provider-agnostic, keyed from app-level settings (`BK-012`).** The model id + endpoint are config (a `settings` row / env var), not hardcoded — so the vendor is swappable and the spike can A/B. Start with whatever is cheapest-adequate for grounded Q&A over a tiny corpus. **The decision is the seam (config-driven), not the vendor.**

### 4.4 Cost
**Proposed: cost is bounded by the tiny corpus + structured-first routing.** Most factual questions cost **zero LLM tokens** (answered from `data/`); only narrative questions hit the model, over a small context. The spike must **measure** real per-question cost on a sample set and confirm it's acceptable before any build commitment.

### 4.5 Data boundaries
**Proposed: the assistant answers ONLY over committed, public-read data** (`data/` + repo docs) — the same boundary as the public dashboard (`RFC-LAB-000-008`). No private/superuser data, no secrets, no cross-repo reach (that's a Stage-D-like concern). Fail-closed: if a fact isn't in the grounded data, say so — never invent. Judgment answers ("is this project in trouble?") are **labelled advisory** computed on top of fail-closed facts (mirrors the Nexus INTAKE-001 governance pattern).

## 5. The feasibility spike (what `TSK-061` actually produces — no product build)

A throwaway, time-boxed spike to **prove or kill** §4 before a Spec:
1. **Runtime probe:** stand up a minimal `pb_hooks` route that holds a (test) key and returns a canned LLM round-trip — proves PocketBase can be the assistant's server (§4.1). If it can't, pivot to the Vercel-function alternative and record why.
2. **Grounding probe:** answer 5 representative questions (3 structured, 2 narrative) over the real `data/` + docs — structured deterministically, narrative via context-stuffing — and judge answer quality + citation fidelity (§4.2).
3. **Cost probe:** measure real tokens/cost per question on that sample; extrapolate (§4.4).
4. **Output:** a short spike-findings note (ratify/revise §4.1–§4.5) recorded in the Decision Journal. **No UI, no deploy, no committed assistant** — the spike artifacts are throwaway.
**Spike exit:** either "architecture confirmed → author the build Spec next sprint" or "killed/revised → here's why + the revised approach."

## 6. Scope floor (this RFC + the spike)
- **In:** this decision record + a throwaway feasibility spike that measures the three probes.
- **Out:** the production assistant, any UI, any deploy, a vendor contract, a vector DB, cross-repo answering. All follow a future Spec gated normally **after** the spike.

## 7. Open questions (for the spike / a later Spec)
- OQ-1: Does `pb_hooks` (Goja JS runtime) comfortably make an outbound HTTPS LLM call, or is a tiny Go handler / Vercel function needed? *(spike probe 1)*
- OQ-2: Is structured-first routing enough, or is light doc-embedding worth it even at this corpus size? *(spike probe 2)*
- OQ-3: Which cheapest-adequate model clears the grounded-Q&A bar? *(spike probe 3)*
- OQ-4: Does the assistant read live PocketBase rows or the committed `data/` snapshot (the `VITE_PB_SOURCE` duality from `BK-012`)? Lean: committed snapshot first (simplest, matches the public read boundary).

## 8. Recommendation
**Accept this RFC as the decision of record for the architecture (§4), then run the §5 spike as `TSK-061` — RFC + spike only, no build.** The spike's findings ratify or revise §4 and gate whether `BK-015` graduates to a build Spec in a later sprint. This keeps the flagship honest: decide where it runs and prove it's groundable + affordable **before** spending the high build effort.
