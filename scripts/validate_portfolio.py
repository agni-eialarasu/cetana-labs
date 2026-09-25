#!/usr/bin/env python3
"""
Cetana Labs — Portfolio & Protocol Integrity Validator
Validates structural integrity, naming conventions, STATUS.md protocol conformance,
and master README synchronization across all lab initiatives.
"""

import sys
import re
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECTS_DIR = REPO_ROOT / "projects"
MASTER_README = REPO_ROOT / "README.md"
DATA_DIR = REPO_ROOT / "data"

VALID_HEALTH_BADGES = {
    "🟢 On Track",
    "🟡 At Risk",
    "🔴 Blocked",
    "⏸️ Paused",
    "✅ Completed",
    "⏳ Onboarding Pending"
}

REQUIRED_SECTIONS = [
    r"###\s*1\.\s*Elevator Pitch",
    r"###\s*2\.\s*Latest Deliveries",
    r"###\s*3\.\s*Current Focus",
    r"###\s*4\.\s*Blockers & Risks",
    r"###\s*5\.\s*Verified Quality Metrics"
]


def validate_relational_integrity(errors: list, warnings: list) -> None:
    """
    Referential-integrity pillar for the data/ relational layer
    (BK-009 / RFC-LAB-000-002 §6). No-op if data/ is absent.
    """
    users_file = DATA_DIR / "users.json"
    projects_file = DATA_DIR / "portfolio.json"
    mems_file = DATA_DIR / "memberships.json"

    if not projects_file.exists():
        return  # data/ layer not present; skip relational checks

    # 1. All JSON parses.
    try:
        users = json.loads(users_file.read_text(encoding="utf-8")) if users_file.exists() else []
        projects = json.loads(projects_file.read_text(encoding="utf-8"))
        mems = json.loads(mems_file.read_text(encoding="utf-8")) if mems_file.exists() else []
    except json.JSONDecodeError as e:
        errors.append(f"[data/] JSON parse error: {e}")
        return

    user_ids = {u.get("id") for u in users}
    project_ids = {p.get("id") for p in projects}

    # 2. owner_id resolves to a user.
    for p in projects:
        if p.get("owner_id") not in user_ids:
            errors.append(f"[data/portfolio.json] {p.get('id')} owner_id '{p.get('owner_id')}' does not resolve to a users.json record.")

    # 3. data/ records <-> projects/ directories in strict lockstep.
    dir_names = {d.name for d in PROJECTS_DIR.iterdir() if d.is_dir()}
    expected_dirs = {f"{p.get('id')}-{p.get('slug')}" for p in projects}
    for missing in sorted(expected_dirs - dir_names):
        errors.append(f"[data/portfolio.json] Record '{missing}' has no matching projects/ directory.")
    for orphan in sorted(dir_names - expected_dirs):
        errors.append(f"[projects/{orphan}] Directory has no matching data/portfolio.json record.")

    # 4. Membership FKs resolve; each project has an owner membership matching owner_id.
    owner_mem = {(m.get("project_id"), m.get("user_id")) for m in mems if m.get("role") == "owner"}
    for m in mems:
        if m.get("user_id") not in user_ids:
            errors.append(f"[data/memberships.json] {m.get('id')} user_id '{m.get('user_id')}' does not resolve.")
        if m.get("project_id") not in project_ids:
            errors.append(f"[data/memberships.json] {m.get('id')} project_id '{m.get('project_id')}' does not resolve.")
    for p in projects:
        if (p.get("id"), p.get("owner_id")) not in owner_mem:
            errors.append(f"[data/memberships.json] Missing 'owner' membership for {p.get('id')} / {p.get('owner_id')}.")

    # 5. STATUS.md 'Owner / Lead' matches the resolved owner name (drift detection -> warning).
    users_by_id = {u.get("id"): u for u in users}
    for p in projects:
        status_file = PROJECTS_DIR / f"{p.get('id')}-{p.get('slug')}" / "STATUS.md"
        if not status_file.exists():
            continue
        content = status_file.read_text(encoding="utf-8")
        m = re.search(r"\*\*(?:Owner / Lead|Lead)\*\*\s*\|\s*([^|\n]+)", content)
        if not m:
            continue
        status_lead = m.group(1).strip()
        owner_name = users_by_id.get(p.get("owner_id"), {}).get("name", "")
        if owner_name and status_lead != owner_name:
            warnings.append(
                f"[{p.get('id')}/STATUS.md] Owner/Lead '{status_lead}' differs from users master '{owner_name}' (data/ is authoritative)."
            )


def validate() -> int:
    errors = []
    warnings = []

    if not PROJECTS_DIR.exists():
        print("❌ Error: projects/ directory not found!", file=sys.stderr)
        return 1

    readme_content = MASTER_README.read_text(encoding="utf-8") if MASTER_README.exists() else ""
    project_dirs = sorted([d for d in PROJECTS_DIR.iterdir() if d.is_dir()])

    print(f"🔍 Validating {len(project_dirs)} projects in Cetana Labs...\n")

    for pdir in project_dirs:
        dir_name = pdir.name
        # 1. Folder naming pattern
        if not re.match(r"^LAB-\d{3}-[a-z0-9-]+$", dir_name):
            errors.append(f"[{dir_name}] Invalid directory name. Must match 'LAB-XXX-<slug>' (lowercase, hyphenated).")
            continue

        proj_id = dir_name.split("-")[0] + "-" + dir_name.split("-")[1]

        # 2. Required files
        for req_file in ["README.md", "STATUS.md", "journal.md"]:
            file_path = pdir / req_file
            if not file_path.exists():
                errors.append(f"[{dir_name}] Missing required file: {req_file}")

        # 3. STATUS.md protocol conformance
        status_file = pdir / "STATUS.md"
        if status_file.exists():
            status_text = status_file.read_text(encoding="utf-8")
            lines = status_text.strip().splitlines()

            # Line limit check (strict conciseness rule: <= 45 lines)
            if len(lines) > 45:
                warnings.append(f"[{dir_name}/STATUS.md] Length is {len(lines)} lines (exceeds recommended 35-line limit).")

            # Project ID matching
            id_match = re.search(r"\*\*Project ID\*\*\s*\|\s*([^|\n]+)", status_text)
            if not id_match or id_match.group(1).strip() != proj_id:
                errors.append(f"[{dir_name}/STATUS.md] Project ID header does not match directory ID '{proj_id}'.")

            # Health badge validation
            health_match = re.search(r"\*\*Current Health\*\*\s*\|\s*([^|\n]+)", status_text)
            if not health_match:
                errors.append(f"[{dir_name}/STATUS.md] Missing '**Current Health**' table property.")
            else:
                health_val = health_match.group(1).strip()
                if not any(badge in health_val for badge in VALID_HEALTH_BADGES):
                    errors.append(f"[{dir_name}/STATUS.md] Invalid Health badge '{health_val}'. Must be one of: {', '.join(VALID_HEALTH_BADGES)}")

            # Date format validation
            date_match = re.search(r"\*\*Last Updated\*\*\s*\|\s*([^|\n]+)", status_text)
            if not date_match:
                errors.append(f"[{dir_name}/STATUS.md] Missing '**Last Updated**' table property.")
            elif not re.match(r"^\d{4}-\d{2}-\d{2}$", date_match.group(1).strip()):
                errors.append(f"[{dir_name}/STATUS.md] Last Updated date '{date_match.group(1).strip()}' is not ISO format (YYYY-MM-DD).")

            # Required sections validation
            for sec_regex in REQUIRED_SECTIONS:
                if not re.search(sec_regex, status_text, re.IGNORECASE):
                    errors.append(f"[{dir_name}/STATUS.md] Missing required section matching: {sec_regex}")

        # 4. Master README registration
        if proj_id not in readme_content:
            errors.append(f"[{dir_name}] Not registered in root README.md master table.")

    # 5. Relational data-layer referential integrity (BK-009 / RFC-LAB-000-002)
    validate_relational_integrity(errors, warnings)

    # Print results
    if warnings:
        print("⚠️ Warnings:")
        for w in warnings:
            print(f"  • {w}")
        print()

    if errors:
        print(f"❌ Validation failed with {len(errors)} error(s):", file=sys.stderr)
        for e in errors:
            print(f"  • {e}", file=sys.stderr)
        return 1

    print(f"✅ All {len(project_dirs)} projects passed structural and protocol integrity checks!")
    return 0


if __name__ == "__main__":
    sys.exit(validate())
