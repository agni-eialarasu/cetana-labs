# AI Assistant "Ask-the-Portfolio" (BK-015) — Tasks

| Property | Value |
| :--- | :--- |
| **Spec ID** | `ask-the-portfolio` |
| **Branch** | `feat/ask-the-portfolio` (`/spec-run` self-creates it) |
| **Work class** | **Sprint deliverable → FULL gate**: 4 automated gates + PR + `/review-pr` scorecard + Gate 5 recording + human merge. Agent never pushes `main`. |
| **Execution** | **`/spec-run ask-the-portfolio`** (app build). Executor = **Kiro IDE** (security-sensitive: server-side key, new public endpoint) per `RFC-LAB-000-014` — advisory; sprint owner picks the runner. |
| **Merge-first** | This Spec lands on `main` as a doc PR BEFORE `/spec-run` (the merge-first rule). |
| **EARS target** | R1–R5 in `requirements.md`; DoD = V1–V7 Human Verification Plan. |

---

## T0 — Preflight (STOP on failure) → P1, P2, P3
- [ ] Confirm spike D77 is on `main` (runtime ratified). *(P1)*
- [ ] Confirm `LLM_API_KEY` is set in the Railway service env + `LLM_MODEL`/`LLM_ENDPOINT` in settings/env — **out of band, never in repo/chat**. *(P2)*
- [ ] Confirm the public-read data boundary (which collections/files the hook may read). *(P3)*

## T1 — Structured router + deterministic handlers → R2.1
- [ ] Add the `pb_hooks` route scaffold `routerAdd("POST", "/api/ask", ...)` with `{question}` parse + 400 on empty. *(R1.1/R1.3)*
- [ ] Intent classifier (keyword/pattern, no LLM) → the handler table (count-active · at-risk · ownership · metadata · last-sprint). *(R2.1)*
- [ ] Each handler reads `data/*.json`, returns `{answer, citations, grounded:true}` with the cited row(s). *(R2.1/R2.3)*
- [ ] Unit tests: the 3 spike questions as fixtures — exact answer + citation, zero network.

## T2 — Section-anchored narrative retrieval → R2.2 (the D77 revision)
- [ ] Build the doc index: section anchors (`##`/`###`) + known ids (sprint/LAB/BK).
- [ ] Narrative selector: match question → section(s), assemble bounded context (NOT whole-doc truncate). *(R2.2)*
- [ ] Test: "what shipped in Sprint 12?" selects the `### Sprint 12` archive block (the spike's failing case now passes).

## T3 — Grounded LLM call → R2.3, R3.2, R4
- [ ] `$http.send` to `LLM_ENDPOINT` with the fail-closed system prompt, `temperature:0`, config-driven model. *(R4.1)*
- [ ] Key from Railway env only; never logged/returned. *(R4.2)*
- [ ] Parse → `{answer, citations, grounded}`; `grounded:false` when the model declines. *(R3.2)*
- [ ] Advisory labelling for judgment questions. *(R3.3)*

## T4 — Fail-closed & boundary → R3.1, R5.1
- [ ] Absent key / LLM error / timeout → graceful "assistant unavailable" (structured answers still work), never 500/fabrication. *(R5.1)*
- [ ] Boundary guard: route reads only public-read data; test it cannot reach a private/superuser collection. *(R3.1)*

## T5 — Gates (full gate) + lockstep
- [ ] 4 automated gates green (`just validate-local` mirrors CI: portfolio + generator --checks + web build/typecheck as applicable).
- [ ] Unit + boundary + fail-closed tests pass.
- [ ] Lockstep: flip `BK-015`/the sprint `TSK-` row to the build state; CHANGELOG `[Unreleased]`.
- [ ] `/spec-run` opens the PR + emits the V1–V7 Human Verification Plan, then STOP-and-hold. **Never merges.**

## T6 — Verify (human) → V1–V7
- [ ] Human runs V1–V7 against the deployed route (structured zero-LLM · ownership · narrative grounded+cited · fail-closed · key-safety · infra fail-closed · boundary). Fixes ride the same PR.
- [ ] `/review-pr` scorecard posted to the PR (full gate — the auditable verdict), THEN human squash-merge, THEN Gate 5 recording (Decision Journal) + lockstep.

## Post
- Merging deploys the hook to Railway (merge = promotion). `/api/ask` is live.
- **Unblocks `BK-040` Stage B** — the web UI now has a real endpoint to consume.
- Rotate any throwaway spike key if not already done.
