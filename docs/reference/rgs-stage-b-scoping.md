<a id="top"></a>
[🏠 Cetana Labs](../../README.md) / [📚 Docs](../README.md) / Reference / **RGS Stage B — Scoping**

# RGS Stage B — Web UI Scoping (Option 1: on the BK-015 AI runtime)

> **Status:** 🎯 **Scoping (pre-Spec)** — not yet a build Spec. `BK-040`. This doc frames Stage B so it can graduate to a Spec via `/plan-start` **once its hard gate clears** (see §1). It is a planning artifact (governance tooling, docs fast-path), not a committed design.
>
> **One-line scope:** give RGS a real browser surface — a SvelteKit route that runs the **same surface-agnostic elicitation engine** (RGS skill §A/§B) through a server-side **PocketBase AI hook** (the `RFC-LAB-000-015` / `BK-015` runtime), so a non-chat user can shape a requirement in the app and get a ledger-ready `INTAKE-NNN` draft.

---

## 0. Where this sits

RGS is staged with a deliberate **engine/surface separation**:

| Stage | What | Status |
| :--- | :--- | :---: |
| **C** | `/rgs` chat skill — the elicitation **engine** + output schema | ✅ Shipped (`BK-026`, PR #67) |
| **B** | **Web UI** — a browser surface over the same engine | 🎯 **This doc** (`BK-040`) |
| **D** | Org-wide intake hub (every project's asks) | ⏸️ Deferred (D69) |

The RGS skill already isolated the reusable core: **§A** (the 7-slot completeness checklist + elicitation strategy) and **§B** (the `INTAKE-NNN` output contract), both documented as *surface-agnostic* precisely so **Stage B reuses them unchanged** (R-ENG-1). Stage B adds a **surface**, not a new engine.

---

## 1. ⛔ The hard gate — Stage B is BLOCKED on BK-015

**This is the load-bearing fact and must not be glossed.** Option 1 runs the elicitation engine **server-side in a PocketBase `pb_hooks` AI route** — which is exactly the runtime `RFC-LAB-000-015` (`BK-015`) proposes but **has not yet proven**:

- `RFC-LAB-000-015` is **🟡 Proposed**, not Accepted-for-build. Its **feasibility spike (`TSK-061`) has not run** — the three probes (runtime / grounding / cost) are still pending, and the spike needs a test LLM key on the probe surface.
- RFC-015 **OQ-1** is open: *does the Goja JS `pb_hooks` runtime comfortably make an outbound HTTPS LLM call, or is a tiny Go handler / Vercel function needed?* **Stage B's entire server tier depends on this answer.**
- The frontend is a **pure static SPA** (`adapter-static` on Vercel) — **there is no SvelteKit server runtime in production**, so the UI *cannot* call an LLM itself without leaking the key (RFC-015 §2). It **must** go through the PocketBase hook. No BK-015 runtime ⟹ no Stage B.

**Consequence:** Stage B cannot be built — or even fully specced with confidence — until the `BK-015` spike confirms (or revises) the `pb_hooks` AI runtime. This doc therefore scopes the UI **conditionally on `POST /api/ask`-style endpoint existing**, and names the spike as the explicit predecessor.

> **Recommendation:** run the `BK-015` feasibility spike (`TSK-061`) **first**. If it ratifies the `pb_hooks` runtime → Stage B's server dependency is real and this scope graduates to a Spec. If it revises the runtime (Vercel function instead) → §4 below changes accordingly. Scoping now is useful (it defines the UI contract and surfaces the gate); **building now is not possible.**

---

## 2. User & value

- **Actor:** a Project Owner / BA / stakeholder who is **not in the KiroCrew chat** — they live in the web app, not the agent surface.
- **Trigger:** they have a fuzzy ask ("make reporting better") and want to shape it into a real requirement without needing the chat skill or the Operator.
- **Outcome:** a guided, one-question-at-a-time web conversation that produces the **same ledger-ready `INTAKE-NNN` draft** (register row + detail block) + channel-relay message the chat skill emits — reviewed by a human before it lands in the ledger.
- **Why a UI (vs just chat):** reach — the chat skill requires a KiroCrew seat and the agent surface; the web UI meets stakeholders where the portfolio already lives.

## 3. Scope (proposed)

**In:**
- A SvelteKit **route** (e.g. `/intake` or `/rgs`) in `app/web` — a guided elicitation form/chat that walks the §A 7-slot checklist one question at a time.
- Each turn calls the **PocketBase AI endpoint** (the BK-015 hook) which runs the elicitation logic server-side and returns the next question / gap flag / convergence.
- On convergence, render the §B `INTAKE-NNN` draft (register row + detail block) + the channel-relay block as **copy-paste output** — byte-compatible with `docs/governance/REQUIREMENTS_INTAKE.md`.
- **Read-only to the repo:** the UI emits a draft for a human to review and commit — it **never writes the ledger or commits scope** (the Stage-C guardrail R-GOV-1 carries over verbatim).
- Grounding: the hook greps/queries the real `data/` + docs server-side and cites what it checked (RFC-015 §4.5 fail-closed data boundary; public-read only).

**Out (floor):**
- The elicitation **engine logic** itself is not re-authored — it is the §A/§B contract, implemented once server-side (shared with the eventual Stage-D hub).
- No new auth tier, no private-data access (public-read boundary, RFC-015 §4.5).
- No org-wide multi-repo intake (that is Stage D).
- No autonomous ledger writes, no live connectors (Jira/Monday/Excel).
- No vector DB (structured-first + light retrieval per RFC-015 §4.2).

## 4. Architecture sketch (conditional on BK-015)

```
Browser (SvelteKit route, static SPA)
   │  POST /api/ask  { session, slots_so_far, latest_answer }
   ▼
PocketBase pb_hooks AI route  (the BK-015 runtime — RFC-015 §4.1)
   │  - runs §A elicitation (pick next slot, flag gaps)
   │  - grounds claims over data/*.json + docs (public-read, cited)
   │  - calls the config-driven LLM (model id from settings, BK-012)
   │  - on convergence: emits the §B INTAKE-NNN draft
   ▼
returns { next_question | draft } → UI renders → human reviews → commits by hand
```

- **Server runtime:** PocketBase `pb_hooks` (pending OQ-1 — may become a Go handler / Vercel function if the spike says so).
- **Model:** provider-agnostic, keyed from app-level settings (`BK-012` / RFC-015 §4.3).
- **Deploy:** merging the Stage-B PR auto-deploys to the single reference env (the standard release model — merge *is* the promotion; frontend→Vercel, backend/hook→Railway).

## 5. Open questions for the Spec (after the spike)
- SB-OQ-1: Does elicitation state live **client-side** (the UI holds slots, posts the whole state each turn — stateless hook) or **server-side** (a session row in PocketBase)? *Lean: client-holds-state, stateless hook — simplest, matches the public boundary.*
- SB-OQ-2: Route name + nav — does Stage B finally fill the **empty header center-nav slot** BK-027 reserved? *(Likely yes — this is the first real web-app route the slot was built for.)*
- SB-OQ-3: Chat `/rgs` and the web UI share the §A/§B contract — do they share **implementation** (one server engine both call) or just the **spec**? *Lean: shared server engine, so Stage D inherits it.*
- SB-OQ-4: Anonymous use or sign-in required to shape an intake? *(Public-read data suggests anonymous-capable; a sign-in gate is a product call.)*

## 6. Graduation path
```
BK-015 spike (TSK-061) ratifies pb_hooks AI runtime
   → BK-015 build Spec (the /api/ask endpoint) ships
   → THEN: /plan-start on BK-040 → Stage B Spec (requirements EARS + design + tasks)
   → /spec-run (Antigravity — pure frontend + a hook consumer) → /review-pr → human merge = live on staging
```

Stage B is a **sprint deliverable** (user-facing functionality) → **full gate** when it builds. This scoping doc is governance tooling → docs fast-path.

---

> 🧭 **Navigation:** [⬆️ Top](#top) · [🏠 Repo](../../README.md) · [📚 Docs Hub](../README.md)
> 🔗 **Related:** [RGS Guide](../guides/rgs-guide.md) · [`RFC-LAB-000-015`](../rfc/RFC-LAB-000-015-ai-assistant.md) · [`REQUIREMENTS_INTAKE.md`](../governance/REQUIREMENTS_INTAKE.md) · `.kiro/skills/rgs/SKILL.md`
