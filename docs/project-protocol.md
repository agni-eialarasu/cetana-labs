# Project Status Protocol — The `STATUS.md` Standard

> 👥 **For Project Leads & Developers:**  
> Read the step-by-step developer playbook with AI prompts: **[Project Owner Guide (docs/project-owner-guide.md)](project-owner-guide.md)**.

---

This document defines the mandatory **`STATUS.md`** protocol for all projects tracked under **Cetana Labs**.

---

## 1. Motivation & Purpose

To ensure leadership, management, and cross-functional stakeholders receive **instant, high-fidelity, executive-ready updates** without interrupting engineering flow:
- Every project must maintain a single, lightweight **`STATUS.md`** file at its root.
- The AI agent parses this file on demand via `/project-status` to generate **WhatsApp-compatible broadcasts** for management in seconds.
- Updating `STATUS.md` takes **under 2 minutes** at the close of a sprint or milestone using automated AI prompts.

---

## 2. File Location Rules

| Project Type | Where `STATUS.md` Resides |
| :--- | :--- |
| **External Mini-Apps / Services** (e.g. `nexus-pulse`, `ammas`, `zerobea.ai`) | In the root of the project's own Git repository (`<repo>/STATUS.md`), with a synced copy or reference in `cetana-labs/projects/<ID>/STATUS.md`. |
| **Internal Research Spikes / Benchmarks** (e.g. `wrenai-eval`) | Directly inside `cetana-labs/projects/<ID>/STATUS.md`. |

---

## 3. The Authoritative `STATUS.md` Schema

Every `STATUS.md` MUST adhere to this concise, 5-section markdown template (strictly capped at `<= 35 lines`):

```markdown
# Project Status & Executive Summary

| Property | Value |
| :--- | :--- |
| **Project ID** | LAB-XXX |
| **Project Name** | [Name] |
| **Current Health** | 🟢 On Track |
| **Owner / Lead** | [Name] |
| **Last Updated** | YYYY-MM-DD |

---

### 1. Elevator Pitch (Business Purpose)
A 2-sentence summary of what this project does and the business value it delivers in plain English (no internal jargon).

### 2. Latest Deliveries & Business Wins
- **[Win 1]**: What capability was unlocked and why it matters to the business.
- **[Win 2]**: Key stability, performance, or architectural milestone reached.

### 3. Current Focus & Next Milestone
- What the team is actively building right now and the target milestone.

### 4. Blockers & Risks
- **Blockers**: None (or specific blocker needing management escalation).
- **Key Risks**: (e.g. dependency on external API, hardware availability).

### 5. Verified Quality Metrics
- Automated tests passing (e.g. 126/126 passed).
- Key performance or architectural validation notes.
```

---

## 4. Health Badge Values

| Health | Badge | Meaning |
| :--- | :---: | :--- |
| **Onboarding Pending** | `⏳ Onboarding Pending` | Project registered in Cetana Labs, but awaiting initial `STATUS.md` baseline from project lead. |
| **On Track** | `🟢 On Track` | Milestones progressing as scheduled. |
| **At Risk** | `🟡 At Risk` | Minor delays or external dependencies pending; no escalation yet. |
| **Blocked** | `🔴 Blocked` | Hard blocker requiring management intervention. |
| **Paused** | `⏸️ Paused` | Intentionally on hold. |
| **Completed** | `✅ Completed` | Deliverables finished or successfully operationalized. |

---

## 5. Constructive Visibility & Cadence Enforcement ("Soft Pressure")

Cetana Labs encourages consistent, high-hygiene engineering practices through transparent management visibility:

1. **Onboarding Enforcement**:
   - Newly registered initiatives start in `⏳ Onboarding Pending`.
   - Routine delivery wins and metrics are suppressed in the executive report until the lead completes onboarding.
   - The morning executive briefing highlights:
     `• *Status Alert:* ⚠️ Initial onboarding protocol pending from project lead.`
     `• *Action Required:* Run /status-init in repo root to establish sprint baseline.`

2. **Sprint Cadence & Staleness Tracking**:
   - Every active project is expected to update `STATUS.md` at sprint closeout (typically every 14 days).
   - If `Last Updated` is older than **14 days**, the status engine automatically appends a subtle cadence flag:
     `• *Cadence Notice:* ℹ️ Last updated X days ago. Awaiting sprint closeout (/status-update).`
   - Completed initiatives are exempt from staleness tracking.

---

## 6. Automated Consumption via `/project-status`

When `/project-status [project_id]` is executed:
1. The AI agent locates the relevant `STATUS.md` file(s).
2. It extracts the Elevator Pitch, Latest Wins, Current Focus, Health, and Blockers.
3. It evaluates onboarding and cadence health.
4. It formats a crisp, emoji-rich, WhatsApp-friendly broadcast message ready to copy-paste.

---

## 7. The Pre-Flight Governance Gate (`/project-validate`)

To eliminate metric drift, hallucinated test numbers, and line-budget overflows, Cetana Labs enforces a **Two-Phase Governance Contract**:

```text
[ /project-validate ]  ──(If GREEN: emits validation_receipt.json)──>  [ /project-status ]
(Automated Pre-Flight Gate)                                            (Scraper Publish & Broadcast)
```

### The 5 Core Verification Pillars:
1. **Scraper Budget**: Root `STATUS.md` is strictly `<= 35 lines` with required metadata keys.
2. **Registry Lockstep**: `CHANGELOG.md`, `BACKLOG.md` (or `SPRINT_TRACKER.md`), and `journal.md` synchronized.
3. **Git Hygiene**: Working tree clean and local branch in parity with remote tracking branch.
4. **Architectural & Math Parity**: AST boundary checks pass and zero absolute path leaks.
5. **Live Test Suite Verification**: Real test suite executed, extracting certified passed/skipped/failed tallies into `.gemini/governance/validation_receipt.json`.
