#!/usr/bin/env python3
"""
Cetana Labs — Automated Lead Ping Engine (BK-003 / TSK-024)

Scans authoritative STATUS.md files across the portfolio and generates lead
"ping" alerts for initiatives needing attention:

  1. STALE:      An active (non-completed) project whose `Last Updated` date is
                 older than the staleness threshold (> 14 days).
  2. ONBOARDING: A project still in `⏳ Onboarding Pending` that has not
                 committed its initial STATUS.md baseline.

Filtering (mirrors the executive portfolio digest):
  - EXCLUDES the LAB-000 control-hub kernel.
  - EXCLUDES completed initiatives (✅ Completed).

Alert delivery modes:
  --dry-run        (default) Print a human-readable report; make no changes.
  --json           Emit a machine-readable JSON payload of pending pings.
  --create-issues  Open (or update) idempotent GitHub issues on the project's
                   own repository via the `gh` CLI. Falls back to a control-hub
                   tracking issue if the sub-project repo is unavailable.

Idempotency:
  Each ping issue carries a stable marker in its title:
      "[Cetana Ping] <LAB-ID>: ..."
  Before creating, the engine searches for an existing OPEN issue with that
  marker. If found, it refreshes it with a comment instead of duplicating.

Zero external dependencies. Reuses the STATUS.md parser from generate_status.py.
"""

import sys
import os
import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECTS_DIR = REPO_ROOT / "projects"
STALE_DAYS_THRESHOLD = 14
SYSTEM_CONTROL_PLANE_ID = "LAB-000"
CONTROL_HUB_REPO = "agni-eialarasu/cetana-labs"
PING_TITLE_MARKER = "[Cetana Ping]"

# Reuse the authoritative STATUS.md parser to avoid logic drift.
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from generate_status import parse_status_file  # noqa: E402


def collect_pending_pings(sync_remote: bool = False) -> list:
    """Scan the portfolio and return the list of projects needing a lead ping."""
    project_dirs = sorted(
        d for d in PROJECTS_DIR.iterdir()
        if d.is_dir() and d.name.startswith("LAB-")
    )

    pings = []
    for pdir in project_dirs:
        data = parse_status_file(pdir / "STATUS.md", sync_remote=sync_remote)
        if not data:
            continue

        pid = data.get("id", "").upper()

        # Exclusions: control-hub kernel and completed initiatives.
        if pid == SYSTEM_CONTROL_PLANE_ID:
            continue
        if data.get("is_completed", False):
            continue

        reasons = []
        if data.get("is_onboarding_pending", False):
            reasons.append("onboarding_pending")
        # Onboarding-pending projects are not additionally flagged as stale;
        # the onboarding CTA takes precedence.
        elif data.get("is_stale", False):
            reasons.append("stale")

        if not reasons:
            continue

        pings.append({
            "id": pid,
            "name": data.get("name", "Unnamed Project"),
            "lead": data.get("lead", "Engineering Team"),
            "health": data.get("health", ""),
            "last_updated": data.get("last_updated", ""),
            "days_ago": data.get("days_ago", 0),
            "repo_url": data.get("repo_url", ""),
            "reasons": reasons,
        })

    return pings


def _repo_slug(repo_url: str) -> str:
    """Extract 'org/repo' from a GitHub URL, or '' if not parseable."""
    if not repo_url:
        return ""
    import re
    m = re.search(r"github\.com/([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+)", repo_url)
    if not m:
        return ""
    repo = m.group(2)
    if repo.endswith(".git"):
        repo = repo[:-len(".git")]
    return f"{m.group(1)}/{repo}"


def build_issue_payload(ping: dict) -> dict:
    """Construct the title and body for a lead ping issue."""
    pid = ping["id"]
    name = ping["name"]
    lead = ping["lead"]

    if "onboarding_pending" in ping["reasons"]:
        title = f"{PING_TITLE_MARKER} {pid}: Initial STATUS.md onboarding pending"
        body = (
            f"## ⏳ Onboarding Protocol Pending — {pid}: {name}\n\n"
            f"**Lead:** {lead}\n"
            f"**Current Health:** {ping['health']}\n"
            f"**Last Updated:** {ping['last_updated'] or 'n/a'}\n\n"
            "This initiative is registered in the Cetana Labs portfolio but has not "
            "yet committed its initial executive `STATUS.md` baseline.\n\n"
            "### Action Required\n"
            "Run `/status-init` in the project repository root (or commit a "
            "`STATUS.md` conforming to the "
            "[Project Protocol](https://github.com/agni-eialarasu/cetana-labs/blob/main/docs/project-protocol.md)) "
            "to establish the sprint baseline, quality metrics, and verified health.\n\n"
            "---\n"
            "_Automated by the Cetana Labs Lead Ping Engine (`BK-003`). "
            "This issue auto-refreshes; close it once the baseline is committed._"
        )
    else:  # stale
        title = f"{PING_TITLE_MARKER} {pid}: STATUS.md stale ({ping['days_ago']} days)"
        body = (
            f"## ℹ️ Sprint Cadence Notice — {pid}: {name}\n\n"
            f"**Lead:** {lead}\n"
            f"**Current Health:** {ping['health']}\n"
            f"**Last Updated:** {ping['last_updated']} "
            f"(**{ping['days_ago']} days ago**, threshold {STALE_DAYS_THRESHOLD} days)\n\n"
            "The executive `STATUS.md` for this initiative has not been updated within "
            "the expected bi-weekly sprint cadence.\n\n"
            "### Action Required\n"
            "Run `/status-update` at sprint closeout to refresh the latest wins, current "
            "focus, blockers, and `Last Updated` date.\n\n"
            "---\n"
            "_Automated by the Cetana Labs Lead Ping Engine (`BK-003`). "
            "This issue auto-refreshes; close it once the status is refreshed._"
        )

    return {"title": title, "body": body}


def _gh(args: list, timeout: int = 15):
    """Run a gh CLI command, returning (returncode, stdout, stderr)."""
    try:
        res = subprocess.run(
            ["gh"] + args, capture_output=True, text=True, timeout=timeout
        )
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except FileNotFoundError:
        return 127, "", "gh CLI not found"
    except Exception as exc:  # pragma: no cover - defensive
        return 1, "", str(exc)


def find_existing_issue(repo: str, title: str) -> int:
    """Return the number of an existing OPEN ping issue with this title, or 0."""
    marker = title.split(":")[0]  # "[Cetana Ping] LAB-XXX"
    rc, out, _ = _gh([
        "issue", "list", "--repo", repo, "--state", "open",
        "--search", marker, "--json", "number,title", "--limit", "50",
    ])
    if rc != 0 or not out:
        return 0
    try:
        for issue in json.loads(out):
            if issue.get("title", "").startswith(marker):
                return int(issue.get("number", 0))
    except (json.JSONDecodeError, ValueError):
        return 0
    return 0


def dispatch_issue(ping: dict) -> dict:
    """Create or refresh an idempotent GitHub issue for a ping. Returns result."""
    payload = build_issue_payload(ping)
    repo = _repo_slug(ping.get("repo_url", "")) or CONTROL_HUB_REPO
    routed_to_hub = repo == CONTROL_HUB_REPO and not _repo_slug(ping.get("repo_url", ""))

    existing = find_existing_issue(repo, payload["title"])
    if existing:
        note = (
            f"🔁 _Still pending as of this scan — {ping['id']} "
            f"({', '.join(ping['reasons'])})._"
        )
        rc, out, err = _gh([
            "issue", "comment", str(existing), "--repo", repo, "--body", note
        ])
        return {
            "id": ping["id"], "repo": repo, "action": "refreshed",
            "issue": existing, "ok": rc == 0, "error": err if rc else "",
            "routed_to_hub": routed_to_hub,
        }

    rc, out, err = _gh([
        "issue", "create", "--repo", repo,
        "--title", payload["title"], "--body", payload["body"],
    ])
    return {
        "id": ping["id"], "repo": repo, "action": "created",
        "url": out if rc == 0 else "", "ok": rc == 0,
        "error": err if rc else "", "routed_to_hub": routed_to_hub,
    }


def format_report(pings: list) -> str:
    """Human-readable dry-run report."""
    if not pings:
        return (
            "✅ Cetana Labs Lead Ping Engine — no pending pings.\n"
            "   All active initiatives are within cadence and onboarded "
            f"(LAB-000 and completed projects excluded)."
        )
    lines = [
        "🔔 Cetana Labs Lead Ping Engine — Pending Alerts",
        f"   {len(pings)} initiative(s) need attention "
        f"(LAB-000 & completed excluded).",
        "",
    ]
    for p in pings:
        reason = "⏳ Onboarding pending" if "onboarding_pending" in p["reasons"] \
            else f"ℹ️ Stale ({p['days_ago']} days)"
        target = _repo_slug(p.get("repo_url", "")) or f"{CONTROL_HUB_REPO} (hub fallback)"
        lines.append(f"• {p['id']}: {p['name']}")
        lines.append(f"    Reason: {reason}")
        lines.append(f"    Lead:   {p['lead']}")
        lines.append(f"    Target: {target}")
        lines.append("")
    return "\n".join(lines).rstrip()


def main():
    argv = sys.argv[1:]
    as_json = "--json" in argv
    create_issues = "--create-issues" in argv
    sync_remote = "--sync-remote" in argv
    # --dry-run is the implicit default whenever --create-issues is absent.

    pings = collect_pending_pings(sync_remote=sync_remote)

    if create_issues:
        results = [dispatch_issue(p) for p in pings]
        if as_json:
            print(json.dumps({"dispatched": results}, indent=2))
        else:
            if not results:
                print("✅ No pings to dispatch.")
            for r in results:
                status = "OK" if r["ok"] else f"FAILED ({r['error']})"
                extra = " [routed to hub]" if r.get("routed_to_hub") else ""
                loc = r.get("url") or f"#{r.get('issue', '?')}"
                print(f"• {r['id']}: {r['action']} {loc} on {r['repo']} — {status}{extra}")
        # Non-zero exit if any dispatch failed (useful for CI signal).
        if any(not r["ok"] for r in results):
            sys.exit(1)
        return

    if as_json:
        print(json.dumps({"pending_pings": pings}, indent=2))
    else:
        print(format_report(pings))


if __name__ == "__main__":
    main()
