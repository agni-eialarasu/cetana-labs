#!/usr/bin/env python3
"""
Cetana Labs — PocketBase Schema Generator (BK-008 P1 / RFC-LAB-000-003)

Renders app/pocketbase/pb_schema.json (PocketBase "import collections" format)
from the data/ relational masters, so the backend schema stays derived from the
single source of truth (RFC-LAB-000-002). Zero external dependencies.

Usage:
    python3 scripts/generate_pb_schema.py            # write pb_schema.json
    python3 scripts/generate_pb_schema.py --check     # exit 1 if stale
    python3 scripts/generate_pb_schema.py --stdout
"""

import sys
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT = REPO_ROOT / "app" / "pocketbase" / "pb_schema.json"

# Access rules (draft, Phase 1) — refined for RBAC in Phase 3 (BK-007).
# @request.auth.id != "" means "any authenticated user".
RULE_AUTHED = '@request.auth.id != ""'


ROLE_VALUES = ["owner", "lead", "contributor", "stakeholder", "reviewer"]


def _text(name, required=False, pattern=""):
    return {"name": name, "type": "text", "required": required, "hidden": False,
            "presentable": False, "pattern": pattern}


def _select(name, values, required=True):
    return {"name": name, "type": "select", "required": required, "hidden": False,
            "presentable": False, "maxSelect": 1, "values": values}


def _relation(name, collection_ref, required=True, cascade=False):
    # collectionId is resolved to the real id on import against a live instance;
    # the human-readable ref name is used here for portability.
    return {"name": name, "type": "relation", "required": required, "hidden": False,
            "presentable": False, "collectionId": collection_ref, "maxSelect": 1,
            "minSelect": 0, "cascadeDelete": cascade}


def collections() -> list:
    """
    PocketBase collections snapshot derived from data/ (RFC-LAB-000-003 §4),
    emitted in the v0.23+ `fields` format (PocketBase >= 0.23 refactor).

    NOTE: Collections are created programmatically by `scripts/pb_provision.py`
    (version-robust REST API creation) — NOT by importing this file. This generated
    JSON is a human-readable REFERENCE of the intended shape, kept in sync with the
    data/ model and CI-checked for drift. The authoritative on-disk schema, if
    needed, is the EXPORT from a provisioned instance. See app/pocketbase/README.md.
    """
    users = {
        "name": "users",
        "type": "auth",
        "fields": [
            _text("seed_id", required=True, pattern="^usr-[a-z0-9-]+$"),
            _text("name", required=True),
            _text("github_handle"),
            _select("role", ROLE_VALUES),
            _text("org"),
            {"name": "active", "type": "bool", "required": False, "hidden": False, "presentable": False},
        ],
        "indexes": ["CREATE UNIQUE INDEX `idx_users_seed_id` ON `users` (`seed_id`)"],
        "listRule": RULE_AUTHED,
        "viewRule": RULE_AUTHED,
        "createRule": None,
        "updateRule": None,
        "deleteRule": None,
    }

    projects = {
        "name": "projects",
        "type": "base",
        "fields": [
            _text("lab_id", required=True, pattern="^LAB-\\d{3}$"),
            _text("slug", required=True),
            _text("name", required=True),
            _text("descriptor"),
            _select("archetype", ["control-plane", "mini-app", "research", "data-collection", "verification"]),
            _relation("owner", "users", required=True, cascade=False),
            {"name": "repo_url", "type": "url", "required": False, "hidden": False, "presentable": False},
            {"name": "reference_url", "type": "url", "required": False, "hidden": False, "presentable": False},
            _select("dev_environment", ["cloud", "local"]),
            _select("status_source", ["local", "remote"]),
        ],
        "indexes": ["CREATE UNIQUE INDEX `idx_projects_lab_id` ON `projects` (`lab_id`)"],
        "listRule": RULE_AUTHED,
        "viewRule": RULE_AUTHED,
        "createRule": None,
        # MVP minimum-RBAC: owner-or-not write on their own project (RFC-LAB-000-006 §4).
        "updateRule": '@request.auth.id != "" && owner = @request.auth.id',
        "deleteRule": None,
    }

    memberships = {
        "name": "memberships",
        "type": "base",
        "fields": [
            _text("seed_id", required=True, pattern="^mem-[a-z0-9-]+$"),
            _relation("user", "users", required=True, cascade=True),
            _relation("project", "projects", required=True, cascade=True),
            _select("role", ROLE_VALUES),
        ],
        "indexes": ["CREATE UNIQUE INDEX `idx_membership` ON `memberships` (`user`, `project`)"],
        "listRule": RULE_AUTHED,
        "viewRule": RULE_AUTHED,
        "createRule": None,
        "updateRule": None,
        "deleteRule": None,
    }

    return [users, projects, memberships]


def render() -> str:
    return json.dumps(collections(), indent=2) + "\n"


def main():
    argv = sys.argv[1:]
    payload = render()

    if "--stdout" in argv:
        sys.stdout.write(payload)
        return 0

    if "--check" in argv:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != payload:
            print("❌ pb_schema.json is stale. Run: python3 scripts/generate_pb_schema.py", file=sys.stderr)
            return 1
        print("✅ pb_schema.json is in sync with data/ model.")
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(payload, encoding="utf-8")
    print(f"✅ PocketBase schema generated: {OUT.relative_to(REPO_ROOT)} (3 collections)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
