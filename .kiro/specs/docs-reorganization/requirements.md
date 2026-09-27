# Docs Reorganization — Requirements

| Property | Value |
| :--- | :--- |
| **Spec ID** | `docs-reorganization` |
| **Feature** | Standardize `docs/` into a logically-grouped, navigable doc system with a documented nav standard — blueprint-grade (copyable by other repos) |
| **Backlog** | `TSK-052` (SPRINT-09) |
| **Status** | 🟡 Proposed (contract authored on Kiro Web; execution on Kiro IDE) |
| **RFCs / Refs** | `RFC-LAB-000-004` (docs may fast-path; here run as a Spec for verification), `AGENTS.md` (references), README |
| **Executor role** | Delegated-agent / onboarded-dev (full Spec) |

---

## 1. Introduction

The `docs/` folder is a **flat dump** of 13 files mixing four different doc kinds, navigation is **one-way** (README → docs, but docs rarely link back or to siblings), three docs are **orphaned** from the README front-door, and the README's "Repository Structure" block is **stale**. Because `LAB-000` is the **AIDLC blueprint** other repos copy, its doc system must be **standardized, logically grouped, and smoothly navigable**.

This Spec delivers: a folder taxonomy, a `docs/README.md` index (docs hub), a **breadcrumb navigation standard** every doc follows, a rename (`work-environment` → `developer-guide`), and a refreshed README structure tree.

**Explicitly excluded:** `docs/index.html` (the generated GitHub-Pages dashboard) is **left untouched** — its retirement belongs to the deployment work (`RFC-LAB-000-011`, Vercel/GCP cutover), not to doc reorganization.

## 0. Preconditions (preflight — verify BEFORE any change; enforced by `tasks.md` T0)

- **P1 — Surface:** Kiro **IDE / local** (file moves + link-resolution checks). `/env-doctor` IDE-ready.
- **P2 — Toolchain:** git (for `git mv`), Python 3.11+ (validators), a grep tool.
- **P3 — Branch:** feature branch `feat/docs-reorganization` off up-to-date `main`; clean tree; not `main`/`master`.
- **P4 — Merge-first:** this Spec is merged to `main` before `/spec-run`.
- **P5 — Baseline green:** `validate_portfolio.py`, `generate_status_json.py --check`, `project_validate.py --allow-dirty` all pass before changes.
- **P6 — Link inventory:** capture the current set of intra-repo links to `docs/*` (README + AGENTS.md + docs + RFCs) as the baseline for the no-broken-links check (R6).

## 2. Current-state facts (of record — verified against the repo)

- **`docs/` (flat, 13 entries):** `rfc/` (grouped ✅), `templates/` (grouped ✅), `index.html` (build artifact), and 10 loose `.md`: `user-guide`, `work-environment`, `sprint-lifecycle`, `project-owner-guide`, `cloud-dev-guide` (guides); `project-protocol`, `DESIGN`, `design-system-lab000` (reference); `DECISION-JOURNAL`, `ai-collaboration-model` (governance).
- **Navigation:** README has a good doc-links header; but of the 10 loose docs only `sprint-lifecycle` (4) and `project-protocol` (1) link back/sideways — 8 are dead-ends.
- **Orphaned from README front-door:** `DESIGN.md`, `design-system-lab000.md`, `cloud-dev-guide.md`.
- **Stale README tree:** the "Repository Structure" block omits recent docs (`sprint-lifecycle`, `DECISION-JOURNAL`, `ai-collaboration-model`, `DESIGN`, `rfc/`, `templates/`) and recent skills (`/spec-run`, `/plan-start`, `/plan-done`, `/review-pr`, `/verification-done`, `/sprint-start`, `env-doctor`, `validate-local`, etc.).
- **Referrers to update on rename/move:** README, `AGENTS.md`, `docs/rfc/RFC-LAB-000-007-*` (names `work-environment.md` as a deliverable), `templates/*/README.md`, `journal.md`. (Journal is a historical record — see R5.2.)

## 3. Requirements (EARS acceptance criteria = Definition of Done)

### R1 — Folder taxonomy
- **R1.1** The system SHALL group `docs/` into: `docs/guides/`, `docs/reference/`, `docs/governance/`, keeping `docs/rfc/` and `docs/templates/` as-is.
- **R1.2** Files SHALL be moved via `git mv` (history preserved) as: **guides/** ← `user-guide`, `developer-guide` (renamed from `work-environment`), `sprint-lifecycle`, `project-owner-guide`, `cloud-dev-guide`; **reference/** ← `project-protocol`, `DESIGN`, `design-system-lab000`; **governance/** ← `DECISION-JOURNAL`, `ai-collaboration-model`.
- **R1.3** `docs/index.html` SHALL NOT be moved or deleted (excluded — deployment concern).

### R2 — Rename `work-environment.md` → `developer-guide.md`
- **R2.1** The file SHALL be renamed via `git mv` to `docs/guides/developer-guide.md`.
- **R2.2** Its header SHALL clearly scope it (*setup / commands / Web+IDE surfaces*) to distinguish it from `project-owner-guide.md` (*how leads write STATUS / prompts*).

### R3 — `docs/README.md` index (the docs hub)
- **R3.1** The system SHALL create `docs/README.md` — an index grouping every doc under its category with a one-line description and a working relative link.
- **R3.2** The index SHALL link back to the repo root `README.md`.

### R4 — Breadcrumb navigation standard
- **R4.1** The system SHALL define a **breadcrumb standard**: every `docs/**` markdown file opens with a nav line of the form `[🏠 Repo](../../README.md) / [📚 Docs](../README.md) / <Category> / **This Doc**` (depth-correct relative paths).
- **R4.2** The standard SHALL be **documented** in `docs/README.md` (the copyable convention) and referenced from `AGENTS.md` so future docs follow it.
- **R4.3** Every existing `docs/**/*.md` (excluding `rfc/*` and `templates/*`, and excluding `index.html`) SHALL carry a conforming breadcrumb. *(RFCs keep their existing header format; the index links to the RFC folder.)*

### R5 — Update all referrers
- **R5.1** `README.md` (doc-links header + the "Repository Structure" tree), `AGENTS.md`, `docs/rfc/RFC-LAB-000-007-*`, and `templates/*/README.md` SHALL be updated to the new paths/name, and the README tree refreshed to reflect the real current `docs/` + `.kiro/skills/` contents.
- **R5.2** Historical records (`journal.md`, prior `CHANGELOG`/RFC prose) SHALL NOT be rewritten; where they reference the old path, leave the historical text but ensure no *active* navigation link is broken. *(Judgment: a historical mention is fine; a live "see X" link should resolve.)*
- **R5.3** The 3 previously-orphaned docs (`DESIGN`, `design-system-lab000`, `cloud-dev-guide`) SHALL be discoverable from `docs/README.md`; `cloud-dev-guide.md` SHALL carry a staleness note if it is superseded by `developer-guide.md` (flag for human confirmation in verification).

### R6 — No broken intra-repo links (the core safety bar)
- **R6.1** WHEN the reorg is complete, every intra-repo markdown link to a `docs/*` path SHALL resolve (no dangling links introduced by the moves/rename).
- **R6.2** A link-check SHALL be run (script or grep-based) comparing against the P6 baseline; any break is fixed before hand-off.

### R7 — Quality gates green
- **R7.1** `validate_portfolio.py`, `generate_status_json.py --check`, and `project_validate.py --allow-dirty` SHALL pass. *(If any validator hard-codes a `docs/` path, update it.)*

## 4b. Human Verification Plan (emitted by `/spec-run`; recorded by `/verification-done`)

- **V1 — Grouping:** `docs/` shows `guides/ reference/ governance/ rfc/ templates/` (+ `index.html` untouched); each loose `.md` moved to the right category.
- **V2 — Index works:** `docs/README.md` lists every doc with a working link and links back to root README.
- **V3 — Breadcrumbs:** open 3–4 docs across categories — each has a correct, clickable breadcrumb back to Docs hub and Repo root.
- **V4 — Rename:** `work-environment.md` is gone; `developer-guide.md` exists with a scope-distinct header; README/AGENTS/RFC-007 point to the new name.
- **V5 — No broken links:** the link-check reports zero dangling `docs/*` links (spot-check the README doc-links header — every entry resolves).
- **V6 — README tree accurate:** the Repository-Structure block matches the real `docs/` + `.kiro/skills/` contents.
- **V7 — index.html untouched:** confirm `docs/index.html` and `deploy-pages.yml` are unchanged (excluded scope held).
- **V8 — Validators green.**

**Verdict rule:** V1–V8 pass (fixes on the same PR, re-verified) before `/verification-done`.

## 5. Out of Scope (deferred)
- Retiring `docs/index.html` / the GitHub-Pages classic dashboard → `RFC-LAB-000-011` (deployment, Vercel/GCP).
- Rewriting doc *content* (this is structure + navigation only; no prose rewrites beyond scope headers + breadcrumbs + staleness note).
- A `docs/` link-check CI pillar — candidate follow-up, not required here.

## 6. Open Questions (resolve at build start)
1. **`cloud-dev-guide.md` fate:** superseded by `developer-guide.md`? *(Leaning: keep, add a staleness/"see developer-guide" note; human confirms in V-review — don't delete content silently.)*
2. **Link-check mechanism:** a small throwaway grep/script vs. a committed helper. *(Leaning: throwaway during the run; a committed link-check is a separate follow-up.)*
