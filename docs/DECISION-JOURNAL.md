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

**Date:** 2026-09-24 · **Mode:** Kiro Web (brainstorm & planning) · **Outcome:** RFC-LAB-000-001 → -008, 11 PRs, releases v0.5.0 → v0.9.0

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
