# AI Assistant "Ask-the-Portfolio" (BK-015) — Design

| Property | Value |
| :--- | :--- |
| **Spec ID** | `ask-the-portfolio` |
| **Decision of record** | `RFC-LAB-000-015` §4 (ratified by spike D77) |

---

## 1. Architecture (ratified by the spike)

```
Browser / client
   │  POST /api/ask  { "question": "..." }
   ▼
PocketBase pb_hooks route  (routerAdd "POST", "/api/ask")   ← the server runtime (D77)
   │
   ├─ 1. ROUTE: structured or narrative?
   │       structured → answer from data/*.json, ZERO LLM, cite the row      (R2.1)
   │       narrative  → ↓
   │
   ├─ 2. RETRIEVE: select the doc slice by SECTION/SPRINT-ID anchor          (R2.2, D77 revision)
   │       (NOT blind whole-doc truncation — that caused the spike's false "I don't know")
   │
   ├─ 3. GROUND + CALL: $http.send to the configured LLM with a fail-closed
   │       system prompt ("answer ONLY from context, cite, never invent")    (R2.3, R3.2)
   │
   └─ 4. RETURN { answer, citations[], grounded }                            (R1.1)
```

- **Runtime:** PocketBase `pb_hooks` + `$http.send` (D77 OQ-1 closed — no Vercel fallback). Request/response only (no SSE).
- **Data source:** the committed `data/*.json` shipped in the PocketBase image / read from disk, + repo docs. Public-read boundary (R3).
- **Model:** id + endpoint from config (settings/env); key from Railway env only (R4).

## 2. The structured-first router (R2.1 — the zero-cost majority)

A small intent classifier (keyword/pattern first, no LLM) maps a question to a deterministic handler over `data/`:

| Intent | Handler (deterministic) | Cite |
| :--- | :--- | :--- |
| count-active | filter `status.json` health ∉ {Completed, Onboarding} | `status.json` |
| at-risk/blocked | filter health ∈ {At Risk, Blocked} | `status.json` |
| ownership | `portfolio.json.owner_id` → `users.json` | both rows |
| metadata (repo, archetype, env) | `portfolio.json` field read | `portfolio.json` |
| last-sprint-shipped | `CHANGELOG`/`SPRINT_TRACKER` **archive** section by sprint-id | the section |

A question that matches no structured intent → narrative path. (The spike proved the first three deterministically; this generalizes them.)

## 3. Section-anchored narrative retrieval (R2.2 — the D77 revision)

The spike's lesson: feeding the whole `CHANGELOG` + the *live* `SPRINT_TRACKER` (which shows the CURRENT sprint, not the asked-about one) produced a correct-but-useless "not in context". Fix:

- Index docs by their markdown **section anchors** (`##`/`###` headings) and known ids (sprint ids, LAB ids, BK ids).
- For a narrative question, select the **matching section(s)** (e.g. "Sprint 12" → the `### Sprint 12` archive block), not a blind head-slice.
- Corpus is tiny, so this is a cheap in-memory keyword/heading match — no vector DB (RFC-015 §4.2; confirmed premature at this size).

## 4. The grounded prompt (R2.3 / R3.2 — fail-closed)

System prompt (verbatim intent, proven in the spike):
> "You answer ONLY from the provided context about the Cetana Labs portfolio. Ground every claim in the context and cite the source doc. If the answer is not in the context, say so — never invent."

- `temperature: 0`.
- The response's `grounded` flag is `false` when the model declines (so the UI can render "not in the data" distinctly).
- Advisory/judgment answers (R3.3) are explicitly labelled and sit on top of fail-closed facts.

## 5. Config & secret handling (R4)
- `LLM_MODEL` (e.g. `gpt-4o-mini`) + `LLM_ENDPOINT` from app settings/env; `LLM_API_KEY` from Railway service env **only**.
- The key is never logged, never in a response, never committed. Absent key → R5.1 fail-closed ("assistant unavailable"); structured questions still answer (no key needed).

## 6. Testing
- **Unit (deterministic):** the structured router + each `data/` handler (the spike's 3 structured Qs become fixtures — assert exact answers + citations, zero network).
- **Boundary:** assert the route cannot reach a private/superuser collection (R3.1); assert key never appears in output (R4.2).
- **Fail-closed:** key-unset env → "unavailable" not 500 (R5.1); absent-fact question → explicit "not in data" (R3.2).
- **Live (human V-plan):** V1–V7 against the deployed route.

## 7. Deploy
Standard model: merging the PR auto-deploys the backend (hook ships in the PocketBase image → Railway via `deploy-backend.yml`). The merge IS the promotion. Post-merge, exercise V1–V7 on the live route.

## 8. Scope floor (what this design does NOT touch)
No web UI (`BK-040`), no `data/` schema change, no new collection, no auth-rule change, no vector store, no streaming, no cross-repo reach. Removable by deleting the hook + config (R5.4).
