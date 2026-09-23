#!/usr/bin/env python3
"""
Cetana Labs — On-Demand Executive Status Generator
Parses authoritative STATUS.md files across projects and generates
mobile-scannable, WhatsApp-compatible text broadcasts for leadership.
"""

import sys
import os
import re
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECTS_DIR = REPO_ROOT / "projects"


def parse_status_file(status_path: Path) -> dict:
    """Parses a STATUS.md file into structured fields."""
    if not status_path.exists():
        return {}

    content = status_path.read_text(encoding="utf-8")
    data = {
        "id": "",
        "name": "",
        "health": "🟢 On Track",
        "lead": "",
        "last_updated": "",
        "pitch": "",
        "wins": [],
        "focus": "",
        "blockers": "None",
        "risks": "",
        "metrics": [],
        "repo_url": ""
    }

    # Extract table metadata
    id_match = re.search(r"\*\*Project ID\*\*\s*\|\s*([^|\n]+)", content)
    if id_match:
        data["id"] = id_match.group(1).strip()

    name_match = re.search(r"\*\*Project Name\*\*\s*\|\s*([^|\n]+)", content)
    if name_match:
        data["name"] = name_match.group(1).strip()

    health_match = re.search(r"\*\*Current Health\*\*\s*\|\s*([^|\n]+)", content)
    if health_match:
        data["health"] = health_match.group(1).strip()

    lead_match = re.search(r"\*\*(?:Owner / Lead|Lead)\*\*\s*\|\s*([^|\n]+)", content)
    if lead_match:
        data["lead"] = lead_match.group(1).strip()

    updated_match = re.search(r"\*\*Last Updated\*\*\s*\|\s*([^|\n]+)", content)
    if updated_match:
        data["last_updated"] = updated_match.group(1).strip()

    # Extract 1. Elevator Pitch
    pitch_match = re.search(r"###\s*1\.\s*Elevator Pitch[^\n]*\n+([^#]+)", content)
    if pitch_match:
        pitch_lines = [line.strip() for line in pitch_match.group(1).strip().splitlines() if line.strip()]
        data["pitch"] = " ".join(pitch_lines)

    # Extract 2. Latest Deliveries & Business Wins
    wins_match = re.search(r"###\s*2\.\s*Latest Deliveries[^\n]*\n+([^#]+)", content)
    if wins_match:
        wins_raw = wins_match.group(1).strip().splitlines()
        for line in wins_raw:
            cleaned = line.strip()
            if cleaned.startswith("- ") or cleaned.startswith("* "):
                data["wins"].append(cleaned[2:].strip())

    # Extract 3. Current Focus & Next Milestone
    focus_match = re.search(r"###\s*3\.\s*Current Focus[^\n]*\n+([^#]+)", content)
    if focus_match:
        focus_lines = [line.strip().lstrip("-* ") for line in focus_match.group(1).strip().splitlines() if line.strip()]
        data["focus"] = " ".join(focus_lines)

    # Extract 4. Blockers & Risks
    blockers_match = re.search(r"###\s*4\.\s*Blockers & Risks[^\n]*\n+([^#]+)", content)
    if blockers_match:
        blockers_raw = blockers_match.group(1).strip()
        b_match = re.search(r"\*\*Blockers\*\*:\s*([^.\n]+)", blockers_raw)
        if b_match:
            data["blockers"] = b_match.group(1).strip()
        r_match = re.search(r"\*\*Key Risks\*\*:\s*([^.\n]+)", blockers_raw)
        if r_match:
            data["risks"] = r_match.group(1).strip()

    # Extract 5. Verified Quality Metrics
    metrics_match = re.search(r"###\s*5\.\s*Verified Quality Metrics[^\n]*\n+([^#]+)", content)
    if metrics_match:
        metrics_raw = metrics_match.group(1).strip().splitlines()
        for line in metrics_raw:
            cleaned = line.strip()
            if cleaned.startswith("- ") or cleaned.startswith("* "):
                data["metrics"].append(cleaned[2:].strip())

    # Check companion README.md for remote URL
    readme_path = status_path.parent / "README.md"
    if readme_path.exists():
        readme_content = readme_path.read_text(encoding="utf-8")
        url_match = re.search(r"\[(?:GitHub Repo|Remote Repository|Repo)\]\((https://github\.com/[^)]+)\)", readme_content)
        if url_match:
            data["repo_url"] = url_match.group(1).strip()
        else:
            url_match2 = re.search(r"https://github\.com/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+", readme_content)
            if url_match2:
                data["repo_url"] = url_match2.group(0).strip().rstrip(".)")

    return data


def format_portfolio_digest(projects: list) -> str:
    """Formats all projects into an executive WhatsApp portfolio digest."""
    now_str = datetime.now().strftime("%d-%b-%Y")
    lines = [
        "📊 *CETANA LABS — EXECUTIVE PORTFOLIO STATUS*",
        f"_Date: {now_str} | Audience: Management Team_",
        ""
    ]

    total_active = len(projects)
    hard_blockers = 0

    for p in projects:
        lines.append("━━━━━━━━━━━━━━━━━━━━━")
        health = p.get("health", "🟢 On Track")
        pid = p.get("id", "LAB-???")
        name = p.get("name", "Unnamed Project")
        lead = p.get("lead", "Engineering Team")
        pitch = p.get("pitch", "")
        focus = p.get("focus", "")
        blockers = p.get("blockers", "None")

        if "block" in blockers.lower() and "none" not in blockers.lower():
            hard_blockers += 1

        lines.append(f"{health} *{pid}: {name}*")
        lines.append(f"• *Lead:* {lead}")
        if pitch:
            lines.append(f"• *Pitch:* {pitch}")

        # Primary Win (first bullet)
        wins = p.get("wins", [])
        if wins:
            # Clean markdown bold formatting for WhatsApp (*bold* instead of **bold**)
            first_win = re.sub(r"\*\*([^*]+)\*\*", r"*\1*", wins[0])
            lines.append(f"• *Latest Win:* {first_win}")

        if focus:
            lines.append(f"• *Current Focus:* {focus}")

        lines.append(f"• *Blockers:* {blockers}")

        repo_url = p.get("repo_url")
        if repo_url:
            lines.append(f"🔗 {repo_url}")
        lines.append("")

    lines.append("━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"_Total Active Initiatives: {total_active} | Hard Blockers: {hard_blockers}_")
    return "\n".join(lines)


def format_single_project(p: dict) -> str:
    """Formats a single project into an executive WhatsApp deep-dive briefing."""
    now_str = datetime.now().strftime("%d-%b-%Y")
    pid = p.get("id", "LAB-???")
    name = p.get("name", "Unnamed Project")
    lead = p.get("lead", "Engineering Team")
    health = p.get("health", "🟢 On Track")

    lines = [
        f"🚀 *PROJECT STATUS BRIEFING: {name} ({pid})*",
        f"_Lead: {lead} | Date: {now_str}_",
        f"_Health: {health}_",
        "",
        "━━━━━━━━━━━━━━━━━━━━━",
        "📌 *BUSINESS VALUE & PURPOSE*",
        p.get("pitch", "Deterministic engineering initiative."),
        "",
        "🌟 *LATEST DELIVERIES & WINS*"
    ]

    for win in p.get("wins", []):
        cleaned_win = re.sub(r"\*\*([^*]+)\*\*", r"*\1*", win)
        lines.append(f"• {cleaned_win}")

    lines.extend([
        "",
        "🎯 *CURRENT FOCUS & NEXT MILESTONE*",
        f"• {p.get('focus', 'Active sprint execution.')}",
        "",
        "🛡️ *QUALITY ASSURANCE & METRICS*"
    ])

    for m in p.get("metrics", []):
        cleaned_m = re.sub(r"\*\*([^*]+)\*\*", r"*\1*", m)
        lines.append(f"• {cleaned_m}")

    lines.extend([
        "",
        "⚠️ *BLOCKERS & RISKS*",
        f"• *Blockers:* {p.get('blockers', 'None')}",
        f"• *Risks:* {p.get('risks', 'None identified.')}"
    ])

    repo_url = p.get("repo_url")
    if repo_url:
        lines.extend([
            "",
            "🔗 *Repository & Artifacts:*",
            repo_url
        ])

    return "\n".join(lines)


def main():
    target_id = None
    output_to_gh_summary = "--github-summary" in sys.argv

    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
    if args:
        target_id = args[0].strip().upper()
        if target_id == "ALL":
            target_id = None

    # Discover all projects
    project_dirs = sorted([d for d in PROJECTS_DIR.iterdir() if d.is_dir() and d.name.startswith("LAB-")])
    parsed_projects = []

    for pdir in project_dirs:
        status_file = pdir / "STATUS.md"
        data = parse_status_file(status_file)
        if data:
            parsed_projects.append(data)

    if not parsed_projects:
        print("No active projects found with STATUS.md.", file=sys.stderr)
        sys.exit(1)

    if target_id:
        match = next((p for p in parsed_projects if p.get("id", "").upper() == target_id), None)
        if not match:
            print(f"Error: Project ID '{target_id}' not found.", file=sys.stderr)
            sys.exit(1)
        output = format_single_project(match)
    else:
        output = format_portfolio_digest(parsed_projects)

    print(output)

    # If requested or in GitHub Actions, write to GITHUB_STEP_SUMMARY
    gh_summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if output_to_gh_summary and gh_summary_file:
        with open(gh_summary_file, "a", encoding="utf-8") as f:
            f.write("### 📱 WhatsApp Executive Status Broadcast\n\n")
            f.write("```text\n")
            f.write(output)
            f.write("\n```\n")


if __name__ == "__main__":
    main()
