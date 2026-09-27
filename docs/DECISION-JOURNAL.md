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
