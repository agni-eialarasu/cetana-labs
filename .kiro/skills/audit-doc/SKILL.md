---
name: audit-doc
description: >-
  Audits a single documentation file for accuracy, staleness, broken links, and convention conformance (portability, no absolute paths, correct cross-references). Use when the user runs /audit-doc <file> or asks to review/check a specific doc.
---

# Skill: Document Audit (`/audit-doc`)

## Objective
Review **one** documentation file for correctness and hygiene, and report actionable findings (optionally fixing them). Complements `/audit-project` (whole-project sweep).

## Trigger Patterns
- `/audit-doc <path>` (e.g. `/audit-doc README.md`, `/audit-doc docs/rfc/RFC-LAB-000-003-pocketbase-web-app.md`)
- "audit / review this doc", "check <file> for staleness"

## Steps

For the target file (trailing text = path; if omitted, ask which file):

### 1. Accuracy & staleness
- Cross-check claims against the current repo: referenced files/scripts exist; commands are current; version/counts/dates match reality (e.g. sprint ids, `LAB-XXX` ids, task ids).
- Flag statements contradicted by the codebase or superseded by a later RFC/decision.

### 2. Links & references
- Verify internal links resolve (relative paths exist); RFC/backlog/task cross-refs (`RFC-LAB-000-0XX`, `TSK-0XX`, `BK-0XX`) point to real entries.
- Flag external URLs that look stale (best-effort; note if unverifiable).

### 3. Convention conformance
- **Portability (AGENTS.md §1.2):** no machine-specific absolute paths (`/Users/...`, `C:\...`).
- Correct semantic/heading structure for the doc type (e.g. STATUS.md 5-section ≤35-line protocol; RFC metadata table present).
- Terminology consistent with `docs/DESIGN.md` and steering (e.g. blue accent not purple; IBM Plex).

### 4. Report
- Emit findings as a checklist: ✅ ok / ⚠️ warn / ❌ fix-needed, each with file:line and a concrete suggestion.
- If asked to fix, apply edits and re-audit; keep changes minimal and within convention.

## Notes
- Read-only by default; only edit when the user asks.
- For `STATUS.md`, defer hard structural checks to `project_validate.py` and summarize its result.
