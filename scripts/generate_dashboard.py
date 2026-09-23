#!/usr/bin/env python3
"""
Cetana Labs — Portfolio Web Dashboard Generator
Generates a zero-dependency, ultra-fast, responsive static HTML dashboard (docs/index.html)
with real-time client-side search, filtering, and 1-click WhatsApp executive briefing export.
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
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Cetana Labs — Engineering Portfolio Dashboard</title>
  <meta name="description" content="Executive management command plane, active project registry, and automated status tracker.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {{
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
      --info: #0284c7;
      --info-bg: rgba(2, 132, 199, 0.12);
      --danger: #ef4444;
      --danger-bg: rgba(239, 68, 68, 0.12);
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background: var(--bg);
      color: var(--text-main);
      line-height: 1.5;
      padding: 2rem 1.5rem;
      min-height: 100vh;
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
      gap: 1rem;
    }}

    .brand-title {{
      font-size: 1.875rem;
      font-weight: 800;
      letter-spacing: -0.025em;
      background: linear-gradient(135deg, #ffffff 0%, #94a3b8 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }}

    .brand-subtitle {{
      color: var(--text-muted);
      font-size: 0.95rem;
      margin-top: 0.25rem;
    }}

    .btn {{
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      background: #1e293b;
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
      background: #334155;
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
      border-color: #475569;
    }}
    .tab.active {{
      background: #1e293b;
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
      transition: all 0.2s ease;
    }}
    .project-card:hover {{
      border-color: var(--card-hover);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
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
    .health-on-track {{ background: var(--success-bg); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }}
    .health-pending {{ background: var(--warning-bg); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }}
    .health-completed {{ background: rgba(148, 163, 184, 0.12); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.25); }}

    .card-header-main {{
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }}
    .card-title {{
      font-size: 1.15rem;
      font-weight: 700;
      letter-spacing: -0.015em;
      color: #ffffff;
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
      color: #cbd5e1;
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
      color: #e2e8f0;
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
      background: rgba(245, 158, 11, 0.08);
      border: 1px dashed rgba(245, 158, 11, 0.35);
      border-radius: 8px;
      padding: 0.85rem;
      font-size: 0.8rem;
      color: #fde68a;
      display: flex;
      flex-direction: column;
      gap: 0.3rem;
    }}

    .card-footer {{
      margin-top: auto;
      padding-top: 1rem;
      border-top: 1px solid var(--card-border);
      display: flex;
      justify-content: space-between;
      align-items: center;
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
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
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
        <div style="display: flex; gap: 0.75rem;">
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
          <span class="kpi-val" style="color: #34d399;">{active_count}</span>
          <span class="kpi-sub">Client & product initiatives</span>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Onboarding Setup</span>
          <span class="kpi-val" style="color: #fbbf24;">{onboarding_count}</span>
          <span class="kpi-sub">Awaiting /status-init baseline</span>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Completed Spikes</span>
          <span class="kpi-val" style="color: #cbd5e1;">{completed_count}</span>
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
            html += """        <div class="alert-box">
          <strong>⚠️ Onboarding Protocol Pending</strong>
          <span>Run <code>/status-init</code> in repo root to establish verified sprint deliverables and metrics.</span>
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
          <p style="font-size: 0.825rem; color: #cbd5e1;">{focus}</p>
        </div>
"""

        html += f"""        <div class="card-footer">
          <div class="card-actions">
            <button class="btn" onclick="copySingleBriefing(this)" data-briefing="{p['b64_briefing']}">
              📋 Copy WhatsApp Status
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
      setTimeout(() => toast.classList.remove('show'), 2500);
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
  </script>
</body>
</html>
"""

    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"✅ Dashboard generated successfully: {OUTPUT_HTML} ({len(projects_data)} projects rendered)")
    return 0


if __name__ == "__main__":
    sys.exit(build_dashboard())
