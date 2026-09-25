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


def collections() -> list:
    """PocketBase collections import payload derived from data/ (RFC-LAB-000-003 §4)."""
    users = {
        "name": "users",
        "type": "auth",
        "schema": [
            {"name": "seed_id", "type": "text", "required": True, "options": {"pattern": "^usr-[a-z0-9-]+$"}},
            {"name": "name", "type": "text", "required": True},
            {"name": "github_handle", "type": "text", "required": False},
            {"name": "role", "type": "select", "required": True,
             "options": {"maxSelect": 1, "values": ["owner", "lead", "contributor", "stakeholder", "reviewer"]}},
            {"name": "org", "type": "text", "required": False},
            {"name": "active", "type": "bool", "required": False},
        ],
        "indexes": ["CREATE UNIQUE INDEX idx_users_seed_id ON users (seed_id)"],
        # email/password + auth fields are provided by the auth collection type.
        "listRule": RULE_AUTHED,
        "viewRule": RULE_AUTHED,
        "createRule": None,   # superuser only
        "updateRule": None,   # superuser only (self-update refined in Phase 3)
        "deleteRule": None,
    }

    projects = {
        "name": "projects",
        "type": "base",
        "schema": [
            {"name": "lab_id", "type": "text", "required": True, "options": {"pattern": "^LAB-\\d{3}$"}},
            {"name": "slug", "type": "text", "required": True},
            {"name": "name", "type": "text", "required": True},
            {"name": "descriptor", "type": "text", "required": False},
            {"name": "archetype", "type": "select", "required": True,
             "options": {"maxSelect": 1, "values": ["control-plane", "mini-app", "research", "data-collection", "verification"]}},
            {"name": "owner", "type": "relation", "required": True,
             "options": {"collectionId": "users", "maxSelect": 1, "cascadeDelete": False}},
            {"name": "repo_url", "type": "url", "required": False},
            {"name": "reference_url", "type": "url", "required": False},
            {"name": "dev_environment", "type": "select", "required": True,
             "options": {"maxSelect": 1, "values": ["cloud", "local"]}},
            {"name": "status_source", "type": "select", "required": True,
             "options": {"maxSelect": 1, "values": ["local", "remote"]}},
        ],
        "indexes": ["CREATE UNIQUE INDEX idx_projects_lab_id ON projects (lab_id)"],
        "listRule": RULE_AUTHED,
        "viewRule": RULE_AUTHED,
        # Draft: owner or superuser writes. Refined in Phase 3 via memberships.
        "createRule": None,
        "updateRule": '@request.auth.id != "" && owner = @request.auth.id',
        "deleteRule": None,
    }

    memberships = {
        "name": "memberships",
        "type": "base",
        "schema": [
            {"name": "seed_id", "type": "text", "required": True, "options": {"pattern": "^mem-[a-z0-9-]+$"}},
            {"name": "user", "type": "relation", "required": True,
             "options": {"collectionId": "users", "maxSelect": 1, "cascadeDelete": True}},
            {"name": "project", "type": "relation", "required": True,
             "options": {"collectionId": "projects", "maxSelect": 1, "cascadeDelete": True}},
            {"name": "role", "type": "select", "required": True,
             "options": {"maxSelect": 1, "values": ["owner", "lead", "contributor", "stakeholder", "reviewer"]}},
        ],
        "indexes": ["CREATE UNIQUE INDEX idx_membership ON memberships (user, project)"],
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
