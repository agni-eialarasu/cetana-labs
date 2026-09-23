# Project Status Protocol — The `STATUS.md` Standard

This document defines the mandatory **`STATUS.md`** protocol for all projects tracked under **Cetana Labs**.

---

## 1. Motivation & Purpose

To ensure leadership, management, and cross-functional stakeholders receive **instant, high-fidelity, executive-ready updates** without interrupting engineering flow:
- Every project must maintain a single, lightweight **`STATUS.md`** file at its root.
- The AI agent parses this file on demand via `/project-status` to generate **WhatsApp-compatible broadcasts** for management in seconds.
- Updating `STATUS.md` takes **under 2 minutes** at the close of a sprint or milestone.

---

## 2. File Location Rules

| Project Type | Where `STATUS.md` Resides |
| :--- | :--- |
| **External Mini-Apps / Services** (e.g. `nexus-pulse`, `ammas`) | In the root of the project's own Git repository (`<repo>/STATUS.md`), with a synced copy or reference in `cetana-labs/projects/<ID>/STATUS.md`. |
| **Internal Research Spikes / Benchmarks** (e.g. `wrenai-eval`) | Directly inside `cetana-labs/projects/<ID>/STATUS.md`. |

---

## 3. The Authoritative `STATUS.md` Schema

Every `STATUS.md` MUST adhere to this concise, 5-section markdown template (maximum 30–40 lines):

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
| **On Track** | `🟢 On Track` | Milestones progressing as scheduled. |
| **At Risk** | `🟡 At Risk` | Minor delays or external dependencies pending; no escalation yet. |
| **Blocked** | `🔴 Blocked` | Hard blocker requiring management intervention. |
| **Paused** | `⏸️ Paused` | Intentionally on hold. |
| **Completed** | `✅ Completed` | Deliverables finished or successfully operationalized. |

---

## 5. Automated Consumption via `/project-status`

When `/project-status [project_id]` is executed:
1. The AI agent locates the relevant `STATUS.md` file(s).
2. It extracts the Elevator Pitch, Latest Wins, Current Focus, Health, and Blockers.
3. It formats a crisp, emoji-rich, WhatsApp-friendly broadcast message ready to copy-paste.
