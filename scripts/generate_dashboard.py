#!/usr/bin/env python3
"""
Cetana Labs — Portfolio Web Dashboard Generator
Generates a zero-dependency, ultra-fast, responsive static HTML dashboard (docs/index.html)
with real-time client-side search, filtering, theme toggle (System/Light/Dark),
1-click WhatsApp executive briefing export, and 1-click AI Onboarding Prompt generation.
"""

import sys
import os
import json
import re
import base64
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECTS_DIR = REPO_ROOT / "projects"
DOCS_DIR = REPO_ROOT / "docs"
OUTPUT_HTML = DOCS_DIR / "index.html"

# Add scripts directory to path to import generate_status helpers
sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_status import parse_status_file, format_single_project, format_portfolio_digest


def extract_archetype(readme_path: Path) -> tuple[str, str]:
    """Extracts archetype name and icon from project README.md."""
    if not readme_path.exists():
        return "Mini-App", "💻"
    content = readme_path.read_text(encoding="utf-8")
    arch_match = re.search(r"\*\*Archetype\*\*\s*\|\s*([^|\n]+)", content)
    if arch_match:
        val = arch_match.group(1).strip()
        icon = "💻"
        name = val
        if "Research" in val or "Spike" in val:
            icon = "📑"
            name = "Research Spike"
        elif "Data" in val:
            icon = "📊"
            name = "Data Collection"
        elif "Verification" in val or "Benchmark" in val:
            icon = "🔬"
            name = "Verification"
        elif "Control Plane" in val:
            icon = "💻"
            name = "Control Plane"
        elif "Mini-App" in val:
            icon = "💻"
            name = "Mini-App"
        return name, icon
    return "Mini-App", "💻"


def generate_onboarding_prompt(data: dict) -> str:
    """Generates a tailor-made, zero-friction AI onboarding prompt for this project."""
    pid = data.get("id", "LAB-XXX")
    name = data.get("name", "Project Name")
    lead = data.get("lead", "Engineering Team")
    pitch = data.get("pitch", "") or "Engineering initiative registered in Cetana Labs."
    repo_url = data.get("repo_url", "")
    now_date = datetime.now().strftime("%Y-%m-%d")
    badge_id = pid.replace("-", "--")

    prompt = f"""Act as our Technical Delivery & Governance Lead for {name}.

### 🌐 Context & Objective
Our engineering organization has established Cetana Labs (our master engineering portfolio and management control plane at https://agni-eialarasu.github.io/cetana-labs/).

Every weekday morning at 9:30 AM IST, an automated cron engine inspects registered repositories to compile an executive status broadcast for leadership. To eliminate manual status paperwork, repetitive standup recaps, and management interruptions, {name} is registered as initiative {pid} and must follow our organization's 30-line STATUS.md protocol.

The central Cetana Labs engine automatically fetches STATUS.md from the root of this repository (on main branch).

---

### 📋 Actions Required in this Repository

#### 1. Initialize Root STATUS.md
Create or update the root STATUS.md following our strict 5-section schema under 35 lines, reflecting our current sprint baseline and verified metrics:

# Project Status & Executive Summary

| Property | Value |
| :--- | :--- |
| **Project ID** | {pid} |
| **Project Name** | {name} |
| **Current Health** | 🟢 On Track |
| **Owner / Lead** | {lead} |
| **Last Updated** | {now_date} |

---

### 1. Elevator Pitch (Business Purpose)
{pitch}

### 2. Latest Deliveries & Business Wins
- **Sprint Baseline Delivery**: Summarize 1-2 major technical or architectural deliveries achieved in recent commits.
- **Protocol Baseline**: Initialized Cetana Labs status protocol ({pid}) for automated executive tracking.

### 3. Current Focus & Next Milestone
- Immediate sprint focus and upcoming deliverable milestones.

### 4. Blockers & Risks
- **Blockers**: None.
- **Key Risks**: None identified.

### 5. Verified Quality Metrics
- Automated test suite passing status (e.g. tests passing, build verification).


#### 2. Embed the Governance Protocol into AGENTS.md (or .cursorrules)
Add this section under governance so all future AI agents know how to update status during sprint closeouts:

---

## Status Protocol & Executive Cadence (`/status-update`)

When the user asks for `/status-update` or completes a sprint milestone:
1. Inspect the last 5 commits (`git log -n 5 --oneline`) and recent test/sprint outputs.
2. Update root `STATUS.md`:
   - Set `Last Updated` to today's date (`YYYY-MM-DD`).
   - Prepend top 1-2 new deliverable wins under `2. Latest Deliveries & Business Wins` (keep top 3-4 bullets).
   - Update `3. Current Focus & Next Milestone`.
   - Update `5. Verified Quality Metrics` with latest test counts.
   - Ensure the file remains under 35 lines.
3. Commit with message: `docs: update STATUS.md for <sprint/milestone>`.
4. Output a concise WhatsApp-compatible update using bold headers and bullet points.


#### 3. Link Cetana Labs in README.md
In the top badge row of README.md, add the Cetana Labs portfolio badge:
[![Cetana Labs: {pid}](https://img.shields.io/badge/Cetana_Labs-{badge_id}-blue.svg)](https://agni-eialarasu.github.io/cetana-labs/)


#### 4. Stage, Commit & Push
1. Stage STATUS.md, AGENTS.md, and README.md.
2. Commit with message:
   docs(governance): initialize Cetana Labs STATUS.md protocol ({pid})
3. Push to origin main.


#### 5. Output Verification Broadcast
Finally, output the ready-to-paste WhatsApp executive update snippet formatted with bold headers and clean dividers (━━━━━━━━━━━━━━━━━━━━━).
"""
    return prompt.strip()


def build_dashboard():
    project_dirs = sorted([d for d in PROJECTS_DIR.iterdir() if d.is_dir() and d.name.startswith("LAB-")])
    projects_data = []

    for pdir in project_dirs:
        status_file = pdir / "STATUS.md"
        readme_file = pdir / "README.md"
        data = parse_status_file(status_file)
        if not data:
            continue

        arch_name, arch_icon = extract_archetype(readme_file)
        data["archetype_name"] = arch_name
        data["archetype_icon"] = arch_icon
        data["folder_name"] = pdir.name
        single_briefing = format_single_project(data)
        data["whatsapp_briefing"] = single_briefing
        data["b64_briefing"] = base64.b64encode(single_briefing.encode("utf-8")).decode("utf-8")

        # Generate pre-filled AI onboarding prompt
        onboarding_prompt = generate_onboarding_prompt(data)
        data["onboarding_prompt"] = onboarding_prompt
        data["b64_onboarding"] = base64.b64encode(onboarding_prompt.encode("utf-8")).decode("utf-8")

        # Categorization tags
        tags = []
        if data["id"] == "LAB-000":
            tags.append("control-plane")
        elif data.get("is_completed"):
            tags.append("completed")
        else:
            tags.append("active")
            if data.get("is_onboarding_pending"):
                tags.append("onboarding-pending")
            else:
                tags.append("on-track")
        data["tags"] = tags
        projects_data.append(data)

    portfolio_whatsapp = format_portfolio_digest(projects_data)
    b64_portfolio = base64.b64encode(portfolio_whatsapp.encode("utf-8")).decode("utf-8")

    # Compute KPI totals
    total_projects = len(projects_data)
    active_count = sum(1 for p in projects_data if "active" in p["tags"])
    onboarding_count = sum(1 for p in projects_data if "onboarding-pending" in p["tags"])
    completed_count = sum(1 for p in projects_data if "completed" in p["tags"])

    now_str = datetime.now().strftime("%d-%b-%Y %H:%M IST")

    # Render HTML template
    html = f"""<!DOCTYPE html>
<html lang="en" data-theme="system">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Cetana Labs — Engineering Portfolio Dashboard</title>
  <meta name="description" content="Executive management command plane, active project registry, and automated status tracker.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    /* Default / Dark Theme Palette */
    :root, [data-theme="dark"] {{
      --bg: #090d16;
      --card-bg: #121826;
      --card-border: #1f293d;
      --card-hover: #26334d;
      --text-main: #f1f5f9;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      --accent: #38bdf8;
      --accent-glow: rgba(56, 189, 248, 0.15);
      --success: #10b981;
      --success-bg: rgba(16, 185, 129, 0.12);
      --warning: #f59e0b;
      --warning-bg: rgba(245, 158, 11, 0.12);
      --warning-border: rgba(245, 158, 11, 0.35);
      --info: #0284c7;
      --info-bg: rgba(2, 132, 199, 0.12);
      --danger: #ef4444;
      --danger-bg: rgba(239, 68, 68, 0.12);
      --btn-bg: #1e293b;
      --btn-hover: #334155;
      --shadow-color: rgba(0, 0, 0, 0.35);
    }}

    /* Light Theme Palette */
    [data-theme="light"] {{
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --card-border: #e2e8f0;
      --card-hover: #cbd5e1;
      --text-main: #0f172a;
      --text-muted: #475569;
      --text-dim: #64748b;
      --accent: #0284c7;
      --accent-glow: rgba(2, 132, 199, 0.1);
      --success: #059669;
      --success-bg: rgba(5, 150, 105, 0.1);
      --warning: #d97706;
      --warning-bg: rgba(217, 119, 6, 0.1);
      --warning-border: rgba(217, 119, 6, 0.35);
      --info: #0284c7;
      --info-bg: rgba(2, 132, 199, 0.1);
      --danger: #dc2626;
      --danger-bg: rgba(220, 38, 38, 0.1);
      --btn-bg: #f1f5f9;
      --btn-hover: #e2e8f0;
      --shadow-color: rgba(0, 0, 0, 0.08);
    }}

    /* System Theme Auto Detection */
    @media (prefers-color-scheme: light) {{
      [data-theme="system"] {{
        --bg: #f8fafc;
        --card-bg: #ffffff;
        --card-border: #e2e8f0;
        --card-hover: #cbd5e1;
        --text-main: #0f172a;
        --text-muted: #475569;
        --text-dim: #64748b;
        --accent: #0284c7;
        --accent-glow: rgba(2, 132, 199, 0.1);
        --success: #059669;
        --success-bg: rgba(5, 150, 105, 0.1);
        --warning: #d97706;
        --warning-bg: rgba(217, 119, 6, 0.1);
        --warning-border: rgba(217, 119, 6, 0.35);
        --info: #0284c7;
        --info-bg: rgba(2, 132, 199, 0.1);
        --danger: #dc2626;
        --danger-bg: rgba(220, 38, 38, 0.1);
        --btn-bg: #f1f5f9;
        --btn-hover: #e2e8f0;
        --shadow-color: rgba(0, 0, 0, 0.08);
      }}
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background: var(--bg);
      color: var(--text-main);
      line-height: 1.5;
      padding: 2rem 1.5rem;
      min-height: 100vh;
      transition: background-color 0.25s ease, color 0.25s ease;
    }}

    .container {{
      max-width: 1280px;
      margin: 0 auto;
    }}

    /* Header */
    header {{
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
      margin-bottom: 2.5rem;
      border-bottom: 1px solid var(--card-border);
      padding-bottom: 2rem;
    }}

    .header-top {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: flex-start;
      gap: 1.25rem;
    }}

    .brand-title {{
      font-size: 1.875rem;
      font-weight: 800;
      letter-spacing: -0.025em;
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }}

    .brand-subtitle {{
      color: var(--text-muted);
      font-size: 0.95rem;
      margin-top: 0.25rem;
    }}

    .header-actions {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 0.75rem;
    }}

    /* Theme Switcher Segmented Control */
    .theme-switcher {{
      display: inline-flex;
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 8px;
      padding: 0.25rem;
      gap: 0.2rem;
    }}

    .theme-btn {{
      background: transparent;
      border: none;
      color: var(--text-muted);
      padding: 0.35rem 0.65rem;
      border-radius: 6px;
      font-size: 0.775rem;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      transition: all 0.15s ease;
    }}

    .theme-btn:hover {{
      color: var(--text-main);
    }}

    .theme-btn.active {{
      background: var(--btn-bg);
      color: var(--accent);
      box-shadow: 0 1px 3px var(--shadow-color);
    }}

    .btn {{
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      background: var(--btn-bg);
      color: var(--text-main);
      border: 1px solid var(--card-border);
      padding: 0.65rem 1.15rem;
      border-radius: 8px;
      font-size: 0.875rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      text-decoration: none;
    }}
    .btn:hover {{
      background: var(--btn-hover);
      border-color: var(--accent);
      transform: translateY(-1px);
    }}
    .btn-primary {{
      background: #0284c7;
      border-color: #38bdf8;
      color: #ffffff;
      box-shadow: 0 0 15px rgba(56, 189, 248, 0.25);
    }}
    .btn-primary:hover {{
      background: #0369a1;
      border-color: #7dd3fc;
    }}
    .btn-warning {{
      background: rgba(245, 158, 11, 0.15);
      border-color: var(--warning-border);
      color: var(--warning);
    }}
    .btn-warning:hover {{
      background: rgba(245, 158, 11, 0.25);
      border-color: var(--warning);
    }}

    /* KPI Bar */
    .kpi-bar {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1rem;
    }}

    .kpi-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 10px;
      padding: 1.1rem 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
      transition: background-color 0.25s ease, border-color 0.25s ease;
    }}
    .kpi-label {{
      font-size: 0.8rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-dim);
    }}
    .kpi-val {{
      font-size: 1.75rem;
      font-weight: 800;
      letter-spacing: -0.02em;
    }}
    .kpi-sub {{
      font-size: 0.75rem;
      color: var(--text-muted);
    }}

    /* Controls: Search & Tabs */
    .controls {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 1rem;
      margin-bottom: 2rem;
    }}

    .tabs {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }}
    .tab {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      color: var(--text-muted);
      padding: 0.5rem 0.95rem;
      border-radius: 6px;
      font-size: 0.85rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
    }}
    .tab:hover {{
      color: var(--text-main);
      border-color: var(--card-hover);
    }}
    .tab.active {{
      background: var(--btn-bg);
      color: var(--accent);
      border-color: var(--accent);
    }}

    .search-box {{
      position: relative;
      min-width: 260px;
    }}
    .search-box input {{
      width: 100%;
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 8px;
      padding: 0.55rem 1rem 0.55rem 2.25rem;
      color: var(--text-main);
      font-size: 0.875rem;
      outline: none;
      transition: border-color 0.2s;
    }}
    .search-box input:focus {{
      border-color: var(--accent);
    }}
    .search-box svg {{
      position: absolute;
      left: 0.75rem;
      top: 50%;
      transform: translateY(-50%);
      width: 16px;
      height: 16px;
      stroke: var(--text-dim);
    }}

    /* Project Cards Grid */
    .cards-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(370px, 1fr));
      gap: 1.5rem;
    }}

    .project-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 1.4rem;
      display: flex;
      flex-direction: column;
      gap: 1.15rem;
      box-shadow: 0 2px 8px var(--shadow-color);
      transition: all 0.2s ease;
    }}
    .project-card:hover {{
      border-color: var(--card-hover);
      box-shadow: 0 6px 20px var(--shadow-color);
      transform: translateY(-2px);
    }}

    .card-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .id-badge {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.75rem;
      font-weight: 700;
      color: var(--accent);
      background: var(--accent-glow);
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      border: 1px solid rgba(56, 189, 248, 0.25);
    }}

    .health-pill {{
      font-size: 0.75rem;
      font-weight: 600;
      padding: 0.2rem 0.6rem;
      border-radius: 12px;
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
    }}
    .health-on-track {{ background: var(--success-bg); color: var(--success); border: 1px solid rgba(16, 185, 129, 0.3); }}
    .health-pending {{ background: var(--warning-bg); color: var(--warning); border: 1px solid rgba(245, 158, 11, 0.3); }}
    .health-completed {{ background: rgba(148, 163, 184, 0.12); color: var(--text-muted); border: 1px solid rgba(148, 163, 184, 0.25); }}

    .card-header-main {{
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }}
    .card-title {{
      font-size: 1.15rem;
      font-weight: 700;
      letter-spacing: -0.015em;
      color: var(--text-main);
    }}
    .card-meta {{
      font-size: 0.8rem;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }}

    .pitch-box {{
      font-size: 0.875rem;
      color: var(--text-muted);
      line-height: 1.45;
    }}

    .section-title {{
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-dim);
      margin-bottom: 0.4rem;
    }}

    .wins-list {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 0.4rem;
    }}
    .wins-list li {{
      font-size: 0.825rem;
      color: var(--text-main);
      position: relative;
      padding-left: 1rem;
      line-height: 1.4;
    }}
    .wins-list li::before {{
      content: "•";
      color: var(--accent);
      position: absolute;
      left: 0;
      font-weight: bold;
    }}

    .alert-box {{
      background: var(--warning-bg);
      border: 1px dashed var(--warning-border);
      border-radius: 8px;
      padding: 0.95rem;
      font-size: 0.825rem;
      color: var(--warning);
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }}

    .card-footer {{
      margin-top: auto;
      padding-top: 1rem;
      border-top: 1px solid var(--card-border);
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }}

    .card-actions {{
      display: flex;
      gap: 0.5rem;
      width: 100%;
    }}
    .card-actions .btn {{
      flex: 1;
      justify-content: center;
      font-size: 0.775rem;
      padding: 0.5rem 0.6rem;
    }}

    /* Toast Notification */
    #toast {{
      position: fixed;
      bottom: 2rem;
      right: 2rem;
      background: #0284c7;
      color: #ffffff;
      padding: 0.85rem 1.4rem;
      border-radius: 8px;
      font-size: 0.875rem;
      font-weight: 600;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
      opacity: 0;
      transform: translateY(15px);
      transition: all 0.25s ease;
      pointer-events: none;
      z-index: 1000;
    }}
    #toast.show {{
      opacity: 1;
      transform: translateY(0);
    }}

    footer {{
      margin-top: 3.5rem;
      padding-top: 1.5rem;
      border-top: 1px solid var(--card-border);
      text-align: center;
      font-size: 0.8rem;
      color: var(--text-dim);
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="header-top">
        <div>
          <h1 class="brand-title">🌐 Cetana Labs</h1>
          <p class="brand-subtitle">Executive Engineering Portfolio & Automated Status Dashboard</p>
        </div>
        <div class="header-actions">
          <!-- Theme Switcher -->
          <div class="theme-switcher">
            <button class="theme-btn active" id="theme-system" onclick="setTheme('system')">
              💻 System
            </button>
            <button class="theme-btn" id="theme-light" onclick="setTheme('light')">
              ☀️ Light
            </button>
            <button class="theme-btn" id="theme-dark" onclick="setTheme('dark')">
              🌙 Dark
            </button>
          </div>

          <button class="btn btn-primary" onclick="copyPortfolioBriefing()">
            📋 Copy Executive WhatsApp Digest
          </button>
          <a href="https://github.com/agni-eialarasu/cetana-labs" target="_blank" class="btn">
            GitHub Repository ↗
          </a>
        </div>
      </div>

      <div class="kpi-bar">
        <div class="kpi-card">
          <span class="kpi-label">Total Initiatives</span>
          <span class="kpi-val" style="color: var(--accent);">{total_projects}</span>
          <span class="kpi-sub">Registered in Cetana Labs</span>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Active Projects</span>
          <span class="kpi-val" style="color: var(--success);">{active_count}</span>
          <span class="kpi-sub">Client & product initiatives</span>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Onboarding Setup</span>
          <span class="kpi-val" style="color: var(--warning);">{onboarding_count}</span>
          <span class="kpi-sub">Awaiting /status-init baseline</span>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Completed Spikes</span>
          <span class="kpi-val" style="color: var(--text-muted);">{completed_count}</span>
          <span class="kpi-sub">Operationalized & archived</span>
        </div>
      </div>
    </header>

    <div class="controls">
      <div class="tabs">
        <button class="tab active" onclick="setFilter('all', this)">All Projects ({total_projects})</button>
        <button class="tab" onclick="setFilter('active', this)">Active Products ({active_count})</button>
        <button class="tab" onclick="setFilter('onboarding-pending', this)">Onboarding Pending ({onboarding_count})</button>
        <button class="tab" onclick="setFilter('completed', this)">Completed ({completed_count})</button>
        <button class="tab" onclick="setFilter('control-plane', this)">Control Hub (1)</button>
      </div>
      <div class="search-box">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
        <input type="text" id="searchInput" placeholder="Search by title, lead, ID..." oninput="handleSearch()">
      </div>
    </div>

    <div class="cards-grid" id="cardsGrid">
"""

    for p in projects_data:
        health = p["health"]
        health_class = "health-on-track"
        if "pending" in health.lower() or "setup" in health.lower():
            health_class = "health-pending"
        elif "completed" in health.lower():
            health_class = "health-completed"

        tags_str = " ".join(p["tags"])

        html += f"""      <div class="project-card" data-tags="{tags_str}" data-search="{p['id']} {p['name']} {p['lead']} {p['archetype_name']}">
        <div class="card-top">
          <span class="id-badge">{p['id']}</span>
          <span class="health-pill {health_class}">{health}</span>
        </div>
        <div class="card-header-main">
          <h2 class="card-title">{p['name']}</h2>
          <div class="card-meta">
            <span>👤 {p['lead']}</span>
            <span>•</span>
            <span>{p['archetype_icon']} {p['archetype_name']}</span>
          </div>
        </div>

        <div class="pitch-box">
          {p['pitch']}
        </div>
"""
        if p.get("is_onboarding_pending"):
            html += f"""        <div class="alert-box">
          <strong>⚠️ Onboarding Protocol Pending</strong>
          <span>Initial baseline <code>STATUS.md</code> has not yet been committed to this repository.</span>
          <button class="btn btn-warning" onclick="copyOnboardingPrompt(this)" data-prompt="{p['b64_onboarding']}" data-pid="{p['id']}" style="width: 100%; justify-content: center; font-weight: 700; margin-top: 0.35rem;">
            🤖 Copy AI Onboarding Prompt (1-Click Setup)
          </button>
        </div>
"""
        else:
            wins = p.get("wins", [])
            if wins:
                html += """        <div>
          <div class="section-title">Latest Deliveries & Wins</div>
          <ul class="wins-list">
"""
                for win in wins[:3]:
                    clean_win = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", win)
                    html += f"            <li>{clean_win}</li>\n"
                html += """          </ul>
        </div>
"""

            focus = p.get("focus")
            if focus:
                html += f"""        <div>
          <div class="section-title">Current Focus</div>
          <p style="font-size: 0.825rem; color: var(--text-muted);">{focus}</p>
        </div>
"""

        html += f"""        <div class="card-footer">
          <div class="card-actions">
            <button class="btn" onclick="copySingleBriefing(this)" data-briefing="{p['b64_briefing']}">
              📋 Copy WhatsApp Status
            </button>
            <button class="btn" title="Copy pre-filled AI Prompt for this repo" onclick="copyOnboardingPrompt(this)" data-prompt="{p['b64_onboarding']}" data-pid="{p['id']}">
              🤖 AI Prompt
            </button>
"""
        if p.get("repo_url"):
            html += f"""            <a href="{p['repo_url']}" target="_blank" class="btn">
              Codebase ↗
            </a>
"""
        html += """          </div>
        </div>
      </div>
"""

    html += f"""    </div>

    <footer>
      <p>Cetana Labs Control Hub • Last Generated: {now_str} • Auto-synchronized from authoritative STATUS.md records</p>
    </footer>
  </div>

  <div id="toast">Copied to clipboard! Ready to paste into WhatsApp.</div>

  <script>
    const b64Portfolio = "{b64_portfolio}";
    let currentFilter = 'all';

    // Theme Management: System (default), Light, Dark
    function applyTheme(theme) {{
      document.documentElement.setAttribute('data-theme', theme);
      document.querySelectorAll('.theme-btn').forEach(btn => btn.classList.remove('active'));
      const activeBtn = document.getElementById('theme-' + theme);
      if (activeBtn) activeBtn.classList.add('active');
    }}

    function setTheme(theme) {{
      localStorage.setItem('cetana-theme', theme);
      applyTheme(theme);
    }}

    // Initialize Theme (Default to system)
    const savedTheme = localStorage.getItem('cetana-theme') || 'system';
    applyTheme(savedTheme);

    // Watch OS Theme Changes when in 'system' mode
    if (window.matchMedia) {{
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {{
        if ((localStorage.getItem('cetana-theme') || 'system') === 'system') {{
          applyTheme('system');
        }}
      }});
    }}

    function setFilter(filter, el) {{
      currentFilter = filter;
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      el.classList.add('active');
      filterCards();
    }}

    function handleSearch() {{
      filterCards();
    }}

    function filterCards() {{
      const query = document.getElementById('searchInput').value.toLowerCase().trim();
      const cards = document.querySelectorAll('.project-card');

      cards.forEach(card => {{
        const tags = card.getAttribute('data-tags') || '';
        const searchTarget = card.getAttribute('data-search').toLowerCase();

        const matchesFilter = (currentFilter === 'all') || tags.includes(currentFilter);
        const matchesQuery = !query || searchTarget.includes(query);

        if (matchesFilter && matchesQuery) {{
          card.style.display = 'flex';
        }} else {{
          card.style.display = 'none';
        }}
      }});
    }}

    function showToast(msg) {{
      const toast = document.getElementById('toast');
      toast.textContent = msg || 'Copied to clipboard!';
      toast.classList.add('show');
      setTimeout(() => toast.classList.remove('show'), 3000);
    }}

    function copyPortfolioBriefing() {{
      try {{
        const text = decodeURIComponent(escape(window.atob(b64Portfolio)));
        navigator.clipboard.writeText(text).then(() => {{
          showToast('📋 Executive Portfolio Digest copied to clipboard!');
        }}).catch(err => {{
          console.error('Failed to copy', err);
        }});
      }} catch (e) {{
        console.error('Decoding failed', e);
      }}
    }}

    function copySingleBriefing(btn) {{
      try {{
        const rawB64 = btn.getAttribute('data-briefing') || '';
        const text = decodeURIComponent(escape(window.atob(rawB64)));
        navigator.clipboard.writeText(text).then(() => {{
          showToast('📋 Project WhatsApp update copied to clipboard!');
        }}).catch(err => {{
          console.error('Failed to copy', err);
        }});
      }} catch (e) {{
        console.error('Decoding failed', e);
      }}
    }}

    function copyOnboardingPrompt(btn) {{
      try {{
        const pid = btn.getAttribute('data-pid') || 'Project';
        const rawB64 = btn.getAttribute('data-prompt') || '';
        const text = decodeURIComponent(escape(window.atob(rawB64)));
        navigator.clipboard.writeText(text).then(() => {{
          showToast('🤖 AI Onboarding Prompt for ' + pid + ' copied! Ready to paste into Cursor/Claude/Copilot.');
        }}).catch(err => {{
          console.error('Failed to copy', err);
        }});
      }} catch (e) {{
        console.error('Decoding failed', e);
      }}
    }}
  </script>
</body>
</html>
"""

    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"✅ Dashboard generated successfully: {OUTPUT_HTML} ({len(projects_data)} projects rendered)")
    return 0


if __name__ == "__main__":
    sys.exit(build_dashboard())
