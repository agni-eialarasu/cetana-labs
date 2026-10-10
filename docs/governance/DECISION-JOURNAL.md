[🏠 Cetana Labs](../../README.md) / [📚 Docs](../README.md) / Governance / **Decision Journal**

# Decision Journal — Cetana Labs

> **Purpose.** This journal records *how* key engineering decisions were reached — the
> problem, the options weighed, the trade-offs, and the rationale — not just what shipped.
> The CHANGELOG records *what*; the RFCs record the *formal decision*; this journal records
> the ***thinking***. Entries are curated (signal, not transcript) and written to be read by
> engineering leadership.
>
> **Method.** Work follows a human-directed, AI-assisted model: the human (Eialarasu) sets
> direction, weighs options, and gates every merge; the AI agent executes, validates, and
> surfaces trade-offs. Decisions below reflect that division — the human made the calls.

---

## Entry 001 — Foundational Session: from static control plane to governed, AI-driven web app

**Date:** 2026-09-24 · **Contributor(s):** Agni Eialarasu (`arasu@agnitechnologies.com`), AI-assisted · **Mode:** Kiro Web (brainstorm & planning) · **Outcome:** RFC-LAB-000-001 → -008, 11 PRs, releases v0.5.0 → v0.9.0

> _Decisions D1–D11 in this entry were made by Agni Eialarasu (human-directed), AI-assisted in execution/validation._

This inaugural entry captures a single extended working session that took Cetana Labs
(`LAB-000`) from a static, file-based control plane to a governed web-app foundation with a
scoped MVP and an AI-driven delivery process. Each sub-section is a discrete decision.

---

### D1 — Move the control plane to cloud-based development
- **Trigger:** Running IntelliJ + Antigravity for two projects on one machine caused performance pressure. `LAB-000` has no local runtime dependency (docs + zero-dep Python; automation runs in CI).
- **Options:** (A) keep local; (B) cloud-based dev; (C) hybrid.
- **Decision & rationale:** Cloud-based (Kiro Web primary, Codespaces fallback for future services). The repo was *only* using the local machine as an editor — offloading it freed the machine for the genuinely stateful fullstack project. A reusable **Cloud-vs-Local classification heuristic** was defined so the choice is principled for future projects, not ad-hoc.
- **Outcome:** `RFC-LAB-000-001`; `Dev Environment` field added to the protocol; devcontainer.

### D2 — Make the portfolio metadata relational (users ⇄ projects)
- **Trigger:** Master metadata lived as a hand-maintained Markdown table, duplicated across files and parsed by fragile regex (a `.ai` TLD truncation bug had already appeared).
- **Options:** (A) JSON index alongside Markdown; (B) full JSON source of truth; (C) JSON as a read-only export.
- **Decision & rationale:** Option A — `data/` JSON masters as the source of truth for *structural* data, `STATUS.md` remains canonical for *live status*, README table becomes **generated**. Chosen because it kills duplication without destabilizing the daily status-scraper contract. The human then added a decisive requirement: **a user master with a many-to-many memberships join** — insisting M2M be modeled from day one ("many-to-many will definitely" happen), which later became the exact foundation for RBAC.
- **Outcome:** `RFC-LAB-000-002`; `data/users|portfolio|memberships.json` + schemas; generated registry; referential-integrity validator pillar.

### D3 — Surface the project owner on dashboard cards; make the internal ID internal
- **Trigger:** Cards led with the Project ID (internal, low executive value).
- **Decision & rationale:** Replace the top-left ID badge with an **owner pill**; keep the ID for search/sort/tooltip only. The human's reasoning: the ID is plumbing; *accountability* (who owns it) is what an executive viewer needs.
- **Outcome:** Owner-first cards; ID retained internally.

### D4 — Scope the web-app evolution on PocketBase
- **Trigger:** The static control plane needed to become a real app (db + server); RBAC (`BK-007`) on the horizon.
- **Options:** PocketBase vs Supabase/Firebase vs bespoke FastAPI+Postgres.
- **Decision & rationale:** **PocketBase** — single Go binary + embedded SQLite + built-in auth + per-collection API rules. Won on ops-simplicity-per-feature at this scale, and its collections map 1:1 onto the `data/` masters (the D2 M2M model pays off). Alternatives were over-provisioned for a control hub.
- **Outcome:** `RFC-LAB-000-003`; phased P0–P5 plan.

### D5 — Adopt branch-based development (the "sleek → high" inflection)
- **Trigger:** Introducing runnable code, a database, and migrations makes trunk-based direct commits risky. The human explicitly signalled moving "from sleek to high" — time for industry-standard practice.
- **Options:** (A) strict PR-for-everything; (B) hybrid path-scoping; (C) full GitFlow.
- **Decision & rationale:** **GitHub Flow, hybrid path-scoped** — app code / `data/` / migrations require PR + green CI + squash-merge; governance/docs may fast-path. Full GitFlow rejected as over-ceremony for team size. The model was **dogfooded** — landed as the repo's first-ever PR (#1).
- **Outcome:** `RFC-LAB-000-004`; PR CI workflow; PR template. (Branch protection deferred — repo transfers to an org account first.)

### D6 — Phase 1 & 2 build; and the "don't reinvent" reflex on the UI
- **Decision & rationale:** Backend scaffolding (P1) and the SvelteKit "Sleek UI" (P2) were built via PRs. Framework/tooling choices were the human's, with course-corrections that mattered: **Svelte 5 over 4** (greenfield, current, long-lived), **pnpm** as package manager, and — when the org handed over a **Nexus Pulse Design System** — adopting it wholesale rather than a generic component kit. The agent flagged the Next.js↔SvelteKit mismatch; the human accepted a token/framework split (adopt the design tokens verbatim, translate the framework specifics).
- **Outcome:** `RFC-LAB-000-005`, `docs/DESIGN.md`, Sleek UI live at `/app` (dual-run with the classic dashboard).

### D7 — Scope auth & RBAC (activating the M2M model)
- **Decision & rationale:** GitHub OAuth identity; **per-project roles via the `memberships` join** decided in D2; access enforced by explicit, auditable PocketBase API rules; access-only audit with non-surveillance safeguards. The human's earlier "M2M will definitely happen" is why this scoped cleanly.
- **Outcome:** `RFC-LAB-000-006`.

### D8 — Standardize the two-surface work environment (Kiro Web + IDE)
- **Trigger:** Poor DX juggling Web and IDE; skills had grown organically in a non-Kiro-native location.
- **Decisions & rationale:**
  - **Surface roles:** Web = stateless governance/docs; IDE = stateful servers. Intentional split, not a wall.
  - **Skills migrated** `.agents/skills/` → **`.kiro/skills/`** (Kiro-native; auto-shared Web+IDE). Personal skills (`/sign-in`, `/session-save`, …) go to `~/.kiro/` + Config Sync — a deliberate project-vs-personal split.
  - **Podman-first** containers per the org standard; but honestly scoped — PocketBase is a bare binary locally, so containers are for staging/parity only, not forced into local dev.
  - **`/env-doctor` vs `/validate-*` boundary** — the human questioned potential duplication; resolved with a hard rule: env-doctor diagnoses *readiness* (never runs validators), validate-* checks *work*.
- **Outcome:** `RFC-LAB-000-004` (updated), `RFC-LAB-000-007`; Makefile cheat-sheet; work-environment guide.

### D9 — Verify locally before defining MVP ("from a working stack, then requirements")
- **Trigger:** The human insisted on running the stack locally *before* scoping the MVP — "from there only I will come up with requirements."
- **What it surfaced (the value of insisting on real verification):**
  - The repo config didn't match the actual MBP (nvm intentionally absent → `.nvmrc` was wrong; pnpm pin mismatch). Reconciled to Homebrew-native reality.
  - **PocketBase 0.22 scaffold vs 0.40 machine** — a breaking-version gap caught *before* it wasted time. Schema regenerated to the v0.23+ format.
  - Hand-written schema import **failed on v0.40** ("Invalid collections configuration"). Decision: **switch to programmatic provisioning via the API** (Option B) — version-robust, idempotent. This was the right call over fighting the import format.
  - Idempotency bugs on re-run (unique-index on the default `users` collection; email-collision on re-seed) — fixed to make setup safely re-runnable.
  - A "ran stale code" trap (forgot `git pull`) → added a `make setup` staleness-guard.
- **Rationale:** Every one of these would have been a confusing failure mid-MVP. Insisting on a *proven* local stack first was vindicated. The agent was wrong twice (nvm advice; assuming the import would work) and the human's real-environment testing caught it — the human gate working as intended.
- **Outcome:** working local stack (provision + seed live on PocketBase v0.40); `make setup` one-command bootstrap; several `fix()` PRs.

### D10 — Define the MVP with *minimum* RBAC
- **Decision & rationale:** MVP = logged-in user sees live PocketBase portfolio; **owner edits their own project's status**; deployed. **Minimum RBAC = 3 tiers** (public / authenticated / owner-via-`owner_id`), *deliberately deferring* the full 5-role `memberships` model, audit, and status migration. The discipline here: ship the thinnest thing that exercises the real auth+write path, defer the relational-role complexity until there's concrete need — while the M2M layer stays in the schema, ready.
- **Outcome:** `RFC-LAB-000-008`; MVP epic `BK-011`; phases M1–M5.

### D11 — Adopt Kiro-native Specs + Autonomous mode as the AIDLC engine (don't reinvent)
- **Trigger:** Designing a sprint/AIDLC process, the human first proposed a custom `PROMPT.md` contract (ask + Definition of Done), sensing its long-run value for onboarding developers/agents.
- **The pivotal realization:** A **Kiro Spec** (`requirements.md` with EARS acceptance criteria + `design.md` + `tasks.md`, agent-executed → PR) *is* that contract — natively. And **Autonomous mode** (plan → execute via sub-agents → PR, human-gated at review) *is* the AIDLC executor.
- **Decision & rationale:** **Adopt Kiro Specs as the delegated/agent contract instead of a homegrown PROMPT.md**; keep a lightweight per-sprint REPORT.md (the one genuine gap) for human sign-off. **Progressive formality**: solo-pair work stays light; delegated-agent/onboarded-dev work gets a full Spec. Frame the sprint RFC (RFC-009, planned) around Kiro-native spec-driven + autonomous features, human-gated via PR review. Rationale: don't rebuild what the tool provides; EARS is a more testable DoD than freeform prose; Specs live in `.kiro/` (same portability as skills). Honest caveat noted: docs don't confirm "Autonomous over an existing Spec's tasks" — the AIDLC spike will determine the best chaining.
- **Human trajectory context:** solo → MVP, then developers onboard; wants to experiment with multi-agent (AIDLC) work, human-gated throughout. Kiro Web for brainstorm/plan, Kiro IDE for execute/verify.
- **Outcome (planned):** `RFC-LAB-000-009` (sprint lifecycle on Kiro-native spec-driven + autonomous); first experiment = run MVP task **M1** as a Spec.

---

### Session meta — the working method demonstrated
- **Division of labor:** human set every direction and gated every merge; agent executed, validated, and surfaced trade-offs.
- **Governance throughput:** 9 RFCs, 11 PRs (all CI-gated, squash-merged), releases v0.5.0 → v0.9.0 — high volume *with* discipline.
- **Course-corrections by the human that changed outcomes:** Svelte 5 (not 4); defer TSK-025/026; check the work-machine guide (caught the nvm/version mismatches); minimum-RBAC scoping; Specs over custom PROMPT.md.
- **Honest failures & recovery:** agent gave wrong nvm advice and wrongly assumed the schema import would work on v0.40; local verification (human-insisted) caught both; fixes shipped. This is the human gate functioning as designed — and is recorded here deliberately, because credible decision-making includes the misses.


---

## Entry 002 — Standardizing the dev process: sprint lifecycle, AIDLC, and decision capture

**Date:** 2026-09-24 · **Contributor(s):** Agni Eialarasu (`arasu@agnitechnologies.com`), AI-assisted · **Mode:** Kiro Web (brainstorm & planning) · **Outcome:** `/brainstorm-save` skill, `DECISION-JOURNAL.md`, AI-collaboration model; RFC-LAB-000-009 planned

Follows Entry 001. This session shifted from *building* to *standardizing how building happens* — reviewing an external team's sprint protocol, aligning on Kiro-native tooling, and establishing a record of engineering reasoning.

### D12 — Adopt a sprint lifecycle protocol, adapted from Nexus Pulse (LAB-003) — not copied
- **Trigger:** The human shared the Nexus Pulse Engineering Sprint Lifecycle (5-verb pipeline, PROMPT/REPORT envelopes, Track A/B, roster, role-based broadcasts) and asked to "adapt best and needed."
- **Options:** (A) adopt wholesale; (B) adopt the delivery *discipline*, defer the multi-dev *org structure*; (C) minimal.
- **Decision & rationale:** Option B. Nexus Pulse's protocol targets a multi-contributor team (human devs + AI agents, roster, tracks); `LAB-000` is solo+AI today. Adopt the **5-phase pipeline, `/review-pr` gate, STOP-and-hold, consolidated Golden Rules, lightweight REPORT**; **defer** roster/Track-A-B until real contributors join. Avoids premature team ceremony while capturing the discipline. _(Contributor: Agni Eialarasu)_
- **Outcome:** RFC-LAB-000-009 (planned).

### D13 — Progressive-formality contracts (right-sized by executor)
- **Trigger:** The human noted per-sprint PROMPT.md feels heavy now, but is valuable long-run as a clear ask + Definition of Done for another developer/agent picking up cold. Proposed a hybrid.
- **Decision & rationale:** Contract **depth scales with executor autonomy** — solo-pairing stays light; delegated agent / onboarded dev gets a full contract. Reframed PROMPT.md not as ceremony but as *the interface* for an agent that has no conversational context. Same structure, dialed up/down. _(Contributor: Agni Eialarasu)_
- **Outcome:** folded into the AIDLC model (superseded by D15's Kiro-Specs decision).

### D14 — Trajectory & AIDLC intent (solo → team; multi-agent, human-gated)
- **Trigger:** The human clarified: solo to MVP, then developers onboard; wants to experiment with multi-agent work (AIDLC), human-gated throughout; Kiro Web for brainstorm/plan, Kiro IDE for execute/verify.
- **Decision & rationale:** Design the process to **scale up without a rewrite** — define **executor roles** (Lead-paired / Delegated-agent / Onboarded-dev) rather than named people; human gate is the non-negotiable safety rail for AIDLC. _(Contributor: Agni Eialarasu)_
- **Outcome:** informs RFC-LAB-000-009 framing.

### D15 — Use Kiro-native Specs + Autonomous mode as the AIDLC engine (don't reinvent)
- **Trigger:** The human asked how Kiro's spec-driven development and Autonomous mode fit — before committing to a custom PROMPT.md.
- **Key realization (verified against Kiro docs):** a **Kiro Spec** (`requirements.md` EARS acceptance criteria + `design.md` + `tasks.md`, agent-executed → PR) *is* the contract; **Autonomous mode** (plan → sub-agent execute → PR, human-gated at review) *is* the AIDLC executor.
- **Decision & rationale:** **Adopt Kiro Specs as the delegated/agent contract instead of a homegrown PROMPT.md**; keep a lightweight REPORT.md for sign-off (the genuine gap). Don't rebuild what the tool provides; EARS is a more testable DoD than prose; Specs live in `.kiro/` (same portability as skills). Honest caveat: "Autonomous over an existing Spec's tasks" is undocumented — the AIDLC spike will determine best chaining. _(Contributor: Agni Eialarasu)_
- **Outcome:** RFC-LAB-000-009 framed on Kiro-native features; first experiment = run MVP task M1 as a Spec.

### D16 — Establish a Decision Journal (this document) as a project showcase artifact
- **Trigger:** The human wanted the brainstorming reasoning captured "in structured format" to showcase thinking pattern/experience to a Manager/Architect/CTO (and any co-reviewer).
- **Options for placement:** (A) repo `docs/`; (B) personal `~/` folder; (C) hybrid.
- **Decision & rationale:** **Repo (`docs/DECISION-JOURNAL.md`)** — reframed as a *project governance artifact* (not personal), because its value is contextual: it references repo RFCs/PRs and is read in-repo alongside them. Format = decision narrative (problem → options → rationale → outcome), curated for credibility (includes honest failures). Contributor attribution added per section for multi-author readiness. _(Contributor: Agni Eialarasu)_
- **Outcome:** `docs/DECISION-JOURNAL.md` (PR #12); this entry.

### D17 — `/brainstorm-save` is a project skill; `/sign-off` prompts (not auto-runs) it
- **Trigger:** The human spotted an inconsistency — a *personal* skill writing to a *repo* doc — and asked whether `/session-save` or `/sign-off` should internally trigger capture.
- **Decision & rationale:** Since the journal is a **project** artifact (D16), **`/brainstorm-save` is a project skill** (`.kiro/skills/`), reusable by future contributors — resolving the inconsistency. Chaining: `/sign-off` should **prompt** to run it *when the session had decisions*, **never auto-run** — auto-capturing every session would pollute the journal with noise and destroy its credibility. Curation stays human-controlled. _(Contributor: Agni Eialarasu)_
- **Outcome:** `.kiro/skills/brainstorm-save/SKILL.md`; `/sign-off` (personal) to prompt, documented in the skill.

### Session meta
- **Theme:** meta-work — designing *how* the team (human + agents) will build, and how reasoning is recorded.
- **Notable judgment:** repeatedly chose "adapt/adopt-native, don't reinvent" (Nexus Pulse discipline over its org apparatus; Kiro Specs over custom PROMPT.md; project skill over inconsistent personal placement).
- **Method:** human set intent and made every call; AI verified Kiro capabilities against docs, surfaced the placement inconsistency's resolution options, and executed.


---

## Entry 003 — Sprint lifecycle as a phase-aware state machine (great-DX AIDLC one-liners)

**Date:** 2026-09-26 · **Contributor(s):** Agni Eialarasu (`arasu@agnitechnologies.com`), AI-assisted · **Mode:** Kiro Web (brainstorm & planning) · **Outcome:** `RFC-LAB-000-009` (+§3.1 state machine), `/spec-run` `/plan-start` `/plan-done` skills + state guards on `/review-pr` `/sprint-done`, first AIDLC Spec (M1); PRs #14–#17

> _Decisions D18–D22 were made by Agni Eialarasu (human-directed), AI-assisted in execution/validation._

Follows Entries 001–002. Where 002 *chose* Kiro Specs + Autonomous mode as the AIDLC engine, this session **operationalized** it: turning the sprint lifecycle into a small, phase-aware state machine of `/commands` optimized for a great AIDLC developer experience — and stress-testing the design against an external reference (the Nexus Pulse Sprint Lifecycle) without copying it.

---

### D18 — Frame the lifecycle as ordered `/commands`: `brainstorm → implement → verify → done`
- **Trigger:** Having authored RFC-009 (the lifecycle) and the M1 Spec, the human asked how to actually *kickstart* the next items in the IDE — and, seeing the runbook, pushed back that it still had too many manual steps. The goal was crystallized as: **a one-liner with args, where I only worry about the functional change and its verification; everything else is repeatable and should be owned by the commands.**
- **Options:** (A) keep a documented multi-step runbook; (B) a single monolithic command (à la Nexus Pulse `/sprint-start <id>` doing register+build+PR); (C) a small set of ordered, phase-aware commands, each owning its repeatable boilerplate.
- **Decision & rationale:** **Option C** — a four-verb flow `brainstorm → implement → verify → done`. Monolithic (B) was rejected because it would collapse the deliberate Web(plan)/IDE(execute) surface split (`RFC-LAB-000-007`) and the phase gates into one verb. The human's DX bar — *attention spent only on function + verification* — became the design's north star. _(Contributor: Agni Eialarasu)_
- **Outcome:** `RFC-LAB-000-009` §3.1 (state machine + verb map); the command set below.

### D19 — `/spec-run <spec-id>` owns everything repeatable; the "extra checkout" is a workflow smell, fixed by merge-first
- **Trigger:** The first `/spec-run` draft still told the user to `git checkout` the spec branch before running — the human caught this as a leaky abstraction ("the extra step is still there").
- **The realization (agent-surfaced, human-decided):** the checkout only existed because the Spec sat on an *unmerged* branch. If the Spec is **merged to `main` during planning** (the human's own LAB-003 pattern: "drafted the spec as doc changes and merged"), then `/spec-run <id>` can sync `main`, find the Spec, and self-create the branch — needing **only the id**.
- **Decision & rationale:** Adopt the **merge-first rule** and make `/spec-run` **own all repeatable steps** (git sync, branch, preflight, PR), with **silent-unless-broken preflight** so green checks don't cost attention. The Spec is the single source of truth — **no inline arg overrides** (avoids two drifting contracts). Chosen over cleverer arg-passing because the friction was a *workflow* problem, not a command-surface one. _(Contributor: Agni Eialarasu)_
- **Outcome:** `/spec-run` rewritten (PR #17); self-describing **Execution header** on the M1 Spec (PR #15); merge-first codified in RFC-009 §3.1/§9.

### D20 — Verb granularity: a sprint *contains many* plans (`/sprint-start` ⊃ `/plan-start`)
- **Trigger:** The human proposed `/plan-start` / `/plan-done` for brainstorming/backlog/doc work, with `/plan-start` **optional and implicit** (any free-form topic *is* a plan-start). The agent flagged an overlap: this collides conceptually with the existing `/sprint-start` (also a Scope/Web opener).
- **Options:** (a) **nest** — `/sprint-start` = the sprint container (once), `/plan-start` = a per-feature planning session within it (many → one Spec each); (b) generalize `/plan-start` and make `/sprint-start` an alias; (c) no distinct `/plan-start`.
- **Decision & rationale:** **Option (a) — nesting.** Because the AIDLC *unit of work is the Spec*, and a sprint naturally holds several, sprint-⊃-plans-⊃-Spec is the honest hierarchy. `/plan-start` stays **optional/implicit** for zero-ceremony brainstorming; `/plan-done` performs the merge-first Spec merge. _(Contributor: Agni Eialarasu)_
- **Outcome:** `/plan-start` + `/plan-done` skills (PR #17); documented in RFC-009 §3.1 verb map and `AGENTS.md` §4.

### D21 — State guards: "skip if redundant, HOLD if a gate/prereq is missing" — never a silent bypass
- **Trigger:** The human wanted issuing a command **at the wrong state** to "alert, skip, and proceed." The agent pushed back that "skip and proceed" is only safe for *redundant* work — for a *missing prerequisite or gate* it must **stop**, not fabricate the missing step.
- **Decision & rationale:** Split the semantics: **redundant/already-done ⇒ skip + continue**; **missing prerequisite or gate ⇒ alert + HOLD** (name the exact next action). This preserves the intent (wrong-order tolerance) while guaranteeing a wrong-order command can **never quietly skip a gate** — the human review, the merge-first requirement, or recording only-merged work. The guard is a **tripwire, not a shortcut.** The human accepted the refinement. _(Contributor: Agni Eialarasu; refinement surfaced by AI, human-approved)_
- **Outcome:** state guards added to `/plan-start`, `/plan-done`, `/spec-run`, `/review-pr`, `/sprint-done` (PRs #16, #17); semantics in RFC-009 §3.1.

### D22 — Adapt Nexus Pulse's one-liner DX; keep LAB-000's decisions (don't copy)
- **Trigger:** The human shared the Nexus Pulse Engineering Sprint Lifecycle (5-verb pipeline, `/sprint-start <id>` one-liner, Track A/B roster, `gh pr create`, "42/42 AST checks") as the DX reference.
- **Decision & rationale:** **Adopt the one-liner-kickoff DX and the ordered-pipeline discipline; translate everything else to LAB-000's prior decisions** — Kiro **Specs** (not `PROMPT.md`), **`gh api`** (the `gh pr create`/GraphQL path fails in this environment), **5-pillar `make validate-local`** (not "42/42 AST checks"), and **no Track-A/B roster** (deferred until real contributors — consistent with D12). Same reason as before: adopt the *discipline*, not the *org apparatus*. _(Contributor: Agni Eialarasu)_
- **Outcome:** the lifecycle command set is Nexus-Pulse-inspired but LAB-000-native; noted in RFC-009 §8 (deferred scope) and the `/spec-run` PR.

---

### Session meta
- **Theme:** operationalizing the AIDLC lifecycle into a great-DX, phase-aware command set — the "how you drive it" layer atop 002's "what the engine is."
- **Notable judgment:** the human repeatedly optimized for a single thing — *spend attention only on function + verification* — and used it to reject leaky abstractions (the manual checkout) and over-collapsed designs (a monolithic verb).
- **Course-corrections that changed outcomes (human):** killed the extra-checkout step (→ merge-first, D19); chose nesting over a colliding `/plan-start` (D20); tightened "skip and proceed" so gates can't be silently skipped (D21).
- **Honest note:** the commands are *skill specifications* (procedures the IDE agent follows), not yet executable code — so their first real exercise is the M1 run, which also remains the spike for the still-undocumented Autonomous-over-existing-Spec chaining (RFC-009 §7). Recorded so the credibility bar (design-vs-proven) stays explicit.


---

## Entry 004 — Human functional verification: closing the loop between agent self-validation and merge

**Date:** 2026-09-27 · **Contributor(s):** Agni Eialarasu (`arasu@agnitechnologies.com`), AI-assisted · **Mode:** Kiro Web (brainstorm & planning) · **Outcome:** `RFC-LAB-000-009` §3.2/§3.3 amendment, `/verification-done` skill, Human Verification Plan + Verification Log, `/review-pr` evidence gate; TSK-048

> _Decisions D23–D25 were made by Agni Eialarasu (human-directed), AI-assisted in execution/validation._

Follows Entry 003, and was **triggered by the very first `/spec-run`** (M1). The AIDLC run worked — but in reviewing PR #21, the human noticed the lifecycle had no *formal* step for the part he'd just done by hand: actually exercising the feature. This entry captures closing that gap.

---

### D23 — Add an explicit human functional-verification phase (IN_VERIFICATION), distinct from the gate
- **Trigger:** After the M1 `/spec-run`, the protocol observed was: IDE completes → human asks for review → **human manually verifies** → authorizes merge. The lifecycle only had agent self-validation (EARS) then the governance gate (`/review-pr`) — the *human exercising the feature* was undocumented and unrecorded.
- **Options:** (A) leave it implicit inside `/review-pr`; (B) a distinct verification phase/state between implement and the gate, with its own loop.
- **Decision & rationale:** **Option B.** Insert an **`IN_VERIFICATION`** state: `/spec-run` opens the PR + **emits a Human Verification Plan** and STOPs there (not at merge); the human runs it, fixes ride the **same PR**, and the loop repeats until it passes. Under AIDLC this is *where trust is earned* — an agent wrote the code, so an explicit hands-on human check matters more, not less. Mirrors Nexus Pulse's "Phase 3 — Human Local Verification." _(Contributor: Agni Eialarasu)_
- **Outcome:** `RFC-LAB-000-009` §3.2; state machine + both sequence diagrams updated.

### D24 — Capture the verification loop (don't let it evaporate): `/verification-done` → Verification Log in `REPORT.md`
- **Trigger:** The human noted (from Nexus Pulse practice) that "IDE agent handles fixes conversationally" isn't enough — the findings/corrections must be **captured** so the next agent in the pipeline (Web `/review-pr`, then `/sprint-done`) inherits the evidence rather than losing it to IDE chat.
- **Options for naming:** `/verification-save` (checkpoint-ish) vs `/verification-done` (terminal transition). For location: PR comment vs a repo artifact.
- **Decision & rationale:** **`/verification-done`** — it fits the `-done` family (`plan-done`, `sprint-done`) and does double duty: **append a Verification Log** to `.kiro/specs/<id>/REPORT.md` (source of truth, rides the same PR) **and** transition `IN_VERIFICATION → IN_REVIEW`. `/review-pr` gains a step that **consumes** the log as evidence (missing/failed ⇒ HOLD) — turning the gate from "CI + DoD-on-paper" into "CI + DoD + the human actually verified it." The **Human Verification Plan** is authored in the Spec (experiential, human-executable) and kept **distinct from EARS** (machine self-validation), not auto-derived. _(Contributor: Agni Eialarasu)_
- **Outcome:** `/verification-done` skill; `REPORT.template.md` Verification Log; M1 REPORT retro-captures the manual verification as the worked example.

### D25 — Codify the command naming convention: `[phase-or-action]-[start|done]`
- **Trigger:** Naming `/verification-done`, the human stated the general rule: future commands should follow one style.
- **Decision & rationale:** Adopt **`[phase-or-action]-[start|done]`** — `start` opens/enters a phase, `done` closes/transitions it — so the command surface is self-documenting and future verbs (`deploy-start`/`deploy-done`, …) slot in without re-litigating names. Honest asymmetry noted: the verify loop has **no `/verification-start`** — it's opened when `/spec-run` emits the plan; only the `-done` closer is a command. _(Contributor: Agni Eialarasu)_
- **Outcome:** `RFC-LAB-000-009` §3.3; applied across the verb map and guide.

---

### Session meta
- **Theme:** the first real execution *taught the process* — running M1 exposed a missing phase, and the fix was folded back immediately (the lifecycle improving itself from evidence, exactly as the AIDLC spike intended).
- **Notable judgment:** the human insisted verification be **captured, not just performed** (auditability for the next agent) and that a wrong-state `/verification-done` must **never record a pass that didn't happen** (guard: unrun/failing steps ⇒ HOLD) — consistent with the D21 tripwire-not-shortcut principle.
- **Honest note:** M1's Verification Log is a **retro-capture** — the manual verification happened before this loop was formalized. From the next Spec onward it's the live path. The skills remain *specifications* until exercised; `/verification-done` is first exercised on the next real run.


---

## Entry 005 — Standardizing work-tracking: the three-tier funnel as AIDLC-blueprint infrastructure

**Date:** 2026-09-27 · **Contributor(s):** Agni Eialarasu (`arasu@agnitechnologies.com`), AI-assisted · **Mode:** Kiro Web (brainstorm & planning) · **Outcome:** `RFC-LAB-000-010` (Portfolio & Sprint Tracking Model); TSK-051 (refactor Spec, deferred)

> _Decisions D26–D28 were made by Agni Eialarasu (human-directed), AI-assisted in execution/validation._

Follows Entry 004, in the same session that closed SPRINT-08 (v0.10.0). With the lifecycle proven on real work, the human moved to standardize the *tracking* substrate — explicitly framing `LAB-000` as **the proven blueprint for the AIDLC framework**, so the model must be industry-standard and portable, not bespoke.

---

### D26 — Retire the conflated single-file tracking; adopt the three-tier funnel as distinct artifacts
- **Trigger:** The human proposed a clean separation: sprint-tracker = scoped/planned-for-implementation; backlog = idea bucket (scope-or-shelf); changelog = completed history — and asked for the best industry-standard practice, since this is the blueprint.
- **Options:** (A) keep the current single `BACKLOG.md` (sprint + ideas together), formalize semantics in place; (B) split a dedicated **`SPRINT_TRACKER.md`** (committed/in-flight) from `BACKLOG.md` (ideas only), with `CHANGELOG.md` as shipped history.
- **Decision & rationale:** **Option B — split.** The human's three-bucket intuition maps 1:1 onto the standard **Product Backlog → Sprint Backlog → Release** funnel; for a *portable blueprint*, the three concerns should be *physically distinct files* so any reader/agent sees the funnel immediately. Matches the Nexus Pulse `SPRINT_TRACKER.md`/`BACKLOG.md` separation (adapted). The agent noted this is mostly *formalizing what the repo already does* — the value is structure + portability, not new mechanics. _(Contributor: Agni Eialarasu)_
- **Outcome:** `RFC-LAB-000-010` §3.

### D27 — One vocabulary everywhere: tracker status = the lifecycle state machine; Definition of Ready = "Spec merged"
- **Trigger:** Designing the tracker's status column — reuse the `RFC-LAB-000-009` state machine, or a separate tracker dialect?
- **Decision & rationale:** **Reuse the state machine verbatim** (`Ready`=`READY_TO_BUILD`, `In Verification`=`IN_VERIFICATION`, `In Review`=`IN_REVIEW`, `Done`=`RECORDED`) — one vocabulary across tracker, commands, and guide is the blueprint payoff and prevents dialect drift. And **Definition of Ready (backlog → sprint) = the Spec is merged to `main`** — i.e. the merge-first `/plan-done` transition. This makes **the funnel *be* the lifecycle**: "sprint-ready" isn't a separate judgment, it's the `READY_TO_BUILD` state — closing the classic "half-baked items enter the sprint" failure. _(Contributor: Agni Eialarasu)_
- **Outcome:** `RFC-LAB-000-010` §4–§5.

### D28 — Make it blueprint-grade: explicit traceability chain + dogfood the refactor as a Spec; RFC now, refactor later
- **Trigger:** The "this is the proven model for the framework" framing raised the bar beyond a solo repo's convenience.
- **Decision & rationale:** Add an explicit **traceability chain** (`BK → TSK → Spec → PR → CHANGELOG → tag`) so an idea can be walked to its shipped code and back — the auditable thread a governed AIDLC framework needs. Sequence the work **RFC-first, then a follow-on Spec** for the mechanical refactor (`TSK-051`) — and run that refactor *through the AIDLC lifecycle itself*, so the blueprint is **proven on its own repo** (dogfood). Kept **git-native** — no external tracker (Jira/Linear) — to stay portable. _(Contributor: Agni Eialarasu)_
- **Outcome:** `RFC-LAB-000-010` §6/§9; TSK-051 backlog item.

---

### Session meta
- **Theme:** treating *work-tracking as framework infrastructure* — because the repo is the blueprint, its tracking must be standard and portable, not personal convenience.
- **Notable judgment:** the human independently arrived at the textbook three-tier funnel, then insisted the vocabulary and readiness gate **reuse the lifecycle** (one system, not two) — and that the refactor be dogfooded through that lifecycle.
- **Also captured (process tip):** agreed a `/brainstorm-save` trigger heuristic — save when a session made a *decision* (choice between options / direction set / course-correction / trade-off accepted), not for routine execution; `/plan-done` is the natural trigger point.
- **Honest note:** `RFC-LAB-000-010` is the decision only; the tracking files still use the old single-file layout until the `TSK-051` refactor Spec ships. Merge-first: the RFC lands before any skill targets the new structure.


---

## Entry 006 — Doc-system standardization, deployment unblock, and the next feature horizon

**Date:** 2026-09-27 · **Contributor(s):** Agni Eialarasu (`arasu@agnitechnologies.com`), AI-assisted · **Mode:** Kiro Web (brainstorm & planning) · **Outcome:** `docs-reorganization` Spec (TSK-052); `RFC-LAB-000-011` deployment queued (TSK-053); backlog `BK-012`–`BK-015`

> _Decisions D29–D31 were made by Agni Eialarasu (human-directed), AI-assisted in execution/validation._

A `/plan-start` brainstorm surfacing five items (doc org, project CRUD, branding, app settings, AI integration) plus two mid-session additions (retire the build artifact; org approval for Vercel/GCP). Triaged into one Spec + one queued RFC + four backlog features.

---

### D29 — Standardize the doc system as blueprint infrastructure (grouped folders + a nav standard)
- **Trigger:** The human asked to audit README/`docs/`: standardized? logically grouped? smooth navigation both ways? The audit found a flat `docs/`, one-way navigation (8 of 10 docs are dead-ends), 3 orphaned docs, and a stale README tree.
- **Options:** (A) do the tidy directly (docs fast-path); (B) a Kiro Spec with a documented, copyable nav standard.
- **Decision & rationale:** **Option B + a documented nav standard**, explicitly *because this repo is the blueprint others copy* — the doc system should be standardized deliberately. Group `docs/` into `guides/reference/governance/rfc`; add a `docs/README.md` hub + a breadcrumb standard referenced from `AGENTS.md`; rename `work-environment` → `developer-guide`. Running it as a Spec (not a quick edit) is justified because file moves break links — a Human Verification Plan ("zero broken links") earns its keep, and it's a low-risk second/third AIDLC dogfood. _(Contributor: Agni Eialarasu)_
- **Outcome:** `docs-reorganization` Spec (TSK-052).

### D30 — Deployment unblocked (Vercel + GCP); it supersedes the Pages stopgap and absorbs the artifact retirement
- **Trigger:** The human granted two updates: retire the obsolete build artifact (`docs/index.html`), and org approval to deploy frontend → **Vercel**, PocketBase → **GCP**.
- **The realization (agent-surfaced):** these are one story. `docs/index.html` + `deploy-pages.yml` are the GitHub-Pages *stopgap* dashboard; moving the frontend to Vercel **replaces** it. And this **clears the exact blocker MVP M5 was waiting on** (`RFC-LAB-000-008`: "deploy blocked on org-transfer"; `RFC-LAB-000-007` staging placeholders "pending org transfer").
- **Decision & rationale:** Treat deployment as an **architecture decision → new `RFC-LAB-000-011`** (amending 007/008), **not** a quick task; **retire the Pages dashboard *within* that deployment work**, not in the docs Spec — deleting it earlier would leave no live dashboard mid-cutover. Sequenced as the **next planning item** after the docs Spec, given it now gates the MVP finish line. _(Contributor: Agni Eialarasu)_
- **Outcome:** `RFC-LAB-000-011` queued (TSK-053); `index.html` retirement scoped out of the docs Spec.

### D31 — Feature horizon triaged; settings-before-branding; CRUD/AI framed against the MVP path
- **Trigger:** Three feature ideas (admin project CRUD, branding/white-label, app settings) plus the flagship AI-assistant.
- **Decision & rationale:**
  - **App settings (`BK-012`) is the foundation; branding (`BK-013`) is its first consumer** — name/description/logo are configurable *settings*, so build one config system, not two.
  - **Admin project CRUD (`BK-014`) is a superset of MVP M4**, needing auth (M2) + an admin role that `RFC-LAB-000-008` deferred (5-role model) — so it's post-MVP, not standalone.
  - **AI assistant (`BK-015`) is the flagship** ("ask casual questions about the project, grounded in repo + docs") — highest value *and* effort; needs its own RFC + feasibility spike (index/model/cost/data-boundaries) before scoping.
  - All shelved as `BK-` with explicit coupling notes rather than half-scoped now. _(Contributor: Agni Eialarasu)_
- **Outcome:** `BK-012`–`BK-015` with dependency annotations.

---

### Session meta
- **Theme:** turning a loose idea list into a triaged plan — one actionable Spec now, one newly-unblocked architecture RFC next, four coupled features shelved with honest dependencies.
- **Notable judgment:** the human's "this is the blueprint" lens repeatedly raised the bar (docs → a documented standard, not a tidy); the agent surfaced that "retire index.html" and "deploy to Vercel/GCP" are the same decision and that it unblocks M5.
- **Process note:** confirmed the `/brainstorm-save` trigger heuristic in practice — this session had real decisions (D29–D31), so it's captured; pure Spec-authoring sessions (e.g. the refactor Spec) were correctly skipped.
- **Honest note:** none of D29–D31 is built yet — the docs Spec is authored (merge-first pending), the deployment RFC is only *queued*, and BK-012–015 are shelf items. Scope stays honest: decisions + plan, not delivery.


---

## Entry 007 — Deployment architecture: Vercel + GCP, and retiring the Pages stopgap

**Date:** 2026-09-27 · **Contributor(s):** Agni Eialarasu (`arasu@agnitechnologies.com`), AI-assisted · **Mode:** Kiro Web (brainstorm & planning) · **Outcome:** `RFC-LAB-000-011` (deployment); TSK-053 (RFC) + TSK-054 (M5 execution)

> _Decisions D32–D35 were made by Agni Eialarasu (human-directed), AI-assisted in execution/validation._

Resumed the parked `/plan-start RFC-011`. With org approval granted (Entry 006, D30), MVP **M5 is unblocked**; this session decided the deployment topology the prior RFCs deferred (`RFC-LAB-000-007` §6, `RFC-LAB-000-008` §9).

---

### D32 — PocketBase on a small always-on GCP VM (not Cloud Run) for the MVP
- **Trigger:** Where/how to host PocketBase on GCP — it's a single binary + a SQLite file, so *state* is the crux.
- **Options:** (a) Cloud Run + mounted persistent volume (the containerized path RFC-007 provisioned); (b) a small always-on VM (`e2-micro`) + persistent disk running the binary.
- **Decision & rationale:** **(b) the VM.** SQLite + a single binary is happiest as one always-on process on a persistent disk; Cloud Run's scale-to-zero + volume + single-writer-SQLite semantics add complexity for no real gain at control-hub scale. Trade-off accepted: minimal always-on cost for operational simplicity and local↔prod parity. The container/Cloud Run + managed-DB path stays the documented **forward option** if the datastore grows. _(Contributor: Agni Eialarasu)_
- **Outcome:** `RFC-LAB-000-011` §4.1.

### D33 — Frontend on Vercel; dual-run then retire the GitHub-Pages stopgap
- **Trigger:** The SvelteKit SPA needs a real host; the Pages dashboard (`index.html`) is the interim artifact to retire (Entry 006, D30).
- **Decision & rationale:** **Vercel** (first-class SvelteKit, env vars, preview deploys, easy custom-domain later; near-drop-in for a static SPA). **Dual-run** Vercel alongside Pages during transition, verify against live GCP PocketBase, **then retire** Pages (`index.html` + `deploy-pages.yml` + generator) — completing the artifact-retirement decision safely (no gap with no live dashboard). _(Contributor: Agni Eialarasu)_
- **Outcome:** `RFC-LAB-000-011` §4.2.

### D34 — Secrets split by surface (resolves RFC-007 §6 OQ-2)
- **Decision & rationale:** **Vercel env vars** for the frontend (`VITE_PB_URL` → GCP PocketBase; non-secret but env-managed per environment); **VM env / GCP Secret Manager** for backend secrets (PocketBase superuser, GitHub OAuth id/secret). VM env for MVP simplicity, Secret Manager as the hardening step. Nothing real committed. _(Contributor: Agni Eialarasu)_
- **Outcome:** `RFC-LAB-000-011` §4.3; amends `RFC-LAB-000-007` §6.

### D35 — Custom domain deferred to branding (`BK-013`); RFC decides, Spec deploys
- **Decision & rationale:** Ship M5 on Vercel's default domain (usable, HTTPS); the **custom domain is a white-labeling concern** — wire it per-client when branding lands, so M5 isn't gated on domain/DNS decisions. And a scoping call: **`RFC-LAB-000-011` is the decision of record only** — the actual provisioning is **execution** delivered as M5 Kiro Spec(s) (`TSK-054`) via the lifecycle, keeping the RFC a clean, mergeable planning artifact. Sequencing resolved: **backend (GCP) first** (frontend needs a live `VITE_PB_URL`), then Vercel, then Pages retirement; authenticated deploy depends on M2, but a public read-only deploy could precede it. _(Contributor: Agni Eialarasu)_
- **Outcome:** `RFC-LAB-000-011` §4.4/§5/§6; amends `RFC-LAB-000-008` §9.3.

---

### Session meta
- **Theme:** resolving the long-deferred deployment architecture the moment its blocker (org approval) cleared — turning "GCP/Vercel someday" into concrete, rationale-backed choices.
- **Notable judgment:** the human chose **operational simplicity over cloud-native sophistication** (VM over Cloud Run) appropriate to scale, while explicitly preserving the forward path; and kept the RFC a *decision* separate from *execution* (M5 Specs).
- **Process note (honest, from this session):** the preceding lockstep tidy caught that the docs-reorg run never added its CHANGELOG entry — and that `/review-pr` had marked lockstep green without verifying the CHANGELOG firsthand. Flagged for a `/review-pr` tightening (check the TSK id is actually in CHANGELOG). Recorded because credible process improvement includes catching the gate's own misses.
- **Honest note:** nothing is deployed — `RFC-LAB-000-011` decides; `TSK-054` (M5 execution) is shelved for the lifecycle. Authenticated deploy still depends on M2 (OAuth), not yet built.


---

## Entry 008 — RBAC engine and status storage for the MVP owner-write path

**Date:** 2026-09-27 · **Contributor(s):** Agni Eialarasu (`arasu@agnitechnologies.com`), AI-assisted · **Mode:** Kiro Web (brainstorm & planning) · **Outcome:** `mvp-m3-m4-rbac-owner-writes` Spec (TSK-050)

> _Decisions D36–D37 were made by Agni Eialarasu (human-directed), AI-assisted in execution/validation._

Planning M3 (minimum RBAC) + M4 (owner write path). Two decisions settled before authoring the Spec.

### D36 — RBAC engine = PocketBase API rules; no RBAC library
- **Trigger:** The human asked directly, "what RBAC library are we going to use?" before planning M3.
- **Options:** (a) an RBAC library (Casbin/oso/etc.) layered on the app; (b) PocketBase'"'"'s built-in per-collection API rules.
- **Decision & rationale:** **(b) — no library.** RBAC is enforced by **PocketBase per-collection API rules** (server-side filter expressions), already in use since M1/M2 and the owner `updateRule` already provisioned. A library would **duplicate what the datastore enforces and split the source of truth** — and PocketBase-with-built-in-rules was *the reason* PocketBase was chosen over bespoke FastAPI+Postgres (`RFC-LAB-000-003`, D4). Key framing captured: **enforcement = the rule (server, authoritative); UI show/hide = UX only, never the security boundary** — so M3 must *test* a non-owner 403, not trust a hidden button. The 5-role `memberships` model stays deferred (`RFC-LAB-000-008` §4); richer future RBAC is still *rules* (joining `memberships`), not a library. _(Contributor: Agni Eialarasu)_
- **Outcome:** `mvp-m3-m4-rbac-owner-writes` §2/§R1/§R5.

### D37 — MVP status storage = a minimal field on `projects` (§9.1 option a), dual-track with `status.json`
- **Trigger:** M4 ("owner edits status") needs a *place* to write — but `projects` has no status field today; status lives in `status.json`.
- **Options:** (a) a minimal owner-editable status field on `projects`; (b) bring the deferred `status_snapshots` history collection forward.
- **Decision & rationale:** **(a)** — matches `RFC-LAB-000-008` §9.1'"'"'s own lean. The owner `updateRule` already covers new fields, so M4 is "add a field + wire one write"; `status_snapshots` history is deferred (option b would balloon M4). Honest wrinkle surfaced + accepted: this creates **two status sources** for MVP — the PB `status_*` field (owner-editable, in-app) and `status.json` (the executive-broadcast cadence). Chosen to **run them dual-track for MVP** (the UI reads the PB field back so edits are visible; the broadcast cadence stays untouched), with **reconciliation deferred post-MVP**. Combined into **one Spec** (M3+M4 ship together — the owner rule is meaningless without the write UI). _(Contributor: Agni Eialarasu)_
- **Outcome:** `mvp-m3-m4-rbac-owner-writes` §R2/§R4/§R6; two-source reality documented dual-track.

### Session meta
- **Theme:** settling the *architecture* questions M3–M4 hinge on (enforcement engine, status home) before scoping — so the Spec implements decisions rather than discovering them mid-build.
- **Notable judgment:** "don'"'"'t reinvent" again (built-in rules over a library, echoing D11/D15 on Specs-over-PROMPT.md); and choosing the minimal status field while *honestly naming* the two-source tension rather than hiding it.
- **Honest note:** nothing built — the Spec is authored (merge-first pending). M3–M4 completes the MVP'"'"'s *local* auth loop; only M5 (deploy) then remains.


---

## Entry 009 — Mini AIDLC: a POC-speed model with a graduation path to standard

**Date:** 2026-09-27 · **Contributor(s):** Agni Eialarasu (`arasu@agnitechnologies.com`), AI-assisted · **Mode:** Kiro Web (brainstorm & planning) · **Outcome:** `templates/aidlc-mini/` scaffold (KICKSTART + POC-LOG + POC-SPEC + MIGRATION + `/graduate` skill)

> _Decisions D38–D40 were made by Agni Eialarasu (human-directed), AI-assisted in execution/validation._

Kicking off a new POC, the human wanted to run AIDLC **from the start** — but in a **mini** mode: faster loop, less ceremony, generic + tech-stack-independent, with a clean path to migrate to the standard model if the POC is approved. Framed as a maturity ladder: **POC (mini) → MVP (standard) → Product (extended)**.

### D38 — A three-tier maturity ladder, same shape at every tier
- **Trigger:** Full LAB-000 ceremony is too heavy for a throwaway-ish POC, but a *different* lightweight process would create a painful rewrite at migration.
- **Decision & rationale:** Define **Mini AIDLC** as the *same shape* (brainstorm→implement→verify→done, human-gated) with less ceremony — so migration is "add rigor," not "rewrite." Process formality scales with product maturity, mirroring the *contract* progressive-formality already in `RFC-LAB-000-009` §5, one level up. _(Contributor: Agni Eialarasu)_
- **Outcome:** the ladder in `KICKSTART.md` §0; scaffold under `templates/aidlc-mini/`.

### D39 — The keep/relax/defer cut (what "mini" means, concretely)
- **Trigger:** "Faster/lighter" is meaningless unless *what's optional* is defined.
- **Decision & rationale:** **Non-negotiable even at POC:** the phase shape, the **human gate**, and the Decision Journal (the human held the line on the gate explicitly — cheap, and the habit that makes migration seamless). **Relaxed:** contract → one `POC-SPEC.md`; verify → eyeball checklist; git → commit-freely/milestone-PRs; tracker/changelog/journal → **collapsed into one sectioned `POC-LOG.md`**. **Deferred to standard:** RFCs (POC decisions → journal), merge-first, state machine + guards, validators/lockstep, the command suite, the two-surface split. _(Contributor: Agni Eialarasu)_
- **Outcome:** `KICKSTART.md` §1–§3; `POC-LOG.md` collapsed artifact.

### D40 — `POC-LOG.md` is the seed crystal; `/graduate` derives-then-freezes
- **Trigger:** The human articulated the migration precisely: at POC→MVP, SPRINT_TRACKER + BACKLOG are *derived from* `POC-LOG`, and `POC-LOG` *becomes a historical reference*.
- **Decision & rationale:** Make it a **first-class, documented, commanded transition** — **`/graduate`** (named for the maturity ladder; distinct from data-migration connotations). `POC-LOG.md` is **pre-sectioned along the graduation seams** (§Decisions/§Now/§Ideas/§Shipped/§Spec) so graduation is a clean *lift*: §Now→SPRINT_TRACKER, §Ideas→BACKLOG (forward-looking, migrated); §Shipped→CHANGELOG, §Decisions→DECISION-JOURNAL (historical, carried forward); §Spec→full Kiro Spec; then **freeze `POC-LOG.md`** (kept, not deleted) + add the deferred rigor — **human-gated**. The command + runbook **ship inside the scaffold** so any POC is self-contained and generic. _(Contributor: Agni Eialarasu)_
- **Outcome:** `MIGRATION.md` (derivation map + graduation checklist); `skills/graduate/SKILL.md`.

### Session meta
- **Theme:** generalizing the method into a *reusable, tech-agnostic POC kickstarter* — the blueprint producing a smaller blueprint, with an explicit ramp between them.
- **Notable judgment:** the human insisted the **human gate is non-negotiable even at POC** (speed never buys out trust), and framed the migration as *derive-then-freeze* (seed crystal) — which drove the sectioned `POC-LOG` design.
- **Honest note:** this is a **template/methodology artifact** — not yet battle-tested; its first real exercise is the new POC the human is starting. `/graduate` is a skill *spec* until first run. Built in parallel with the M3–M4 run (different paths, no collision).


---

## Entry 010 — Deployment backend: GCP VM → Railway (amend RFC-011)

**Date:** 2026-09-28 · **Contributor(s):** Agni Eialarasu (`arasu@agnitechnologies.com`), AI-assisted · **Mode:** Kiro Web (brainstorm & planning) · **Outcome:** `RFC-LAB-000-011` amended (backend host)

> _Decision D41 was made by Agni Eialarasu (human-directed), AI-assisted in execution/validation._

### D41 — Host PocketBase on Railway instead of a GCP VM
- **Trigger:** Opening `/plan-start M5`, the human corrected the target: "it's Vercel and **Railway**" — a change from `RFC-LAB-000-011`'s recorded decision (Vercel + **GCP VM**, Entry 007/D32). The agent verified the discrepancy against the merged RFC before acting rather than silently switching.
- **Options:** (a) keep the recorded **GCP VM**; (b) **Railway** for the PocketBase backend.
- **Decision & rationale:** **(b) Railway.** It delivers the *exact* model RFC-011 wanted — **one always-on process + a persistent volume** for PocketBase's single-binary+SQLite — as a **managed platform**, removing the very GCP-VM burdens the RFC had listed as risks: **no manual patching, firewall, or reverse-proxy/Let's-Encrypt HTTPS** (Railway provides TLS + domain out of the box). Vercel-like DX on the backend; local↔prod parity preserved (same binary + volume; the `Containerfile` deploys directly). Trade-off accepted: platform lock-in + usage cost vs. raw-VM control — worth it at control-hub scale; the `Containerfile` keeps it portable. **Everything else in RFC-011 stands** (Vercel frontend, dual-run→retire-Pages, secrets split → Railway env vars + Vercel env vars, custom-domain-deferred). _(Contributor: Agni Eialarasu)_
- **Process note:** handled as a proper **amendment to a merged decision-of-record** — an amendment banner + a superseding §4.1a on RFC-011 (original §4.1 retained for history), this journal entry, merge-first — *before* the M5 execution Spec references it. The blueprint's integrity requires the RFC to match reality, not drift silently.
- **Outcome:** `RFC-LAB-000-011` amended (title, §2.2, §4.1a, §6, §8, §9); M5 execution Spec (`TSK-054`) to be authored against Railway next.

---

## Entry 011 — BK-018 spike: root-causing PocketBase 0.40 OAuth-through-Railway, and un-pinning via the redirect flow

**Date:** 2026-09-26 · **Contributor(s):** Agni Eialarasu (`arasu@agnitechnologies.com`), AI-assisted · **Mode:** Kiro IDE (investigation spike — reproduce & diagnose) · **Outcome:** `spike-bk018-pb040-oauth` finding (root cause confirmed, H1 chosen); `RFC-LAB-000-011` amended (PB version); fix Spec `fix-bk018-oauth-redirect` scoped

> _Decisions D42–D43 were made by Agni Eialarasu (human-directed), AI-assisted in execution/validation._

Follows the M5 deploy (Entry 010). M5 shipped only because prod was **pinned to PocketBase 0.28.4** — 0.40.x broke GitHub OAuth behind Railway's proxy with `/api/realtime 400`. `BK-018` was logged to root-cause that (deliberately a **spike, not a Spec** — the symptom was known but the mechanism wasn't, so writing EARS acceptance criteria would have been guessing). This session ran the spike collaboratively: the agent owned repo/build/analysis, the human owned the Railway/Vercel/browser console.

### D42 — Establish a *valid* reproduction before trusting any result (the false-negative catch)
- **Trigger:** The first attempt — a Vercel **preview** branch wired to a throwaway 0.40 Railway instance — appeared to show OAuth **succeeding** (no 400, 6 projects, signed in). Taken at face value, that would have "closed" the spike with "can't reproduce, maybe un-pin." The agent instead cross-checked the two backends and found a contradiction: the throwaway 0.40 had **no `projects` collection** (`Missing collection context`), yet the preview showed 6 projects — which only exist on **prod 0.28.4**.
- **Root of the trap:** Vercel's env-var scoping (`VITE_PB_URL` set "Production and Preview", secret-vs-config lock, build-time inlining by Vite) meant the preview had baked in the **prod** URL, not the throwaway. The "non-reproduction" was an artifact of testing the *wrong backend*.
- **Decision & rationale:** **Don't debug through the ambiguous surface — make the test deterministic.** Build the spike frontend **locally** with `VITE_PB_URL` set explicitly to the throwaway, then **verify the built bundle** before testing (`grep`: throwaway URL present ×1, prod URL ×0). Only then serve it (`vite preview`) and sign in. This removed every layer of Vercel/CLI ambiguity that had burned two prior attempts. _(Contributor: Agni Eialarasu; false-negative surfaced by AI, human-directed the pivot to local build)_
- **Outcome:** a bundle-verified 0.40-wired build; reproduction confirmed against the genuine throwaway 0.40 (`/api/realtime` **400**). The "verify the artifact, don't trust the setting" discipline is the reusable lesson.

### D43 — Root cause = 0.40 realtime handshake vs. Railway SSE proxying; fix = redirect OAuth (H1), which un-pins prod to 0.40+
- **Trigger:** With a valid reproduction, pin down *why* the realtime client is "invalid" through the proxy — the spike's actual acceptance bar (mechanism, not symptom).
- **Mechanism confirmed:** the all-in-one popup flow (`authWithOAuth2`) receives the OAuth callback over PocketBase's **realtime channel** — a two-step handshake: (1) `GET /api/realtime` opens an SSE stream, returns a `clientId` (verified working through Railway: `PB_CONNECT` + 200); (2) `POST /api/realtime` registers `{clientId, subscriptions:["@oauth2"]}` against that live stream — this **fails** on 0.40 (`400` / `"Missing or invalid client id"`). Railway's edge proxy doesn't preserve the SSE connection/affinity that **0.40** requires to tie the POST to the live `clientId`; the subscribe is rejected and the popup never gets its callback. Not a version-pairing issue (works locally, no proxy) and absent on 0.28.4 (older, more tolerant realtime path).
- **Options:** **H1** — switch to the redirect-based `authWithOAuth2Code` (no realtime channel at all); **H2** — make SSE work through Railway (proxy/CORS/trusted-proxy tuning); **H3** — declare it a genuine 0.40 regression and stay pinned.
- **Decision & rationale:** **H1.** The redirect flow does a plain OAuth `code` exchange and **never touches `/api/realtime`**, so the proxy/SSE incompatibility structurally cannot occur — and it's PocketBase's recommended production flow (popups are fragile regardless). H2 was rejected: it depends on Railway proxy internals we don't control and would leave a fragile SSE dependency on the *critical sign-in path*. Crucially, **H1 removes the only reason prod is pinned to 0.28.4 → prod can un-pin to 0.40+.** UX change (popup → full-page redirect) accepted as standard and more robust. Guardrail honored: **no prod change from the spike itself** — the live backend stays 0.28.4 until the fix Spec ships through the normal gate; all testing used a throwaway instance. _(Contributor: Agni Eialarasu)_
- **Outcome:** finding recorded in `.kiro/specs/spike-bk018-pb040-oauth/SPIKE.md` §6; `RFC-LAB-000-011` amended (PB-version note: 0.40+ supported via redirect OAuth); fix Spec **`fix-bk018-oauth-redirect`** scoped — swap `signInWithGitHub()` at `app/web/src/lib/auth.svelte.ts` to `authWithOAuth2Code`, preserve the `github_handle` hook + owner-write resolution (R3), then un-pin the `Containerfile` to 0.40.x. Spike branch `spike/bk018-pb040-oauth` stays **unmerged** (it was the test rig).

### Session meta
- **Theme:** a disciplined investigation spike — the value was as much in *refusing to trust a convenient green result* as in the diagnosis itself.
- **Notable judgment:** the human directed the pivot away from wrestling Vercel's confusing env UI toward a deterministic local build; the agent's cross-check of the two backends caught a false negative that would otherwise have produced a wrong "un-pin, it's fine" conclusion.
- **Honest note:** two earlier reproduction attempts were invalid (preview silently hitting prod) — recorded deliberately, because the credible finding is precisely the one that survived that scrutiny. The chosen fix (H1) is evidence-backed but **not yet shipped**; it ships and is human-verified via its own Spec.


---

## Entry 012 — Process retro: the BK-018 spike bypassed the gate; deploy-DX is the real fix

**Date:** 2026-09-28 · **Contributor(s):** Agni Eialarasu (`arasu@agnitechnologies.com`), AI-assisted · **Mode:** Kiro Web (brainstorm & planning) · **Outcome:** spike branch cleanup; motivates the CLI + casual-environment RFC (`BK-017`)

> _Honest retrospective. The spike **succeeded technically** (Entry 011: root cause confirmed, fix direction chosen) but its **execution collapsed the protocol** — recorded here because credible decision-making includes the misses._

### What went wrong (process, not content)
- **The gate was bypassed.** During the BK-018 spike run, commits landed **directly on `main`** (`3ff88fc`, `16f52a3`, `733309e`), and a fix Spec was both **authored and reverted on `main`** (`9d62965` → `20375e8`) instead of on a branch via PR. Merge-first + the human PR gate — the core safety rails — were not followed. `main` was left clean and the MVP intact, but the *discipline* lapsed.
- **The runtime-ops pain compounded it.** The "ops-less" managed stack (Railway/Vercel via their UIs) became the source of friction: Vercel env scoping (Prod vs Preview), Secret→Config locks, root-directory doubling, and Vite build-time inlining silently pointing a "verification" build at the **prod** backend — a false negative that nearly derailed the diagnosis (Entry 011 / spike REPORT §4).

### D44 — Cleanup: abandon the spike branch, keep the finding, note the breach
- **Decision:** delete the throwaway `spike/bk018-pb040-oauth` branch (its un-pin/reproduction commits must never reach prod; the *finding* is already on `main` via `16f52a3`). Leave the revert pair as honest history. Record this retro rather than quietly moving on. _(Contributor: Agni Eialarasu)_
- **Lesson folded back:** *a spike is still gated* — even exploratory work commits on a branch, never straight to `main`; the spike'"'"'s *code* is throwaway, but the *governance discipline* is not.

### D45 — The real fix is deploy-DX: CLI + casual-environment promotion (→ BK-017 RFC)
- **Trigger:** the human, tired of the UI-driven ops pain, proposed: use **Railway CLI + Vercel CLI** for on-demand ad-hoc deploys, and **treat staging/prod casually — like local — until verified**, then qualify the environment and rotate real secrets via the UI.
- **Decision & rationale:** adopt both, as a proper RFC (`BK-017` scope). CLI + repo-committed config (e.g. the `vercel.json` already landed) is **reproducible and scriptable** — the UI path is what produced the false negatives. The **environment-promotion model** (casual throwaway creds → verify working → *qualify* → rotate real secrets) matches how the team already treats local, and de-risks first-time staging/prod setup. **Guardrail:** never commit secrets (throwaway or real) — env files stay gitignored; "casual" means shared throwaway creds in a throwaway instance, not secrets in git. Plus a concrete lesson: **verify the built artifact, not the setting** (assert the baked-in `VITE_PB_URL` in the bundle). _(Contributor: Agni Eialarasu)_
- **Outcome (planned):** a CLI + casual-environment-promotion RFC (`BK-017`); the BK-018 OAuth fix (`fix-bk018-oauth-redirect`) is **deferred until that DX exists**, so the fix isn'"'"'t verified through the same painful UI path that caused this.

### Session meta
- **Theme:** don'"'"'t re-enter the thing that caused the pain through the same door — fix the *deploy DX* first, then resume the fix.
- **Honest note:** the spike'"'"'s technical result stands (Entry 011); this entry is strictly about the process lapse + the corrective. The gate-bypass is the kind of thing the lifecycle exists to prevent — naming it keeps the blueprint credible.


---

## Entry 013 — Deploy operations: CLI-first + casual→qualified environments (RFC-012)

**Date:** 2026-09-28 · **Contributor(s):** Agni Eialarasu (`arasu@agnitechnologies.com`), AI-assisted · **Mode:** Kiro Web (brainstorm & planning) · **Outcome:** `RFC-LAB-000-012` (deploy operations); `BK-020` (status-drift fix); `BK-017` gets its decision of record

> _Decisions D46–D48 were made by Agni Eialarasu (human-directed), AI-assisted in execution/validation._

Follows Entry 012 (the BK-018 spike'"'"'s process breach + UI-driven ops pain). `RFC-011` decided *what* we deploy to; this session decided *how we operate deploys* — the missing piece that made M5 + the spike painful.

### D46 — CLI-first deploys (Railway CLI + Vercel CLI), repo-committed config
- **Trigger:** the human, tired of "understanding each UI," proposed CLI-based on-demand deploys with UI only for verification.
- **Decision & rationale:** all ad-hoc/iterative deploys go through the **Railway + Vercel CLIs** with **committed config** (`vercel.json` already landed; `railway.json`, `.env.*.example` to follow); UIs are for one-time linking + inspection, not the loop. The audit backs this: the UI path (env scoping, Secret→Config locks, root-dir doubling) is what produced the BK-018 false negatives. CLI + committed config is reproducible, scriptable, greppable. _(Contributor: Agni Eialarasu)_
- **Outcome:** `RFC-LAB-000-012` §3.

### D47 — Casual → qualified environment promotion
- **Trigger:** first-time staging/prod setup is miserable when you must wrestle real secrets up front; the human wanted to "treat it like local and go casual, then harden once qualified."
- **Decision & rationale:** every deployed env has a lifecycle — **CASUAL** (throwaway creds, throwaway instance, iterate freely, don'"'"'t sweat secrets) → verify working → **QUALIFIED** (rotate real secrets via UI, lock down, treat as real). Mirrors how local is already treated; de-risks first-time setup. **Guardrail (non-negotiable):** no secrets in git at *any* stage — "casual" = throwaway creds in a throwaway instance, never committed. _(Contributor: Agni Eialarasu)_
- **Outcome:** `RFC-LAB-000-012` §4.

### D48 — Two spike lessons codified: verify-the-artifact + gates-apply-to-ops
- **Decision & rationale:** (a) **"Verify the artifact, not the setting"** — for build-time-inlined config (Vite `VITE_*`), assert the baked-in value in the *bundle* before trusting a live test (the exact false negative that nearly derailed BK-018). (b) **Gates apply to ops/spikes too** — even throwaway spike code goes on a branch, never `main` (Entry 012'"'"'s breach, codified). Also folded in: the recurring **`status.json` date-drift** (5 CI failures) → make the check date-tolerant (`BK-020`). _(Contributor: Agni Eialarasu)_
- **Outcome:** `RFC-LAB-000-012` §5/§6/§7; `BK-020`.

### Session meta
- **Theme:** fix the *deploy DX* (the source of the pain) before resuming the BK-018 OAuth fix — don'"'"'t re-enter the pain through the same door.
- **Sequencing:** RFC now (decision) → deploy-scaffold Spec (CLI wrappers + artifact-assertion helper + status-drift fix) → *then* the BK-018 fix Spec, verified via the new CLI flow.
- **Honest note:** this RFC is `BK-017`'"'"'s decision of record; nothing built yet — the scaffold + fixes are the follow-on Spec.

---

## Entry 014 — AIDLC scope boundary: `done = live-on-main`; multi-env promotion is DevOps (out of scope)

**Date:** 2026-09-30 · **Contributor(s):** Agni Eialarasu (human-directed), AI-assisted · **Mode:** Kiro Web (brainstorm & planning) · **Outcome:** scope-boundary decision (this entry); reframes `RFC-LAB-000-012` as reference ops guidance; `BK-019` reclassified out-of-scope; new `BK-021` (make `done` observably live)

> _Decisions D49–D52 were made by Agni Eialarasu (human-directed), AI-assisted in framing/validation. This session began as "plan BK-019 (prod cutover)" and surfaced that the real question was a **scope boundary**, not a cutover task._

Follows the merge of the BK-018 fix (PR #46, `TSK-058`) which made the codebase 0.40-ready. Planning the "prod cutover" (`BK-019`) exposed that BK-019, RFC-012's promotion ladder, and the stale `status-staging` placeholders were all **operational** concerns that had crept into the **lifecycle** model. This session drew the line.

### D49 — AIDLC scope ends at `done = merged to main = live`; ops is out of scope
- **Trigger:** the human named the motto — AIDLC is `brainstorm → plan → implement → verify → done`, and **`done` = live** (merged to `main`). "Staging, UAT, Prod etc. are operational, i.e. DevOps scope — not part of this project."
- **Options:** (a) keep modeling multi-env promotion (staging→UAT→prod) inside the lifecycle; (b) declare the lifecycle's scope ends at a trustworthy, deployed `main` on a single reference environment, and treat topology/promotion/hardening as out-of-scope ops.
- **Decision & rationale:** **(b).** The LAB-000 blueprint demonstrates *how you structurally go from idea → gated, shipped code* — that is generic and dogfoodable. Environment topology is org-specific and not blueprint-able; conflating the two is what left BK-019 ambiguously "ripe?" and the `status-staging`/`validate-staging` skills stale for weeks. The lifecycle's deliverable is **trustworthy `main`**; where/how many tiers it runs in is DevOps. _(Contributor: Agni Eialarasu)_
- **Outcome:** this entry as decision of record; drives D50–D52.

### D50 — `done = live` is pragmatic (b), not strict (a): the contract is the merge, not uptime
- **Trigger:** if `done` means "deployed-and-reachable," a deploy hiccup would become a *lifecycle* failure — pulling ops back into scope through the back door.
- **Options:** (a) strict — `done` isn't reached until the deploy succeeds (deploy failure = not done); (b) pragmatic — `done` = merged to trustworthy `main`; the auto-deploy is a *consequence* that makes it live, and a deploy hiccup is an *ops* problem, not a lifecycle failure.
- **Decision & rationale:** **(b).** Keeps the lifecycle clean — its contract is the gated merge; deployment is how `done` becomes *observable*, not what defines it. Honors "deploy mechanics are ops." _(Contributor: Agni Eialarasu)_
- **Outcome:** encoded in the model; shapes the BK-021 Spec (deploy failure alerts as ops, never blocks the lifecycle).

### D51 — `main` = the single reference environment ("staging"); no prod pipeline; the PR gate IS the deploy gate
- **Trigger:** the human: "treat merge to `main` = STAGING, for both front and back… I don't want to increase the pipeline for live. Prod will be derived / a new instance later once matured."
- **Decision & rationale:** one automated environment, fed by `main`. A **merge deploys both tiers** (frontend already via Vercel Git integration; backend to match). The **gate = PR review + required CI checks** — "an invalid build should not reach `main`," so everything on `main` is deployable; no separate, painful post-merge approval. **No staging→prod promotion pipeline** is built; real prod is derived later (ops), when matured. _(Contributor: Agni Eialarasu)_
- **Outcome:** `BK-021` Spec; branch-protection/required-checks as the gate.

### D52 — Reclassify the ops artifacts: RFC-012 → reference guidance; BK-019 out-of-scope; BK-021 = the minimal bridge
- **Decision & rationale:** (a) **`RFC-LAB-000-012`** stands as **optional reference ops guidance**, not part of the lifecycle contract (its casual→qualified promotion ladder is ops doctrine). (b) **`BK-019`** ("dedicated prod, domain, backup discipline") is **reclassified out-of-scope / future ops** — not a sprint-blocking lifecycle item. (c) New **`BK-021`**: the *minimal bridge* that makes `done` observably live — **backend CI deploy on merge (path-filtered `app/pocketbase/**`)** to match the frontend, plus a **`/deploy-adhoc`** developer tool for ad-hoc testing against throwaway/other instances (explicitly a tool, not a lifecycle stage). The stale `status-staging`/`validate-staging` placeholders get refreshed to reflect the one-environment reality. _(Contributor: Agni Eialarasu)_
- **Outcome:** `BK-021` backlog row + Spec `automate-staging-deploy`; RFC-012 reframe note; BK-019 reclassified.

### Session meta
- **Theme:** the session that *removed* scope. Started as "plan the prod cutover," ended by declaring cutover/topology out of scope entirely — the more valuable move.
- **Course-correction:** the AI initially planned an RFC-012 *amendment extending* promotion to staging; the human's framing inverted it — RFC-012 becomes reference-only, and the plan *shrank*. Recorded honestly: the tension "if ops is out of scope, why build deploy automation?" resolved as **a deliberate boundary** — BK-021 is the thin bridge so `done` is *observably* live on the one environment; it is explicitly the edge of scope, not a promotion pipeline.
- **Division of labor:** human set the scope motto and the one-environment/no-prod-pipeline calls; AI framed the boundary language, mapped it onto existing artifacts, and flagged the strict-vs-pragmatic `done=live` fork (resolved to pragmatic).

---

## Entry 015 — App-level settings: key/value collection + a typed accessor façade

**Date:** 2026-09-30 · **Contributor(s):** Agni Eialarasu (human-directed), AI-assisted · **Mode:** Kiro Web (brainstorm & planning) · **Outcome:** `RFC-LAB-000-013`; Spec `app-level-settings` (`TSK-057` / `BK-012`); enables `BK-013`

> _Decisions D53–D55 were made by Agni Eialarasu (human-directed), AI-assisted in framing. First SPRINT-11 planning session; opens the first post-MVP product feature._

Planning `BK-012` (app-level settings, the foundation for `BK-013` branding). The design brief — "initialized minimal, grown over time" — made the *shape* the pivotal call, because app settings is configuration, not the array-of-records shape the repo's existing collections use.

### D53 — Shape = key/value collection + a typed accessor façade
- **Trigger:** settings must "grow over time" cheaply, yet the app wants type-safety when reading them.
- **Options:** (A) key/value rows; (B) one typed record with a column per setting; (C) a single JSON blob.
- **Decision & rationale:** **A + a typed accessor façade.** Key/value keeps extensibility in the *data* (a new setting is a seed row, never a schema migration — the "grow freely" brief), and the typed TS accessor recovers B's safety in *one* place (getters that know each key's name, `type` cast, and default). B was rejected as the base (every setting = a migration); C rejected (no validation, corruption-prone). _(Contributor: Agni Eialarasu)_
- **Outcome:** `RFC-LAB-000-013` §2/§3/§6.

### D54 — RBAC: public read, superuser-only write (for now)
- **Decision & rationale:** **public read** (branding must render on the anonymous dashboard) + **superuser-only write**. There is no admin role yet (`RFC-LAB-000-008` deferred the 5-role model), and settings are rare/high-trust — so gating writes to superuser is the safe minimum. A lighter owner/admin write path is deferred to `BK-014` (admin CRUD). Recorded as a deliberate deferral, not an oversight. _(Contributor: Agni Eialarasu)_
- **Outcome:** `RFC-LAB-000-013` §5; Spec R2.

### D55 — Scope = the mechanism; branding UI + logo upload deferred to BK-013
- **Decision & rationale:** `BK-012` ships the *mechanism* — collection, schema, seed, typed accessors, API rules, and **read-wiring** (the app reads its own name/description from settings). **Logo upload/file handling and the branding editor UI are `BK-013`**; this RFC only *reserves* the logo keys. Keeps the Spec tight and the foundation/consumer split clean. _(Contributor: Agni Eialarasu)_
- **Outcome:** `RFC-LAB-000-013` §7; Spec §4 (out of scope).

### Session meta
- **Sequencing:** did a green `/audit-project` (portfolio healthy, no drift) before authoring, at the human's request, so BK-012 builds on verified docs. RFC + Spec authored here (Web); next `/plan-done` merges them (merge-first) → `/spec-run app-level-settings` (IDE). Then the `BK-015` AI-Assistant RFC + spike (the parallel de-risking track).
- **Division of labor:** human set the leans (key/value, superuser writes, mechanism-only scope); AI grounded them in the repo's existing collection pattern and wrote the RFC/Spec.

---

## Entry 016 — "done = live" is only true if you verify *live*: three stacked, invisible frontend-deploy failures

**Date:** 2026-09-30 · **Contributor(s):** Agni Eialarasu (human-directed — caught it live), AI-assisted (diagnosis/fix) · **Mode:** Kiro Web · **Outcome:** `BK-023` part 1 fixed (PRs #51, #52); `BK-023` part 2 / `TSK-063` opened

> _A dogfooding retro, not a design pivot. Captured because the failure mode is a reusable lesson for the blueprint._

After closing SPRINT-10 on the claim "`done` = live for both tiers" (Entry 014), a **live staging screenshot** revealed sign-in was still broken on `cetana-labs.vercel.app` — running the *old* popup OAuth flow (`/api/realtime` 400) even though the BK-018 redirect fix had been merged to `main` since PR #46. Peeling it back exposed **three stacked failures, none caught by CI or the `/review-pr` gate**:

### D56 — The failure chain (recorded so we recognize it again)
1. **`vercel.json` had a `"//"` comment key** → Vercel's schema validation *failed every build* (prod + preview) from commit `3ff88fc` onward. Vercel kept serving the last *successful* (pre-BK-018) bundle. (Fix: #51 — schema-pure `vercel.json`.)
2. **Stale bundle** → the live site ran the old popup flow (the visible symptom).
3. Once builds were green, **`/oauth/callback` 404'd** — the route is `prerender=false` (client-only) and Vercel (`framework:null`) doesn't auto-apply `adapter-static`'s `index.html` fallback for unmatched paths. (Fix: #52 — `rewrites /(.*)→/index.html`.)
- **Live-verified fixed:** signed in as Eialarasu via the redirect flow, `/api/realtime` = 0 requests — the first true end-to-end proof of the BK-018 fix on live staging. _(Contributor: Agni Eialarasu)_

### D57 — The real lesson: our gate is blind to the actual deploy
- **Trigger:** all three failures passed `/review-pr` and CI green. The gate trusts the **"Vercel Preview Comments"** check — which is *not* the Vercel build status — and our GitHub `Build Sleek UI` job runs `pnpm build` directly, never Vercel's config validation. So "green CI + merged" told us nothing about whether the frontend actually deployed.
- **Decision & rationale:** **"done = live" is only meaningful if something verifies *live*.** We proved the *backend* deploy live (BK-022) but *assumed* the frontend half. The lifecycle needs a **real deploy signal** — not a proxy check. Opened `TSK-063` (BK-023 part 2): wire a genuine Vercel-build signal and/or a post-deploy live-bundle assertion into the gate, honoring the "no extra pipeline for live" rule (a signal, not a pipeline). _(Contributor: Agni Eialarasu)_
- **Outcome:** `TSK-063`; and a standing reminder — the human checking the live site is what caught all three. Automated live-verification is the durable fix.

### Session meta
- **Division of labor:** the human caught every failure by looking at the *live* site + consoles (build error, 404, network tab); the AI diagnosed root causes against the repo and shipped the fixes via the normal branch → PR → gate. Honest note: the AI's *first* hypothesis (production pinned to an old commit) was **wrong** — the Deployments screenshot corrected it to "every build erroring." Verify against reality, don't trust the first theory.

---

## Entry 017 — Surface model refresh: KiroCrew (Operator) + Kiro IDE (Executor) + Kiro Web (fallback)

**Date:** 2026-10-01 · **Contributor(s):** Agni Eialarasu, AI-assisted · **Mode:** KiroCrew Operator (alignment session) · **Outcome:** `ai-collaboration-model.md §2` + `RFC-LAB-000-007 §2.1` (amended) + `AGENTS.md §4` + `tech.md`

> _Decisions D59–D61 were made by Agni Eialarasu (human-directed); AI surfaced the redundancy and drafted the lockstep edits._

The original work-environment model (`RFC-LAB-000-007`, D8) was a **two-surface** split: Kiro Web
(stateless brainstorm & governance) + Kiro IDE (stateful execution). Since then the human's actual
tooling changed — day-to-day work now runs on **KiroCrew** (this control layer: persistent memory,
scheduled jobs, background sub-agents, multi-session orchestration) and **Kiro IDE**. This session
realigned the governance docs to that reality so they describe the *current* state, not the
historical one.

### D59 — KiroCrew becomes the Operator (absorbs & extends the old "Kiro Web" role)
- **Trigger:** The human works across 6 projects with parallel per-topic chats, and needs a surface that *holds continuity* across those jumps — which stateless Kiro Web never did.
- **Options:** (A) keep Web as the primary brainstorm surface; (B) promote KiroCrew to the primary "Operator" surface, folding in brainstorm + plan + governance ops + persistent memory; (C) a custom split.
- **Decision & rationale:** **B.** KiroCrew already *is* the web surface plus memory/crons/orchestration, so treating Web as primary duplicated a weaker version of it. The Operator owns everything that **decides or coordinates** — brainstorm, RFC/Spec authoring, governance skills (`/project-status`, `/project-validate`, `/audit-*`, `/ping-leads`), PR review, and a durable per-project briefing. The human chose A+B explicitly ("this will be best fit… jumping to other projects will be easy and out-of-project discussion in a different chat will be in parallel").
- **Outcome:** `ai-collaboration-model.md §2` three-role table; standing operating-agreement lesson saved.

### D60 — Kiro IDE is the Executor/Worker; the gate stays human
- **Decision & rationale:** All **code execution and local verification** stay in the IDE (`/spec-run`, `/start-local`, `/validate-local`, `/verification-done`, pushing `feat/` branches). The Operator **never merges** — it opens PRs, self-validates, and STOP-and-holds at `/review-pr`. This preserves the AIDLC safety rail (D8, Entry 004): decisions and the merge gate are the human's; execution is AI-accelerated.
- **Outcome:** Reaffirmed across the amended docs; no change to the merge-gate guarantee.

### D61 — Kiro Web demoted to stateless fallback (not retired)
- **Trigger:** With KiroCrew as Operator, what remains for Web?
- **Decision & rationale:** Keep Web as a **fallback**, not a daily lane — three residual uses: (1) a throwaway brainstorm the human deliberately wants *out* of persistent memory, (2) no-install access from a machine without the KiroCrew app, (3) a cheap `.kiro/` config-sync parity check. Honest scoping over pretending Web is obsolete.
- **Outcome:** `RFC-LAB-000-007 §2.1` Amendment; `tech.md` surface note updated.

### Session meta
- **Sequencing:** this entry was authored on the Operator during an alignment session (no code). Governance/docs fast-path to `main` per `RFC-LAB-000-004`.
- **Lockstep touched:** `ai-collaboration-model.md`, `RFC-LAB-000-007`, `AGENTS.md`, `.kiro/steering/tech.md`. (The historical D8 entry above is left intact as the record of the *original* decision — this entry supersedes, it does not rewrite history.)
- **Division of labor:** human set the direction (A+B, rename to Operator/Executor); AI surfaced that Web was now redundant, proposed the fallback framing, and drafted the four lockstep edits. (Renumbered from Entry 016 / D56–D58 on merge with `origin/main`, which had independently landed an Entry 016; chronology put the 2026-09-30 BK-023 retro first.)

---

## Entry 018 — Two model refinements: a gate-free background-worker lane + Operator/Executor workspace isolation

**Date:** 2026-10-01 · **Contributor(s):** Agni Eialarasu (human-directed), AI-assisted · **Mode:** KiroCrew Operator · **Outcome:** `ai-collaboration-model.md §2` (lane + isolation note); Working Model artifact; standing lesson updated

> _Surfaced during the first full end-to-end run of the Operator/Executor model (the `push-changes-skills` build, PR #53). D62–D63 were the human's calls._

### D62 — A fourth lane: gate-free background workers for bounded specialist work
- **Trigger:** The human noted that running every delegated task through the full `/spec-run → PR → verify → review` cycle is overkill for work that is bounded, reversible, and off the protected path — and that parallel background workers are "the real benefit of working in KiroCrew."
- **Decision & rationale:** Add a **background-worker lane**: the Operator may `spawn_run` a worker for research, analysis, doc drafts, diagram data, scoped investigations, or bulk processing — it runs in parallel and returns a result the Operator validates and reports. **The merge gate is explicitly preserved:** a worker **never pushes `main` and never merges**; if its output is code destined for `main`, it still flows through `/spec-run` + a PR + the human gate. The worker produces the *artifact*; the gate decides what lands. This widens throughput without weakening the AIDLC safety rail (D8, Entry 004).
- **Guardrail:** the lane is for reversible, off-protected-path work only. Anything that becomes a `main` code change takes the full IDE Executor path.
- **Outcome:** `ai-collaboration-model.md §2` background-worker note; Working Model artifact.

### D63 — Operator and Executor work in separate clones (workspace isolation)
- **Trigger:** During PR #53, an IDE `/spec-run` was running in the *same* working tree the Operator uses — a two-writers-on-one-worktree hazard (a background worker or an Operator edit could race the build's branch/files). The earlier merge-divergence (Entry 017's merge) was the milder version of the same root issue.
- **Decision & rationale:** The Operator and the Executor use **separate clones** of the repo (Operator in `cetana-labs/`, the IDE Executor in a sibling `cetana-labs-kiro-ide/`), syncing only through `origin` — never a shared working tree. Mirrors the clean isolation the old Web+IDE split had. It removes the race entirely and lets the Operator safely spawn background workers (D62) without colliding with an IDE run.
- **Outcome:** `ai-collaboration-model.md §2` workspace-isolation note; standing lesson updated. (Setup is a human action — clone the sibling; no repo change required.)

### Session meta
- **Division of labor:** human proposed both refinements from felt pain during the live run; AI framed the guardrails (worker never merges; isolation via origin only) and did the lockstep edits. Governance/docs fast-path to `main` per `RFC-LAB-000-004`.

---

## Entry 019 — The gate verdict must be recorded transactionally on the PR, not just in chat

**Date:** 2026-10-01 · **Contributor(s):** Agni Eialarasu (human-directed — spotted the gap), AI-assisted · **Mode:** KiroCrew Operator · **Outcome:** `review-record` Spec (authored); PR #54 gate comment posted; `fix/stale-web-surface-wording` PR #55

> _Surfaced during the first real `/review-pr` run on the Operator (PR #54). D64 is the human's call; captured here because it tightens the governance guarantee (`§6`)._

### D64 — A `/review-pr` verdict is only trustworthy if it is durably attached to the PR
- **Trigger:** The Operator reviewed PR #54 and reported **READY** — but the verdict existed *only in chat*. The human asked: is this transactionally captured anywhere? It wasn't. Nothing on the PR recorded that the gate ran, what it checked, or its finding — a gap in the model's own **auditable** guarantee (`ai-collaboration-model.md §6`): the Decision Journal records *why*, CI records *pass/fail*, but the *review verdict* evaporated with the chat.
- **Options:** (A) PR comment via `gh api`; (B) a GitHub *review* (approve/request-changes); (C) append to the Spec's `REPORT.md`; (D) Decision Journal per PR.
- **Decision & rationale:** **A** — `/review-pr` posts its checklist + verdict as a **PR comment**, explicitly labelled **recommendation, not approval** (the human still authorizes the merge). **B was rejected on principle:** the gate must *never* cast a GitHub approve/request-changes review — that would usurp the human gate the whole model is built to protect; the record is a *comment*, never a review verdict. C is a nice complement for Spec PRs; D is overkill per-PR. The comment lives on the artifact, timestamped, visible on GitHub without a checkout — exactly where an auditor looks.
- **Guardrail preserved:** comment-only (`issues/<n>/comments`), never `pulls/<n>/reviews`. The gate still STOPs; the human still merges.
- **Outcome:** `review-record` Spec (`/spec-run`-ready; its R4 updates `§6` + CHANGELOG at build time); PR #54's verdict posted manually as the first instance.

### Related — the "Kiro Web" wording drift (lockstep follow-up)
- The same PR #54 run exposed that the IDE Executor emitted "run `/review-pr` on **Kiro Web**" — stale wording the surface-model refresh (Entry 017) missed in the lifecycle skills. Fixed via PR #55 (`spec-run`, `verification-done`, `plan-start`, `sprint-start` → "KiroCrew Operator"); routed through a `feat/` branch + PR because `.kiro/skills/` are project files, not governance/docs fast-path.

### Session meta
- **Pattern worth naming:** this is the second process gap the human caught by *watching the model run* (after the "Kiro Web" wording). Both were fed straight back through the model as Specs/PRs — the system improving itself via its own lifecycle. The human's live attention remains the sharpest gap-detector; automate the record, keep the human watching.

---

## Entry 020 — Multi-executor §7 trial, Phase 1: Antigravity passes the Executor contract (RFC-014 OQ-1 resolved)

**Date:** 2026-10-02 · **Contributor(s):** Agni Eialarasu (human-directed — ran the clone/onboard + the Antigravity validation), AI-assisted (authored the validation prompt, audited the result) · **Mode:** KiroCrew Operator · **Outcome:** `RFC-LAB-000-014` §7 Phase 1 complete; Open Question #1 resolved *yes*; `.kiro/steering/tech.md` stale-nvm line corrected

> _`RFC-LAB-000-014` accepted the multi-executor model but held Antigravity-as-live-executor **pending the §7 trial**. This entry records Phase 1 (contract validation), the first of the trial's three phases (validate → run one real Spec → record)._

### D65 — Antigravity honors the full Executor contract (RFC-014 §3) — adoption gate passed
- **Trigger:** `RFC-LAB-000-014` §7 requires proving a candidate executor can honor the §3 contract before trusting it with a real build. The human cloned `cetana-labs-antigravity/` + onboarded Antigravity (Phase 1 setup); the Operator authored a **read-only validation prompt** (deliberately not a build — no branch, no push, no PR) covering all six §3 obligations.
- **Result (audited against §3, not rubber-stamped):** ✅ reads a Kiro Spec as its brief (correctly summarized `review-record` goal/tasks/REPORT); ✅ reads `.kiro/` steering + specs with no Kiro-native loader; ✅ states both branch-discipline rules (path-scoped PR vs fast-path; the absolute no-force-push-`main` floor); ✅ `gh` authed as `agni-eialarasu` with `repo` scope, REST reachable (the PR path); ✅ enumerated the 6 REPORT.md sections; ✅ honored STOP-and-hold (did not branch/push/open anything on a validation task).
- **Decision & rationale:** **Antigravity is adopted as a candidate Executor** — Phase 1 passes. This **resolves RFC-014 Open Question #1** (*can it read `.kiro/` + the Spec as its brief without a Kiro-native loader?*) → **yes**. It does **not** yet promote cost-first routing to standing practice — that waits on Phase 2 (one real Spec end-to-end, measuring credits + fit) and Phase 3 (record). The gate is unchanged: every PR from Antigravity still goes through `/review-pr` + the human merge gate. _(Contributor: Agni Eialarasu)_
- **Outcome:** `RFC-LAB-000-014` §7 Phase 1 complete; Phase 2 candidate = `BK-024` in-app docs Spec (authored by the Operator, merge-first, then built on Antigravity as the first real trial build).

### Related — the validation surfaced a real doc defect: the stale `tech.md` nvm note
- Antigravity reported Node/pnpm on bare Homebrew PATH with **nvm absent** — which contradicted `.kiro/steering/tech.md` ("provided via nvm (`$HOME/.nvm`)… source `nvm.sh`"). The Operator initially flagged Antigravity's version numbers (Node 26, Python 3.14) as implausibly ahead — a **wrong call, anchored to the training cutoff rather than the current date**. Ground-truthing against the live machine (`node -v` → v26.10.0, no `~/.nvm`, Homebrew-managed) and `~/my-works/WORK_MACHINE_GUIDE.md` §4 confirmed Antigravity was **correct**: nvm/Volta were removed 2026-09-30 in a Homebrew consolidation. The steering line was false since then and would mislead every executor's preflight.
- **Fix:** corrected the `tech.md` toolchain note to the Homebrew reality (docs fast-path). A good first-contact outcome — the trial's whole point is measuring fit, and it immediately caught a stale-config defect that `/spec-run`'s own preflight would also have tripped on.

### Session meta
- **Division of labor:** human owned the clone + onboarding + ran the Antigravity validation (the surface the Operator can't reach); Operator authored the contract-check prompt and audited the evidence against §3.
- **Honest note:** Phase 1 proves the *contract*, not the *economics* — credits-saved and capability-fit are Phase 2's measurement. The Operator's version-anomaly suspicion was wrong and is recorded as such (verify against the current date + the machine, not the training cutoff). Governance/docs fast-path to `main` per `RFC-LAB-000-004`.

---

## Entry 021 — Multi-executor §7 trial COMPLETE: Antigravity shipped a real feature; cost-first routing promoted to standing practice

**Date:** 2026-10-02 · **Contributor(s):** Agni Eialarasu (human-directed — ran the Antigravity build + the human verification + every merge), AI-assisted (authored the Spec + trial prompts, gated the PRs, recorded) · **Mode:** KiroCrew Operator · **Outcome:** `RFC-LAB-000-014` §7 trial complete; cost-first routing (default Antigravity, escalate Kiro IDE) is standing practice; `BK-024` shipped (PR #58 / `TSK-065`)

> _Completes Entry 020 (Phase 1 — contract validation). This records Phase 2 (one real Spec end-to-end on Antigravity) and Phase 3 (the measured findings + the standing-practice decision)._

### D66 — Antigravity passed the §7 trial on a real build; cost-first routing is now standing practice
- **Trigger:** `RFC-LAB-000-014` §7 required running **one real Spec end-to-end on Antigravity** — measuring credits, wall-clock, review iterations, and contract adherence — before promoting cost-first routing from accepted-model to standing practice.
- **The trial:** `BK-024` (in-app docs view) — a routine, consumer-facing frontend feature, the archetypal "default → Antigravity (free)" build class (`RFC-LAB-000-014` §4). Spec authored on the Operator (Entry 020), merged merge-first (PR #57), built by **Antigravity** on `feat/bk024-in-app-docs`, PR [#58](https://github.com/agni-eialarasu/cetana-labs/pull/58), human-verified (PASS), gated via `/review-pr`, human-merged (`9936ec5`).
- **Measured results:**
  - **Contract adherence — full.** Read the Kiro Spec as its brief; built on a `feat/` branch; wrote `REPORT.md` with the EARS DoD walk + Verification Log; opened the PR via `gh api`; STOP-and-held (never merged, never self-approved); on the rebase used `--force-with-lease` on the feature branch and never touched `main`. Every §3 obligation honored on a *real* build, not just the Phase-1 read-test.
  - **Cost — zero credits** (Antigravity AI Pro, bundled free) vs. Kiro IDE's firm-budgeted Pro+ credits. The core RFC-014 thesis — route routine builds to the free executor — is validated in practice.
  - **Speed/quality — ~28 min start→PR, 2 trivial fixups to green** (a `marked` type import; a Prettier format). Clean `pnpm check`/`build`; 5/5 governance pillars green.
  - **Anticipated risk handled correctly.** The Spec's design (§1.1) flagged the `BK-023` cross-root-globbing risk (reaching the repo `docs/` from `app/web/` under Vite `fs.allow` / Vercel's build context). Antigravity resolved it exactly as anticipated — registered `server.fs.allow: ['../..']` in `vite.config.ts` — and additionally added a `prebuild` `check-docs.js` for deterministic fail-loud, a sound call for the static-adapter SPA.
- **Decision & rationale:** **Antigravity is promoted from candidate to a standing Executor; cost-first routing is now standing practice** — routine/mechanical/docs-and-skills/low-risk builds default to Antigravity (free); complex/high-stakes/deep-codebase/Kiro-native-dependent builds escalate to Kiro IDE with a one-line reason (`RFC-LAB-000-014` §4). The trial confirmed both halves of the thesis: the saving is real (zero credits) **and** the fit is real (full contract adherence + shippable quality on the first real feature). The gate is unchanged — every PR from either executor still goes through `/review-pr` + the human merge gate; more executors = more throughput, never more merge authority. _(Contributor: Agni Eialarasu)_
- **Outcome:** `RFC-LAB-000-014` §7 satisfied; cost-first routing standing; `BK-024` live; `TSK-065` recorded. The standing lesson + the Working Model artifact (Executor lane showing both executors + the cost-first default) are the lockstep follow-ups.

### Related — Operator coordination lesson: don't merge into `main` while an executor is mid-build
- **What happened:** while Antigravity was building `BK-024`, the Operator merged an unrelated PR #59 (the Vercel `ignoreCommand` skip) into `main`. Both PRs added `[Unreleased]` CHANGELOG entries, so #58 came back from the build **conflicted** (`mergeable: dirty`) and the `/review-pr` gate correctly HELD on it. Antigravity rebased cleanly (kept both entries) and the gate flipped to READY.
- **Lesson:** the clone-per-executor isolation (Entry 018 / D63) prevents *worktree* races, but not *`main`-moved-under-you* rebases. With multiple executors in flight, the Operator should **batch or sequence `main` merges** around an active build, or expect (cheap, mechanical) rebases. Recorded as a coordination refinement, not a model flaw — the gate did its job (caught the conflict; nothing bad reached `main`).

### Related — a doc defect the trial surfaced (completes the Entry 020 thread)
- The Phase-1 validation already caught + fixed the stale `tech.md` nvm note (Entry 020). No new doc defects surfaced in Phase 2.

### Session meta
- **Division of labor:** human ran the Antigravity build, the human functional verification (incl. the V7 theme toggle Antigravity left for human eyes), and every merge; the Operator authored the Spec + the (now reusable) Antigravity trial/validation/re-sync prompts, gated all three PRs (#57 docs, #59 Vercel-skip, #58 the trial build — HOLD-on-conflict then READY), and recorded. The whole arc stayed inside the Operator/Executor model with the human gate intact throughout.
- **Honest note:** this is a single-feature trial — strong evidence, not a large sample. Cost-first routing is promoted on the strength of a *clean* first run; if a later complex build on Antigravity shows capability or rework cost that erodes the saving, the routing is revisited on that evidence (the escalation lane to Kiro IDE exists precisely for that). The gate's invariance means a weaker build simply HOLDs — cost routing never relaxes the merge bar.

---

## Entry 022 — The `is_admin` tier: in-app administration unblocked (Option C), RFC-008 Amendment A1

> _Brainstorm decision (Operator session, 2026-10-08). Resolves the gate three queued UI features waited on: a write path for someone who is not a PocketBase superuser._

### D67 — Add ONE `is_admin` boolean tier (not the deferred 5-role model) to unblock in-app admin

- **The question:** three brainstorm items (Projects/Developers CRUD UI, App Settings UI, partly RGS Stage B UI) need in-app writes that today's RBAC forbids — `projects` create/delete is `null`, `settings` write is superuser-only. "Is the admin role in scope?"
- **Options weighed:** (A) full admin role / resurrect the 5-role `memberships` model — rejected as over-build; (B) defer admin, keep PocketBase admin-UI as the escape hatch — rejected because "settings/CRUD UI" without a write path are just read views (half-features); (C) **one `is_admin` boolean** — the minimum surface that unblocks all three.
- **Decision: Option C.** Add a single application-level `is_admin` flag on `users` (distinct from the PocketBase **superuser**, which keeps schema power, and from the deferred `role` select). Admin can create/edit/delete any project, write `settings`, and manage users. The 5-role `memberships` model stays **deferred** — nothing listed needs it.
- **Recorded as:** `RFC-LAB-000-008` **Amendment A1** (Accepted) — carries the exact rule matrix (`RULE_ADMIN = @request.auth.id != "" && @request.auth.is_admin = true`), guardrails (no self-escalation; superuser stays bootstrap/escape-hatch; audit still deferred), and the downstream Spec sequence.
- **Supersedes:** the §4 "create/delete of projects in-app = deferred" line — now permitted **for admins only**. All other §4 deferrals stand.

### Downstream (Specs that cite A1, in dependency order)
1. **A1 implementation** (auth-only, no UI): add `is_admin`, update the two rule-source scripts + regenerate `pb_schema.json`, seed the first admin, rule tests. Sprint deliverable → full gate.
2. **App Settings UI** (`BK-012` UI half) — smallest, one collection.
3. **Projects/Developers CRUD UI** (`BK-014`, now unblocked) — manage projects + users.
4. RGS Stage B UI — consumes the admin tier; its larger blocker is the server-runtime spike (separate).

### Session meta
- **Class:** governance/architecture decision → RFC amendment + Decision Journal (doc fast-path / merge-first). The *implementation* of A1 is a separate sprint-deliverable Spec through the full gate.
- **Division of labor:** Operator grounded current RBAC in the live schema (`generate_pb_schema.py` rules, `pb_schema.json`), framed the three options honestly, recommended C, authored the amendment on the user's decision. Human holds every merge.

---

## Entry 023 — README master registry: KEEP as a reconciled snapshot (post-BK-014)

> _Brainstorm decision (Operator session, 2026-10-08), prompted by: "do we keep the project registry + archetypes in the README now that the app has CRUD?"_

### D68 — Keep the README registry + archetypes; reframe it as a reconciled snapshot, not the source of truth

- **Context:** today `BK-014` landed in-app Projects/Developers CRUD + `scripts/export_pb_to_data.py` reconciliation. That made the question timely: with a live app registry, does the generated README registry still belong?
- **Decision: KEEP it** (both the generated registry block and the static archetype list), but **reframe its role**. It is a **committed, at-a-glance, reconciled snapshot** of the portfolio on GitHub — zero-maintenance (generated from `data/`), and where the architect/leads look today. It is explicitly **NOT the live source of truth**: the live portfolio is the deployed app (PocketBase); admins edit there and run `just export-live-data` to reconcile back into `data/*.json`, which regenerates the README block through the normal gate.
- **Why not drop it:** it costs nothing (generated), GitHub remains the common read surface, and a brief DB↔README divergence between an edit and a reconciliation is expected and surfaced (the app's divergence banner, R7.2).
- **Why not make it the source of truth:** the app now is — the README mirrors it. Keeping both honest is exactly what the BK-014 reconciliation + divergence banner provide.
- **Archetypes:** kept — reference material (what the icons mean), not state; no maintenance cost.
- **Recorded in:** a note above the registry block in `README.md` (survives regeneration — it's outside the `BEGIN/END:registry` markers).

### Session meta
- **Class:** governance/doc decision → doc fast-path (README prose above the generated block; `generate_registry --check` stays green). Closes the loop on today's BK-014 reconciliation.
- First of the three "lighter" brainstorm items; the other two (RGS user guide, RGS doc audit) remain open — the audit's intake-ledger question is the next real decision.

---

## Entry 024 — Adopt a Cetana intake ledger (RGS gets a home); seed of the Stage-D org hub

> _RGS doc audit (Operator session, 2026-10-08). Finding: `/rgs` is a producer without a consumer here — it emits `INTAKE-NNN` drafts byte-compatible with `docs/REQUIREMENTS_INTAKE.md`, but Cetana had no such ledger._

### D69 — Create a minimal Cetana `docs/governance/REQUIREMENTS_INTAKE.md`; Cetana-only scope now, documented as the Stage-D org-hub seed

- **Audit finding:** `/rgs` (Stage C, live) shapes fuzzy asks into `INTAKE-NNN` drafts + a channel-relay message, grounded byte-for-byte in the Nexus Pulse intake shape. But **Cetana had no `REQUIREMENTS_INTAKE.md`** — so the drafts and their state machine (`NEW → AWAITING-SOURCE → CLARIFIED → SPECCED → DELIVERED`) had nowhere to land. The skill itself anticipated this ("if no ledger exists yet, e.g. Cetana Labs today, emit INTAKE-001 and note the ledger must be created on first adoption").
- **Options weighed:** (A) adopt a Cetana ledger now; (B) document RGS as draft-only, relay elsewhere, no ledger; (C) defer entirely to the Stage-D org hub.
- **Decision: Option A, scoped minimally — Cetana-only now, explicitly framed as the seed of the Stage-D org hub.** Created `docs/governance/REQUIREMENTS_INTAKE.md` (empty register + state legend). Rationale: (1) Cetana IS the master control plane, so the org-wide intake view belongs here long-term (matches the standing "org-hub over per-repo duplication" lean) — Option B under-uses that role; (2) building the full Stage-D hub now is over-build — Option C leaves RGS homeless meanwhile; (3) Option A as a *seed* threads it: RGS drafts land today, the AIDLC funnel works, and the doc records that org-wide intake is the Stage-D evolution (pairs with the convergence-ledger candidate). No throwaway.
- **The one real fork (recorded):** Cetana-own requirements vs org-wide inbound. Chose **Cetana-only now**, with the ledger's scope note stating org-wide is the Stage-D direction — so the hub isn't prematurely built but the path is documented.
- **Guardrail unchanged:** RGS still never writes this file; the Operator reviews + commits each entry by hand (governance/docs fast-path).

### Downstream
- Unblocks the **RGS minimal user guide** (brainstorm item #1) — it can now say "your `/rgs` draft lands in `docs/governance/REQUIREMENTS_INTAKE.md`."
- The RGS skill's "no ledger yet (e.g. Cetana Labs today)" note is updated to point at the now-existing ledger.

### Session meta
- **Class:** governance/doc decision + a new (empty) governance doc → doc fast-path. Second of the three lighter brainstorm items (after D68 README); the RGS user guide (#1) is the last.

---

## Entry 025 — GitHub-handle identity + PocketBase as source of truth (RFC-016); retire the dual-source model

> _Triggered by a live-app screenshot: signing in as `@agni-eialarasu` produced TWO `users` rows for one human — the OAuth-minted record (Unlinked, owns nothing) and the seeded `usr-eialarasu` (owns LAB-000..003). The dual-source model (committed `data/` masters AND live PocketBase, reconciled by a fragile handle match) made visible._

### D70 — Decide identity (GitHub handle = single key) now; frame + phase the registry retirement

- **Root cause (verified in `auth.svelte.ts`):** PocketBase mints a separate auth record per GitHub identity; the frontend links to a seeded owner by `github_handle`, and a misfire leaves the user authenticated-but-unlinked — two identities, one human. Ownership lives on the seeded row, auth on the OAuth row.
- **Two decisions deliberately separated** (so the urgent fix isn't held hostage to the bigger one):
  - **Decision 1 (DECIDED):** `github_handle` is the unique, authoritative user key — ONE record per GitHub identity; sign-in **upserts by handle** (binds to the seeded row, never creates a second); a one-off migration merges the existing `o43801zyav6cwmd` → `usr-eialarasu`.
  - **Decision 2 (FRAMED, gated):** retire hand-authored `data/` masters + the README registry block + the local `project-*` skillset; PocketBase becomes source of truth; `data/` likely survives as a committed **export** (OQ-2 lean). Deletions gated behind OQ-1..OQ-4.
- **Key correction captured in the RFC:** the daily WhatsApp scraper reads **`STATUS.md`**, not `data/status.json` — so retiring `data/` masters does **not** break the executive broadcast. That materially shrinks Decision 2's blast radius.
- **Phasing:** Phase 1 = identity Spec (fixes the bug, no registry change); Phase 2 = answer OQ-1..OQ-4; Phase 3 = registry inversion Spec(s), keeping `data/` as export.
- **Class:** architecture decision (RFC + journal) → doc merge-first. Implementation Phases are sprint deliverables → full gate; the Phase-1 data migration touches live records (scripted, verified, reversible by reseed).

---

## Entry 026 — Registry-retirement design: answer RFC-016 OQ-1..OQ-4 (Phase 2)

> _Phase 2 of RFC-016. Before any master or skill is deleted, answer the four gating open questions the RFC left open. Grounded in the live code: the app's CRUD owns project **metadata** only; the executive broadcast reads `STATUS.md`, not `data/`._

### D71 — Answer the OQs; retire 2 skills, keep `data/` as export, invert the data flow in Phase 3

- **Decisive finding (verified in code):** the web app's BK-014 CRUD (`admin/projects`, `admin/developers`) owns project **metadata** (`portfolio.json`/`users.json` fields) — it does **not** own `STATUS.md`, `journal.md`, or the WhatsApp broadcast (`generate_status.py` reads `STATUS.md` exclusively: 11 refs, 0 to `data/`). So the registry retirement is a metadata-source-of-truth change, not a status-reporting change.
- **OQ-3 (per-skill call) — retire 2 of 7:** RETIRE `project-add` + `project-edit` (the pure metadata lifecycle the app now owns). KEEP `project-update`, `project-status`, `project-validate`, `audit-doc`, `audit-project` (they operate on the executive/governance layer the app deliberately doesn't touch). KEEP `projects/LAB-XXX/` dirs (existing STATUS/journal still managed by the kept skills; Phase 3 stops *creating new* disk dirs, doesn't delete existing). KEEP `templates/` for now — re-evaluate as a Phase-3 follow-up, not a Phase-3 deletion.
- **OQ-1 — re-point, don't retire:** the "registry lockstep" CI pillar flips its assertion from *README matches hand-authored `data/`* to *committed `data/` export matches live PB*. Still a real gate; guards export freshness. Keeps the at-rest GitHub registry view D68 reframed.
- **OQ-2 — keep `data/` as a generated export** (confirms the RFC lean): `just export-live-data` already writes it; the app's `data.ts` fallback depends on it; GitHub keeps rendering the portfolio. Flip its role master → generated artifact (add to the "never hand-edit" list in `structure.md`).
- **OQ-4 — already satisfied by BK-034 (#89):** handle-unique index + atomic owner-re-point-before-delete migration shipped.
- **The one consequential change Phase 3 (BK-036) owns — the data-flow inversion:** today `data/ ──seed──▶ PB`; Phase 3 flips it to `PB ──export──▶ data/`. Implies: new projects created in-app (not disk-scaffolded); `just export-live-data` becomes the lockstep step (not `generate_registry` from masters); the registry pillars assert export-matches-PB; the 2 retired skills removed with AGENTS.md §3/§4 + referencing docs updated in-lockstep.

### Downstream
- **Unblocks BK-036 (Phase 3)** — its registry-inversion Spec cites `docs/governance/registry-retirement-design.md` for the OQ answers.
- The status-reporting spine (`STATUS.md`, `journal.md`, `project-status`, `project-update`) is explicitly out of scope — a key de-risking.

### Session meta
- **Class:** governance/design decision + a new governance doc → doc fast-path (merge-first, so the Phase-3 Spec can cite it). No code change.
---

> 🧭 **Navigation:** [⬆️ Top](#) · [🏠 Repo](../../README.md) · [📚 Docs Hub](../README.md)
