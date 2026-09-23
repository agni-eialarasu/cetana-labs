---
name: project-status
description: >-
  Generates an on-demand WhatsApp-compatible executive status message for management across all projects or a specific project (e.g. "/project-status", "/project-status LAB-003"). Parses the authoritative STATUS.md protocol file.
---

# Skill: On-Demand Project Status Broadcast (`/project-status`)

## Objective
Generate a mobile-friendly, executive-ready WhatsApp status broadcast for leadership by reading the standardized `STATUS.md` files across projects in `cetana-labs`.

---

## 1. Trigger Patterns
Activate this skill whenever the user invokes:
- `/project-status`
- `/project-status <ID>` (e.g. `/project-status LAB-001`, `/project-status LAB-003`)
- `/project-status all`
- *"Generate executive update for WhatsApp"*
- *"Share project status to management"*

---

## 2. Execution Steps

### Step 1: Resolve Target Scope
- If a project ID is specified (e.g. `LAB-003`), generate a **Deep Dive Single-Project Broadcast**.
- If no argument or `all` is specified, iterate through all active projects registered in [README.md](../../../README.md) and generate an **Executive Portfolio Digest**.

### Step 2: Locate & Read `STATUS.md`
For each target project:
1. First, check `projects/<ID>/STATUS.md`.
2. Also check if the project has a local adjacent repo checkout with a fresher `STATUS.md` (e.g. `../nexus-pulse/STATUS.md`, `../ammas/STATUS.md`).
3. If `STATUS.md` is missing, read the project's `README.md` and `journal.md` as fallback.

### Step 3: Format for WhatsApp
WhatsApp uses specific formatting:
- `*bold text*` for headlines and keys (Do NOT use `**double asterisks**`).
- `_italic text_` for subtitles and dates.
- `• bullet points` with clear spacing.
- **NEVER use markdown tables** (they break horribly on mobile WhatsApp).
- Include dividers like `━━━━━━━━━━━━━━━━━━━━━`.

---

## 3. Output Format Templates

### Template A: Executive Portfolio Digest (All Projects)
```text
📊 *CETANA LABS — EXECUTIVE PORTFOLIO STATUS*
_Date: [DD-Mon-YYYY] | Audience: Management Team_

━━━━━━━━━━━━━━━━━━━━━
[Health Badge] *[PROJECT ID]: [Project Name]*
• *Lead:* [Owner Name]
• *Pitch:* [1-line elevator pitch]
• *Latest Win:* [Key capability or milestone delivered]
• *Current Focus:* [What is actively being built]
• *Blockers:* [None / Specific Blocker]
🔗 [Remote Repo / Link]

━━━━━━━━━━━━━━━━━━━━━
[Repeat for each active project]

━━━━━━━━━━━━━━━━━━━━━
_Total Active Initiatives: [N] | Hard Blockers: [N]_
```

### Template B: Single Project Deep Dive (`/project-status <ID>`)
```text
🚀 *PROJECT STATUS BRIEFING: [Project Name] ([PROJECT ID])*
_Lead: [Owner Name] | Date: [DD-Mon-YYYY]_
_Health: [Health Badge]_

━━━━━━━━━━━━━━━━━━━━━
📌 *BUSINESS VALUE & PURPOSE*
[2-sentence elevator pitch]

🌟 *LATEST DELIVERIES & WINS*
• *[Win 1]:* [Description of impact]
• *[Win 2]:* [Description of impact]

🎯 *CURRENT FOCUS & NEXT MILESTONE*
• [What the team is actively executing right now]

🛡️ *QUALITY ASSURANCE & METRICS*
• [Test pass rates, performance or architectural benchmarks]

⚠️ *BLOCKERS & RISKS*
• *Blockers:* [None / Blocker details]
• *Risks:* [Key risk to monitor]

🔗 *Repository & Artifacts:*
[Remote GitHub Link]
```
