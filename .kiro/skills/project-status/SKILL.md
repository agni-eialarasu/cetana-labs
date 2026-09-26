---
name: project-status
description: >-
  Generates an on-demand WhatsApp-compatible executive status message for management across all active projects or a specific project (e.g. "/project-status", "/project-status LAB-003"). Parses authoritative STATUS.md files and excludes completed projects.
---

# Skill: On-Demand Project Status Broadcast (`/project-status`)

## Objective
Generate a mobile-friendly, executive-ready WhatsApp status broadcast for leadership by reading the standardized `STATUS.md` files across projects in `cetana-labs`.

---

## 1. Trigger Patterns
Activate this skill whenever the user invokes:
- `/project-status`
- `/project-status <ID>` (e.g. `/project-status LAB-000`, `/project-status LAB-003`, `/project-status LAB-005`)
- `/project-status all`
- *"Generate executive update for WhatsApp"*
- *"Share project status to management"*

---

## 2. Automated Execution Engine

The authoritative implementation is executed directly via Python:
```bash
# Full active portfolio digest
python3 scripts/generate_status.py

# Single project deep-dive
python3 scripts/generate_status.py LAB-XXX

# Output with GitHub Actions step summary markdown block
python3 scripts/generate_status.py --github-summary
```

---

## 3. Core Filtering & Presentation Rules

1. **Active Initiatives Only**:
   - The default portfolio digest excludes completed initiatives (`✅ Completed`) and the central control hub kernel (`LAB-000`).
   - Completed counts are summarized in the digest footer.
2. **Onboarding Pending Alert ("Soft Pressure")**:
   - Projects in `⏳ Onboarding Pending` have routine wins suppressed.
   - The generator injects an alert and CTA instructing the lead to run `/status-init`.
3. **Sprint Cadence Staleness (> 14 Days)**:
   - If an active project's `Last Updated` date is older than 14 days, a subtle cadence reminder is appended.
4. **WhatsApp Text Optimization**:
   - `*bold text*` for headings (no double-asterisks `**`).
   - `_italic text_` for subtitles and dates.
   - Clean horizontal ASCII dividers (`━━━━━━━━━━━━━━━━━━━━━`).
   - Strictly **no markdown tables** (tables break on mobile WhatsApp).
