[🏠 Cetana Labs](../../README.md) / [📚 Docs](../README.md) / Guides / **RGS Guide**

# RGS Guide — the Requirement Gathering System (`/rgs`)

> **What this is:** a one-page guide to **`/rgs`**, the Requirement Gathering System (Stage C). RGS does the business-analyst work of turning a **fuzzy, unstructured ask** into a **complete, testable, conflict-checked requirement** — so you review a draft instead of writing one from scratch.

## What RGS is (and isn't)

- **It is** a guided chat conversation (a KiroCrew **chat skill**) that elicits a requirement one question at a time, flags vague bits, grounds its claims in the real code, and emits a ready-to-paste **`INTAKE-NNN`** entry.
- **It is NOT** a web page or part of the Cetana app — there is **no URL, no local stack**. Its surface *is* the chat. (Don't look for it at `localhost:5173`; a future web UI is Stage B, not this.)
- **It never writes to the repo.** RGS drafts; **you review and commit** the entry by hand. It cannot create a backlog item or change scope on its own.

## How to use it

1. In the **KiroCrew dashboard chat**, type:
   ```
   /rgs make reporting better, soon
   ```
   …or `/rgs` on its own, then paste the raw ask (typed text, a pasted WhatsApp/Slack thread, meeting notes, or a voice-note transcript).
2. **Answer one question at a time.** RGS walks a 7-point completeness checklist (below), asking the single most useful question each turn. It will **push back on vagueness** — e.g. "make reporting *faster*" → "What's the target? e.g. 'report renders in < 2s for 10k rows' — what number counts as done?"
3. **It grounds its claims in the code.** Before it states what the system does today, it greps the real intents/entities/file-types and cites what it checked — so you get an honest current-state read, not a guess.
4. **Stop when ready.** When all 7 slots are filled, RGS converges to a draft. You can also say "that's enough" early — unfilled slots become open questions and the entry is marked `AWAITING-SOURCE`.

## The 7-point checklist RGS fills

| # | Slot | "Done" means |
| :-- | :--- | :--- |
| 1 | **Actor / user** | a named role, not "users" |
| 2 | **Trigger** | the event/need that starts it |
| 3 | **Desired outcome** | the concrete end state |
| 4 | **Acceptance criteria** | ≥1 **testable** condition (a number, not "fast") |
| 5 | **Scope boundaries** | what's in AND out |
| 6 | **Priority** | P1 / P2 / P3 + why |
| 7 | **Source-of-truth data** | which data/system grounds it |

## What you get back

Two clearly separated copy-paste blocks:

1. **The ledger entry** — a register row + a detail block, byte-compatible with **[`docs/governance/REQUIREMENTS_INTAKE.md`](../governance/REQUIREMENTS_INTAKE.md)** (Cetana's intake ledger, adopted 2026-10-08). You paste it in; it needs no reformatting.
2. **A channel-relay message** — a crisp ≤3-question summary you can send to whoever asked (RGS never sends it for you).

## Where the draft goes — the AIDLC funnel

```
/rgs  →  INTAKE-NNN draft  →  (you paste into)  docs/governance/REQUIREMENTS_INTAKE.md
      →  graduates to a BACKLOG Epic  →  /plan-start → Spec → /spec-run → /review-pr → human merge
```

- **Cetana's intake ledger** is [`docs/governance/REQUIREMENTS_INTAKE.md`](../governance/REQUIREMENTS_INTAKE.md). The first real entry is `INTAKE-001`. Entry states: `NEW → AWAITING-SOURCE → CLARIFIED → SPECCED → DELIVERED`.
- A requirement that belongs to **another project** (Cetana is the control plane, not a product) is shaped by RGS and **relayed** to that project — not tracked in Cetana's ledger. (Org-wide intake tracking here is the future Stage-D hub.)

## Guardrails (what keeps it honest)

- **Drafts only** — RGS never writes a repo or commits scope; you review and commit.
- **Grounded, never fabricated** — any system-state claim cites where it was verified.
- **Owner labels** use the full name **"Agni Eialarasu"** (bare "Agni" means the org).

## Related
- The skill itself: `.kiro/skills/rgs/SKILL.md` (the engine + the chat flow).
- The intake ledger: [`docs/governance/REQUIREMENTS_INTAKE.md`](../governance/REQUIREMENTS_INTAKE.md).
- The AIDLC delivery process the funnel feeds: [Sprint Lifecycle](sprint-lifecycle.md).
- Architecture context: `RFC-LAB-000-015` (AI assistant) and the Decision Journal (D67–D69).
