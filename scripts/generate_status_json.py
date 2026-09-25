#!/usr/bin/env python3
"""
Cetana Labs — Live Status JSON Exporter (BK-008 P2 / RFC-LAB-000-005 §9 Q1)

Emits data/status.json: a snapshot of the LIVE status fields (health, wins,
focus, blockers, risks, metrics, last_updated, onboarding/stale flags) parsed
from each project's STATUS.md — the interim read source for the Phase 2 SPA
until STATUS.md migrates into PocketBase (Phase 4).

Reuses the authoritative parser from generate_status.py (no logic drift).
Structural metadata (owner, archetype, repo) stays in data/portfolio.json +
data/users.json; this file carries only the live status layer, keyed by LAB id.

Usage:
    python3 scripts/generate_status_json.py            # write data/status.json
    python3 scripts/generate_status_json.py --check     # exit 1 if stale
    python3 scripts/generate_status_json.py --stdout
"""

import sys
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECTS_DIR = REPO_ROOT / "projects"
OUT = REPO_ROOT / "data" / "status.json"

sys.path.insert(0, str(REPO_ROOT / "scripts"))
from generate_status import parse_status_file  # noqa: E402


def build() -> list:
    records = []
    for pdir in sorted(d for d in PROJECTS_DIR.iterdir() if d.is_dir() and d.name.startswith("LAB-")):
        data = parse_status_file(pdir / "STATUS.md")
        if not data:
            continue
        records.append({
            "id": data.get("id", ""),
            "health": data.get("health", ""),
            "last_updated": data.get("last_updated", ""),
            "pitch": data.get("pitch", ""),
            "wins": data.get("wins", []),
            "focus": data.get("focus", ""),
            "blockers": data.get("blockers", "None"),
            "risks": data.get("risks", ""),
            "metrics": data.get("metrics", []),
            "days_ago": data.get("days_ago", 0),
            "is_onboarding_pending": data.get("is_onboarding_pending", False),
            "is_completed": data.get("is_completed", False),
            "is_stale": data.get("is_stale", False),
        })
    return records


def render() -> str:
    return json.dumps(build(), indent=2, ensure_ascii=False) + "\n"


def main():
    argv = sys.argv[1:]
    payload = render()
    if "--stdout" in argv:
        sys.stdout.write(payload)
        return 0
    if "--check" in argv:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != payload:
            print("❌ data/status.json is stale. Run: python3 scripts/generate_status_json.py", file=sys.stderr)
            return 1
        print("✅ data/status.json is in sync with STATUS.md files.")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(payload, encoding="utf-8")
    print(f"✅ Live status exported: {OUT.relative_to(REPO_ROOT)} ({len(build())} projects)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
