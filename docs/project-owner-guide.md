# Project Lead & Developer Guide — Automated Status Protocol

Welcome! This guide is for **project leads and contributing engineers** (e.g. Nexus Pulse, AAMAS, Zerobea.ai, and upcoming initiatives).

To eliminate repetitive status writing, long standup recaps, and management interruptions, our engineering organization uses a **single, 30-line `STATUS.md` file at the root of every project repository**.

---

## ⚡ The Big Idea: Zero Manual Paperwork

You **never write this file by hand**. Your AI coding assistant (Cursor, Claude Code, GitHub Copilot, ChatGPT, Antigravity) does it for you in **10 seconds** whenever you complete a sprint or merge major PRs.

```text
Developer prompts: "/status-update"
       │
       ▼
AI inspects recent Git commits / PRs
       │
       ├──── 1. Updates root STATUS.md & commits
       └──── 2. Outputs a ready-to-send WhatsApp standup message for your team!
```

---

## 🎯 Constructive Visibility: Why We Do This

Every weekday morning at 9:30 AM IST, our automated system generates an executive portfolio update for management and engineering leadership.

1. **When your project is first registered:**
   - It appears as **`⏳ Onboarding Pending`** with an alert:
     `• *Status Alert:* ⚠️ Initial onboarding protocol pending from project lead.`
     `• *Action Required:* Run /status-init in repo root to establish sprint baseline.`
   - Running `/status-init` and pushing `STATUS.md` immediately promotes your badge to **`🟢 On Track`** with your real wins!

2. **Sprint Cadence Reminder (> 14 Days):**
   - If your project goes longer than 14 days without an update, a gentle reminder appears in the morning brief:
     `• *Cadence Notice:* ℹ️ Last updated 16 days ago. Awaiting sprint closeout (/status-update).`
   - Running `/status-update` at each sprint close keeps your project green and leadership fully informed without interrupting you.

---

## 🚀 Step 1: Initialize `STATUS.md` (Run Once)

If your repository doesn't have a `STATUS.md` yet, open your AI chat tool inside your repository and paste:

> ### 📋 AI Prompt: Initialize Status (`/status-init`)
> ```text
> Act as our technical delivery assistant. Inspect this repository's README.md, package manifests, and recent git history. 
> Create a standardized root `STATUS.md` adhering to our engineering protocol:
> - Project Name & Health (🟢 On Track)
> - 2-sentence business elevator pitch
> - Top 2-3 recent deliverable wins with technical and business impact
> - Current focus for the next sprint
> - Verified test metrics (e.g. test pass count, boundary gates)
> - Format strictly with standard markdown table and 5 sections under 35 lines.
> ```

---

## 🔄 Step 2: Routine Milestone / Sprint Updates

Whenever you close a sprint, merge a feature branch, or achieve a milestone, paste:

> ### 📋 AI Prompt: Update Status (`/status-update`)
> ```text
> Act as our technical delivery assistant. Run `git log -n 5 --oneline` (and inspect recent PRs).
> 1. Synthesize the top 1-2 deliverables into business-impact bullets.
> 2. Update root `STATUS.md`:
>    - Update "Last Updated" to today's date.
>    - Prepend the new win(s) under "Latest Deliveries & Business Wins" (keep top 3-4).
>    - Update "Current Focus & Next Milestone".
>    - Update "Verified Quality Metrics" with latest test results.
> 3. Commit the change with message: "docs: update STATUS.md for <sprint/milestone>".
> 4. Output a concise WhatsApp-compatible update (using *bold* and bullet points) that I can send to our team chat.
> ```

---

## 📱 Step 3: Instant WhatsApp Standup Snippet (`/project-status`)

Whenever your manager or peer asks for a quick update:

> ### 📋 AI Prompt: Generate WhatsApp Update
> ```text
> Read our root `STATUS.md` and format an executive WhatsApp update:
> - Use *bold* headers and clean dividers (━━━━━━━━━━━━━━━━━━━━━)
> - Include our health badge, 2-line business pitch, latest wins, current focus, and test metrics
> - Keep it under 20 lines, mobile-scannable, no markdown tables.
> ```

---

## 🤖 Automating This in Your Repo (Optional Drop-in Config)

To make `/status-update` and `/project-status` native slash commands in your favorite AI tool:

### For Cursor (`.cursorrules` or `.cursor/rules/status.mdc`):
Add this snippet to your repo:
```markdown
# Status Protocol Rules
When the user invokes `/status-update` or asks to update status:
1. Inspect the last 5 commits (`git log -n 5 --oneline`).
2. Update `STATUS.md` following the 5-section schema (Health, Pitch, Wins, Focus, Blockers, Metrics).
3. Update "Last Updated" to today's date.
4. Output a WhatsApp-friendly standup summary using *bold* formatting.
```

### For Claude Code / Antigravity (`AGENTS.md` / `CLAUDE.md`):
Add this trigger to your existing `AGENTS.md`:
```markdown
## Command: /status-update
Inspect recent commits, update root `STATUS.md` (keep under 35 lines), commit to git, and format a WhatsApp-ready status broadcast.
```

---

## 📌 The Authoritative `STATUS.md` Template

For reference, this is what the file looks like:

```markdown
# Project Status & Executive Summary

| Property | Value |
| :--- | :--- |
| **Project ID** | LAB-XXX |
| **Project Name** | Nexus Pulse |
| **Current Health** | 🟢 On Track |
| **Owner / Lead** | Hariharasubramanian |
| **Last Updated** | YYYY-MM-DD |

---

### 1. Elevator Pitch (Business Purpose)
An enterprise operational and financial intelligence engine executing an authoritative deterministic pipeline across Commercial SOWs, Workforce Allocations, Governed Finance Margins, and Automated Risk Signals to protect company profitability.

### 2. Latest Deliveries & Business Wins
- **Deterministic Signals Engine (T-014..T-016)**: Real-time automated rule engine detecting margin erosion (SIG-01), SOW consumption risk (SIG-02), and workforce allocation conflicts (SIG-03).
- **Governed Finance Variance (T-013)**: Immutable baseline-vs-forecast variance calculations verified against golden canonical dataset `NP-GOLDEN-001`.

### 3. Current Focus & Next Milestone
- Scenario simulation engine and Next.js multi-tenant operational frontend.

### 4. Blockers & Risks
- **Blockers**: None.
- **Key Risks**: Coordinating cross-domain contract changes during rapid scenario branch evolution.

### 5. Verified Quality Metrics
- 126/126 automated test suite passing cleanly.
- 42/42 architectural AST boundary fitness checks verified with zero leaks.
```

---

## 💬 Shareable Pitch for Team Chat

Copy and send this to project leads on WhatsApp / Slack / Email:

> *"Team, to simplify executive reporting and eliminate manual status writing, we are adopting a standardized 30-line `STATUS.md` across all projects.*
>
> *You don't need to write this manually. We've set up an AI prompt pack for Cursor, Claude Code, and Copilot:*
> *1. Run `/status-init` once to create it.*
> *2. Run `/status-update` whenever you finish a sprint or merge major PRs.*
>
> *Your AI assistant inspects your recent commits, updates `STATUS.md`, and gives you a ready-to-paste WhatsApp standup update. Our central management dashboard syncs with it automatically!*
>
> *Full guide & copy-paste prompts: [docs/project-owner-guide.md](https://github.com/agni-eialarasu/cetana-labs/blob/main/docs/project-owner-guide.md)"*
