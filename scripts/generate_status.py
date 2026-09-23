#!/usr/bin/env python3
"""
Cetana Labs — On-Demand Executive Status Generator
Parses authoritative STATUS.md files across projects and generates
mobile-scannable, WhatsApp-compatible text broadcasts for leadership.

Filters:
- Portfolio digest: Reports only active, non-completed product engineering initiatives.
  (Excludes completed projects and LAB-000 control hub kernel by default).
- Single project lookup: Reports any project by ID (e.g. LAB-000, LAB-001, etc.).
- Remote sync: Optional --sync-remote to pull latest STATUS.md from GitHub repositories.
- Soft pressure: Flags pending onboarding and stale statuses (> 14 days).
"""

import sys
import os
import re
import base64
import subprocess
import urllib.request
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECTS_DIR = REPO_ROOT / "projects"
STALE_DAYS_THRESHOLD = 14
SYSTEM_CONTROL_PLANE_ID = "LAB-000"


def fetch_remote_status(repo_url: str) -> str:
    """Attempts to fetch remote STATUS.md from a GitHub repository."""
    match = re.search(r"github\.com/([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+)", repo_url)
    if not match:
        return ""
    org, repo = match.group(1), match.group(2).rstrip(".git")

    # 1. Try using GitHub CLI (gh)
    try:
        cmd = ["gh", "api", f"repos/{org}/{repo}/contents/STATUS.md", "--jq", ".content"]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if res.returncode == 0 and res.stdout.strip():
            return base64.b64decode(res.stdout.strip()).decode("utf-8")
    except Exception:
        pass

    # 2. Fallback to urllib with raw.githubusercontent.com
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    headers = {"User-Agent": "Cetana-Labs-Sync/1.0"}
    if token:
        headers["Authorization"] = f"token {token}"

    for branch in ["main", "master"]:
        raw_url = f"https://raw.githubusercontent.com/{org}/{repo}/{branch}/STATUS.md"
        try:
            req = urllib.request.Request(raw_url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    return response.read().decode("utf-8")
        except Exception:
            continue

    return ""


def parse_status_content(content: str, readme_content: str = "") -> dict:
    """Parses raw text content of a STATUS.md file into structured fields."""
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
        "repo_url": "",
        "days_ago": 0,
        "is_onboarding_pending": False,
        "is_completed": False,
        "is_stale": False
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

    health_lower = data["health"].lower()
    if "completed" in health_lower:
        data["is_completed"] = True
    if "onboarding pending" in health_lower or "pending onboarding" in health_lower or "pending setup" in health_lower:
        data["is_onboarding_pending"] = True

    # Calculate days since last update
    if data["last_updated"]:
        try:
            up_dt = datetime.strptime(data["last_updated"], "%Y-%m-%d")
            data["days_ago"] = max(0, (datetime.now() - up_dt).days)
            if data["days_ago"] > STALE_DAYS_THRESHOLD and not data["is_completed"]:
                data["is_stale"] = True
        except ValueError:
            pass

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

    # Check companion README.md content for remote URL
    if readme_content:
        url_match = re.search(r"\[(?:GitHub Repo|Remote Repository|Repo)\]\((https://github\.com/[^)]+)\)", readme_content)
        if url_match:
            data["repo_url"] = url_match.group(1).strip()
        else:
            url_match2 = re.search(r"https://github\.com/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+", readme_content)
            if url_match2:
                data["repo_url"] = url_match2.group(0).strip().rstrip(".)")

    return data


def parse_status_file(status_path: Path, sync_remote: bool = False) -> dict:
    """Parses a STATUS.md file, optionally pulling latest from GitHub remote."""
    if not status_path.exists():
        return {}

    content = status_path.read_text(encoding="utf-8")
    readme_path = status_path.parent / "README.md"
    readme_content = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

    data = parse_status_content(content, readme_content)

    if sync_remote and data.get("repo_url"):
        remote_status = fetch_remote_status(data["repo_url"])
        if remote_status and len(remote_status.strip()) > 50:
            # Overwrite local cache if valid remote status was found
            try:
                status_path.write_text(remote_status, encoding="utf-8")
                data = parse_status_content(remote_status, readme_content)
            except Exception:
                pass

    return data


def format_portfolio_digest(projects: list) -> str:
    """Formats active, non-completed projects into an executive WhatsApp portfolio digest."""
    now_str = datetime.now().strftime("%d-%b-%Y")
    lines = [
        "📊 *CETANA LABS — EXECUTIVE PORTFOLIO STATUS*",
        f"_Date: {now_str} | Audience: Management Team_",
        ""
    ]

    active_projects = [
        p for p in projects
        if p.get("id", "").upper() != SYSTEM_CONTROL_PLANE_ID and not p.get("is_completed", False)
    ]
    completed_count = sum(1 for p in projects if p.get("is_completed", False))

    hard_blockers = 0
    pending_onboarding = 0

    for p in active_projects:
        lines.append("━━━━━━━━━━━━━━━━━━━━━")
        health = p.get("health", "🟢 On Track")
        pid = p.get("id", "LAB-???")
        name = p.get("name", "Unnamed Project")
        lead = p.get("lead", "Engineering Team")
        pitch = p.get("pitch", "")
        repo_url = p.get("repo_url")
        is_pending = p.get("is_onboarding_pending", False)
        is_stale = p.get("is_stale", False)
        days_ago = p.get("days_ago", 0)

        lines.append(f"{health} *{pid}: {name}*")
        lines.append(f"• *Lead:* {lead}")
        if pitch:
            lines.append(f"• *Pitch:* {pitch}")

        if is_pending:
            pending_onboarding += 1
            lines.append("• *Status Alert:* ⚠️ _Initial onboarding protocol pending from project lead._")
            lines.append("• *Action Required:* Run `/status-init` in repo root to establish sprint baseline.")
        else:
            wins = p.get("wins", [])
            if wins:
                first_win = re.sub(r"\*\*([^*]+)\*\*", r"*\1*", wins[0])
                lines.append(f"• *Latest Win:* {first_win}")

            focus = p.get("focus", "")
            if focus:
                lines.append(f"• *Current Focus:* {focus}")

            blockers = p.get("blockers", "None")
            if "block" in blockers.lower() and "none" not in blockers.lower():
                hard_blockers += 1
            lines.append(f"• *Blockers:* {blockers}")

            if is_stale:
                lines.append(f"• *Cadence Notice:* ℹ️ _Last updated {days_ago} days ago. Awaiting sprint closeout (/status-update)._")

        if repo_url:
            lines.append(f"🔗 {repo_url}")
        lines.append("")

    lines.append("━━━━━━━━━━━━━━━━━━━━━")
    summary_parts = [f"Active Initiatives: {len(active_projects)}"]
    if hard_blockers > 0:
        summary_parts.append(f"⚠️ Hard Blockers: {hard_blockers}")
    else:
        summary_parts.append("Hard Blockers: 0")
    if pending_onboarding > 0:
        summary_parts.append(f"⏳ Pending Setup: {pending_onboarding}")
    if completed_count > 0:
        summary_parts.append(f"✅ Completed: {completed_count}")

    lines.append(f"_{' | '.join(summary_parts)}_")
    return "\n".join(lines)


def format_single_project(p: dict) -> str:
    """Formats a single project into an executive WhatsApp deep-dive briefing."""
    now_str = datetime.now().strftime("%d-%b-%Y")
    pid = p.get("id", "LAB-???")
    name = p.get("name", "Unnamed Project")
    lead = p.get("lead", "Engineering Team")
    health = p.get("health", "🟢 On Track")
    is_pending = p.get("is_onboarding_pending", False)
    is_stale = p.get("is_stale", False)
    days_ago = p.get("days_ago", 0)

    lines = [
        f"🚀 *PROJECT STATUS BRIEFING: {name} ({pid})*",
        f"_Lead: {lead} | Date: {now_str}_",
        f"_Health: {health}_",
        "",
        "━━━━━━━━━━━━━━━━━━━━━",
        "📌 *BUSINESS VALUE & PURPOSE*",
        p.get("pitch", "Deterministic engineering initiative."),
        ""
    ]

    if is_pending:
        lines.extend([
            "⚠️ *ONBOARDING PROTOCOL PENDING*",
            "• *Status:* Project has been registered in the Cetana Labs portfolio, but the initial status baseline (`STATUS.md`) has not yet been committed to the project codebase.",
            "• *Lead Action Required:* Open the project repository and run `/status-init` (or commit `STATUS.md`) to establish quality metrics, sprint deliverables, and verified health.",
            ""
        ])
    else:
        lines.append("🌟 *LATEST DELIVERIES & WINS*")
        for win in p.get("wins", []):
            cleaned_win = re.sub(r"\*\*([^*]+)\*\*", r"*\1*", win)
            lines.append(f"• {cleaned_win}")

        lines.extend([
            "",
            "🎯 *CURRENT FOCUS & NEXT MILESTONE*",
            f"• {p.get('focus', 'Active sprint execution.')}"
        ])

        if is_stale:
            lines.append(f"• ℹ️ *Cadence Notice:* Last updated {days_ago} days ago. Run `/status-update` at sprint closeout.")

        lines.extend([
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
    sync_remote = "--sync-remote" in sys.argv

    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
    if args:
        target_id = args[0].strip().upper()
        if target_id == "ALL":
            target_id = None

    project_dirs = sorted([d for d in PROJECTS_DIR.iterdir() if d.is_dir() and d.name.startswith("LAB-")])
    parsed_projects = []

    for pdir in project_dirs:
        status_file = pdir / "STATUS.md"
        data = parse_status_file(status_file, sync_remote=sync_remote)
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

    gh_summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if output_to_gh_summary and gh_summary_file:
        with open(gh_summary_file, "a", encoding="utf-8") as f:
            f.write("### 📱 WhatsApp Executive Status Broadcast\n\n")
            f.write("```text\n")
            f.write(output)
            f.write("\n```\n")


if __name__ == "__main__":
    main()
