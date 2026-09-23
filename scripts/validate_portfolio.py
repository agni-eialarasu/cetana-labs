#!/usr/bin/env python3
"""
Cetana Labs — Portfolio & Protocol Integrity Validator
Validates structural integrity, naming conventions, STATUS.md protocol conformance,
and master README synchronization across all lab initiatives.
"""

import sys
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECTS_DIR = REPO_ROOT / "projects"
MASTER_README = REPO_ROOT / "README.md"

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
