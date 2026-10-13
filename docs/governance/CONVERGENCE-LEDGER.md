<a id="top"></a>
[🏠 Cetana Labs](../../README.md) / [📚 Docs](../README.md) / Governance / **Convergence Ledger**

# Cross-Repo Convergence Ledger — Agni

> The single pane for **standards that converge across Agni repos** (Cetana Labs ↔ Nexus Pulse, and future org repos). Cetana Labs is the org's master engineering control plane, so the cross-repo adoption view belongs here (pairs with the Stage-D org-hub evolution of [`REQUIREMENTS_INTAKE.md`](REQUIREMENTS_INTAKE.md)).
>
> **The boundary rule (how adoption works — not optional):** a standard is **never bulk-applied** or auto-crossed from one repo into another. The originating repo prepares a **self-contained kickoff brief**; the **receiving repo's own chat/session** runs it under **its own AIDLC lifecycle** (branch → validate → human merge, one reviewable PR per theme) and records it in **its own Decision Journal**. This ledger only **tracks** that convergence — it is a dashboard, not an actuator. (Convention: the `cross_repo_handoff_structure` decision; `AGENTS.md` §1.)

## Status legend

| Status | Meaning |
| :--- | :--- |
| `🎯 Proposed` | Adoption brief drafted; not yet run in the receiving repo. |
| `🔨 In Adoption` | Receiving repo's lifecycle is running the brief (branch/PR open). |
| `✅ Converged` | Live + merged in **both** repos. The standard is shared. |
| `↩️ Reverse-adopt` | A pattern the *other* repo does better that we want to pull back. |
| `⏸️ Diverged (intentional)` | Deliberately **not** converged — repos differ for a documented reason. |

---

## Converged standards

| # | Standard | Origin → Target | Cetana (`LAB-000`) | Nexus Pulse (`LAB-003`) | Status | Record |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| C-1 | **Shared `/command` vocabulary** — one committed `.kiro/skills/<name>/SKILL.md` becomes a live `/command` across all four surfaces (the "skill-hook"); identical command names across repos | Cetana → NP | ✅ | ✅ | `✅ Converged` | Cetana Entry 028 / D73 (skill-hook stated in `AGENTS.md` §4); NP adopted the convention |
| C-2 | **`just` task runner** — a shared 7-recipe core (`start-local`, `stop-local`, `status-local`, `validate-local`, `validate-staging`, `clean-data`, `help`) with **identical recipe names** in every repo; `Makefile` kept one sprint as a forwarding shim | NP → Cetana | ✅ (`BK-025`, PR #63) | ✅ | `✅ Converged` | Cetana SPRINT-11 `TSK-066`; Director decision — one command vocabulary across Agni repos (`pref.task_runner_just`) |

---

## In-flight adoptions (Cetana → Nexus Pulse)

> The current upgrade pass: patterns Cetana has matured that Nexus Pulse should adopt. Each runs under **NP's own lifecycle** from the kickoff brief; this table tracks state only.

| # | Pattern | Direction | Brief | Status | NP record |
| :---: | :--- | :--- | :--- | :---: | :--- |
| A-1 | **Uniform docs navigation standard** — breadcrumb at top + `🧭 Navigation` footer on every `docs/**` file (jump back without scrolling) | Cetana → NP | Entry 028 brief, Part A | `🎯 Proposed` | _pending NP PR_ |
| A-2 | **Purpose-scoped guide split** — break a monolithic dev-guide into focused guides (AIDLC · Release · local-setup), one source per concept, no duplication | Cetana → NP | Entry 028 brief, Part A | `🎯 Proposed` | _pending NP PR_ |
| A-3 | **Two-work-classes routing table** — ceremony scales to a change's *purpose* (sprint deliverable → full gate · governance tooling → simplified path), not its file path | Cetana ↔ NP (codified NP-side first) | `pref.two_work_classes_process` (NP Entry 005/D7) | `✅ Converged` | NP `main` `e09a465` — already live NP-side; Cetana adopted into `AGENTS.md` §1 |
| A-4 | **Agent entry map (`llms.txt`)** — repo-root curated start-here map (llmstxt.org format), framed as a convenience mirror, not a source of truth | Cetana → NP | Entry 028 / D73 | `🎯 Proposed` | _pending NP PR_ |

## Corrections noticed in Nexus Pulse (verify before acting)

> Observations from the comparison pass. **Flagged, not fixed** — each is NP's own call under NP's lifecycle.

| # | Observation (in NP) | Suggested action | Status |
| :---: | :--- | :--- | :---: |
| X-1 | Committed `.DS_Store` artifacts | Add `**/.DS_Store` to `.gitignore`, untrack | `🎯 Proposed` |
| X-2 | Early-sprint archive entries carried in the live tracker | Move delivered sprints to the archive section | `🎯 Proposed` |
| X-3 | Badge/metric honesty — cosmetic hand-typed metrics that can drift | Prefer state alone over an invented number (`pref.status_board_metric_honesty`) | `🎯 Proposed` |

## Reverse-adoptions (NP → Cetana — pull back what NP does better)

| # | Pattern | Why Cetana wants it | Status |
| :---: | :--- | :--- | :---: |
| R-1 | NP's sharper **in-doc TOC + local-environment matrix** in the developer guide | Scattered local-env facts in Cetana's dev-guide | `✅ Converged` (Cetana Entry 028 / D73 adopted it) |

---

## How to use this ledger
1. **When a standard converges in both repos** → add a `✅ Converged` row to the top table with both Decision Journal records.
2. **When Cetana prepares a brief for NP (or any repo)** → add an `🎯 Proposed` row to the in-flight table; link the brief.
3. **When the receiving repo merges it** → flip to `✅ Converged`, link the receiving PR + its Decision Journal entry.
4. **Never** edit the other repo from here. This ledger is a read-model of convergence; the write path is always the receiving repo's own gated lifecycle.

---

> 🧭 **Navigation:** [⬆️ Top](#top) · [🏠 Repo](../../README.md) · [📚 Docs Hub](../README.md) · 🔗 Related: [`REQUIREMENTS_INTAKE.md`](REQUIREMENTS_INTAKE.md) · [`ai-collaboration-model.md`](ai-collaboration-model.md) · [`DECISION-JOURNAL.md`](DECISION-JOURNAL.md)
