# AI Assistant "Ask-the-Portfolio" (BK-015) — Requirements

| Property | Value |
| :--- | :--- |
| **Spec ID** | `ask-the-portfolio` |
| **Feature** | A grounded natural-language assistant that answers questions about a project / the whole portfolio ("how many active?", "which at risk?", "who owns LAB-003?", "what shipped last sprint?") from the real `data/` masters + repo docs — fail-closed, cited, never hallucinated. |
| **Backlog** | `BK-015` (flagship, P1) |
| **RFC** | [`RFC-LAB-000-015`](../../docs/rfc/RFC-LAB-000-015-ai-assistant.md) — architecture decision of record (§4.1–§4.5) |
| **Spike** | `TSK-061` COMPLETE — Decision Journal **Entry 032 / D77** ratified §4.1–§4.5 (one revision: §4.2 narrative retrieval selects by section/id). This Spec builds what the spike proved. |
| **Work class** | **Sprint deliverable** (business functionality a user exercises) → **FULL gate**: 4 automated gates + PR + `/review-pr` scorecard + Gate 5 recording + human merge. |
| **Executor** | **Kiro IDE** (escalation — security-sensitive: holds the LLM key server-side, new public endpoint, data-boundary enforcement) per `RFC-LAB-000-014`. *(Advisory — the sprint owner picks the runner at execution time.)* |
| **Depends on** | Spike D77 (runtime ratified). Model key provisioned in Railway service env (NOT chat/repo). |

---

## 1. Introduction

`BK-015` is the flagship: let a CTO / Project Owner ask casual natural-language questions about the portfolio and get an answer **grounded in the committed `data/` masters + repo docs**, never a hallucination. The spike (`TSK-061` / D77) confirmed the architecture: a **PocketBase `pb_hooks` custom route** (`POST /api/ask`) does retrieval + the LLM call server-side via `$http.send`, structured-first (most facts answered from `data/` with zero LLM), fail-closed on grounding, over the public-read data boundary only.

**This Spec builds the server-side assistant engine + its endpoint.** The web UI is a separate consumer (`BK-040` Stage B); this Spec delivers the `/api/ask` contract both the (future) UI and any client call.

## 0. Preconditions (preflight — verify BEFORE building)
- **P1 — Spike ratified (hard):** D77 confirms `$http.send` is the runtime, structured-first works, cost is bounded, fail-closed holds. Build to the ratified §4, including the §4.2 revision (section/id-anchored narrative retrieval).
- **P2 — Key provisioned out-of-band (hard):** the LLM API key SHALL exist in the Railway PocketBase service env (e.g. `LLM_API_KEY`) + the model id in app-level settings (`BK-012`). The key SHALL NOT appear in the repo, in chat, or in any committed file. No key ⟹ the route fail-closes (R-NF-3).
- **P3 — Public-read boundary (hard):** the assistant reads ONLY committed, public-read data (`data/*.json` + repo docs), the same boundary as the public dashboard (`RFC-LAB-000-008`). No private/superuser data, no secrets.

## 2. Current-state facts (verified — spike D77)
- PocketBase JSVM ships `$http.send({url,method,body,headers,timeout})` → `{statusCode, body, json, headers, cookies}`; **no SSE/streaming** (blocks, returns whole body). ⟹ `/api/ask` is **request/response**, not streamed tokens.
- Corpus is tiny: 5 `data/` JSON masters (6 projects) + ~26 docs. Structured questions answerable deterministically with **zero LLM**; narrative questions need light retrieval + one model call.
- Spike measured ~$0.00035/narrative question on `gpt-4o-mini`; structured = $0.
- Spike revision: naive whole-doc truncation fed the wrong slice → a false "I don't know". Narrative retrieval MUST select by section/sprint-id anchor.

## 3. Requirements (EARS acceptance criteria = Definition of Done)

### R1 — The endpoint
- **R1.1** The system SHALL expose `POST /api/ask` as a PocketBase `pb_hooks` route (`routerAdd`) accepting `{ question: string }` and returning `{ answer: string, citations: string[], grounded: boolean }`.
- **R1.2** The route SHALL be reachable by the static SPA (CORS/same-origin per the existing app) and SHALL require no auth for public-read questions (R3 boundary). *(Anonymous-capable; a sign-in gate is a later product call.)*
- **R1.3** WHEN the request body is missing `question` or it is empty, the system SHALL return a 400 with a clear error, not a model call.

### R2 — Routing & retrieval (structured-first)
- **R2.1** WHEN a question maps to a structured fact over `data/*.json` (counts, status filters, ownership, metadata), the system SHALL answer **deterministically from the data with ZERO LLM call**, citing the source row(s).
- **R2.2** WHEN a question is narrative (requires docs), the system SHALL select the relevant doc slice **by section/sprint-id anchor** (NOT blind whole-doc truncation — D77 revision), stuff it as context, and call the LLM.
- **R2.3** The system SHALL include, with every answer, **citations** naming the source doc(s)/row(s) the answer rests on (R-GOV grounding).

### R3 — Data boundary (fail-closed)
- **R3.1** The assistant SHALL read ONLY committed public-read data (`data/*.json` + repo docs). It SHALL NOT read private/superuser collections, secrets, or env values beyond the model config.
- **R3.2** WHEN a fact is not present in the grounded data, the system SHALL say so explicitly and SHALL NOT invent an answer. *(The spike's Q4 fail-closed behavior is the contract.)*
- **R3.3** Judgment answers ("is this project in trouble?") SHALL be labelled **advisory** and computed on top of fail-closed facts.

### R4 — Model config (the seam)
- **R4.1** The model id + endpoint SHALL be read from config (app-level settings `BK-012` / env), NOT hardcoded — the vendor is swappable (`RFC-LAB-000-015` §4.3).
- **R4.2** The LLM API key SHALL be read from the Railway service env only; it SHALL NEVER be committed, logged, or returned in a response.

### R5 — Non-functional
- **R5.1 (fail-closed on infra)** WHEN the model key is absent or the LLM call errors/times out, the route SHALL return a graceful "assistant unavailable" (or the deterministic structured answer if the question was structured), never a 500 stack or a fabricated answer.
- **R5.2 (cost)** Structured questions SHALL cost zero LLM tokens; narrative calls SHALL use the cheapest-adequate configured model over a bounded context.
- **R5.3 (scope floor)** This Spec SHALL NOT build the web UI (that is `BK-040` Stage B), a vector DB, cross-repo answering, or streamed responses.
- **R5.4 (reversibility)** The feature SHALL be removable by deleting the hook + its config with no schema migration.

## 4. Out of scope
The web UI (`BK-040` Stage B); a vector store; cross-repo / org-wide answering (Stage-D concern); streamed/SSE responses; a vendor contract; private-data answering; writing anything back to the repo or collections.

## 5. Human Verification Plan (full gate — human exercises the live route)
- **V1 — structured, zero-LLM:** `POST /api/ask {"question":"how many projects are active?"}` → correct count, cited to `data/status.json`; confirm no LLM call made (log/metric). *(R2.1)*
- **V2 — ownership:** "who owns LAB-003?" → Eialarasu, cited to `portfolio.json`→`users.json`. *(R2.1)*
- **V3 — narrative, grounded + cited:** "what is LAB-002 about?" → accurate summary citing the source doc. *(R2.2/R2.3)*
- **V4 — fail-closed:** a question whose fact is absent → explicit "not in the data", no invention. *(R3.2)*
- **V5 — key safety:** confirm the key is in Railway env only; grep the repo + a response payload → key never appears. *(R4.2)*
- **V6 — infra fail-closed:** with the key unset on a throwaway env, the route returns "unavailable", not a 500/fabrication. *(R5.1)*
- **V7 — boundary:** confirm the route cannot read a private/superuser collection. *(R3.1)*
