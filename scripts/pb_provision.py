#!/usr/bin/env python3
"""
Cetana Labs — PocketBase Collection Provisioner (BK-008 / RFC-LAB-000-003)

Creates the `users` / `projects` / `memberships` collections in a running
PocketBase (v0.23+) instance via the REST API — the version-robust alternative
to importing a hand-written schema JSON (which is fragile across versions).

Relations are resolved to REAL collection ids at create time, in dependency
order: users -> projects (owner->users) -> memberships (user->users, project->projects).
Idempotent: existing collections are updated in place (or skipped) rather than
duplicated. Zero external dependencies (stdlib urllib).

Config via env:
    PB_URL            (default http://127.0.0.1:8090)
    PB_ADMIN_EMAIL
    PB_ADMIN_PASSWORD

Usage:
    python3 scripts/pb_provision.py            # dry-run: show the create plan
    python3 scripts/pb_provision.py --apply     # create/update collections
"""

import os
import sys
import json
import urllib.request
import urllib.error

PB_URL = os.environ.get("PB_URL", "http://127.0.0.1:8090").rstrip("/")
PB_ADMIN_EMAIL = os.environ.get("PB_ADMIN_EMAIL", "")
PB_ADMIN_PASSWORD = os.environ.get("PB_ADMIN_PASSWORD", "")

RULE_AUTHED = '@request.auth.id != ""'
ROLE_VALUES = ["owner", "lead", "contributor", "stakeholder", "reviewer"]


# ---- field builders (v0.23+ `fields` format) ----
def f_text(name, required=False, pattern=""):
    return {"name": name, "type": "text", "required": required, "pattern": pattern}


def f_select(name, values, required=True):
    return {"name": name, "type": "select", "required": required, "maxSelect": 1, "values": values}


def f_bool(name):
    return {"name": name, "type": "bool", "required": False}


def f_url(name):
    return {"name": name, "type": "url", "required": False}


def f_relation(name, collection_id, required=True, cascade=False):
    return {"name": name, "type": "relation", "required": required,
            "collectionId": collection_id, "maxSelect": 1, "cascadeDelete": cascade}


def _req(method, path, token=None, body=None):
    url = f"{PB_URL}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", token)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")
    except urllib.error.URLError as e:
        raise SystemExit(f"ERROR: cannot reach PocketBase at {PB_URL} ({e}). Is it running?")


def authenticate():
    status, resp = _req("POST", "/api/collections/_superusers/auth-with-password",
                        body={"identity": PB_ADMIN_EMAIL, "password": PB_ADMIN_PASSWORD})
    if status != 200 or "token" not in resp:
        raise SystemExit(f"ERROR: superuser auth failed (status {status}): {resp}")
    return resp["token"]


def get_collection(token, name):
    status, resp = _req("GET", f"/api/collections/{name}", token=token)
    return resp if status == 200 else None


def upsert_collection(token, spec, dry_run):
    """Create the collection, or update its fields if it already exists. Returns its id."""
    name = spec["name"]
    existing = None if dry_run else get_collection(token, name)

    if dry_run:
        fields = [f["name"] for f in spec["fields"]]
        print(f"  [dry-run] ensure collection '{name}' ({spec['type']}) fields={fields}")
        return f"<{name}:id>"

    if existing:
        # Merge our custom fields into the existing collection (preserve system fields).
        existing_names = {f.get("name") for f in existing.get("fields", [])}
        merged = list(existing.get("fields", []))
        for fld in spec["fields"]:
            if fld["name"] not in existing_names:
                merged.append(fld)
        body = {"fields": merged,
                "listRule": spec.get("listRule"), "viewRule": spec.get("viewRule"),
                "createRule": spec.get("createRule"), "updateRule": spec.get("updateRule"),
                "deleteRule": spec.get("deleteRule")}
        if spec.get("indexes"):
            body["indexes"] = spec["indexes"]
        status, resp = _req("PATCH", f"/api/collections/{existing['id']}", token=token, body=body)
        if status != 200:
            raise SystemExit(f"ERROR: update collection '{name}' failed ({status}): {resp}")
        print(f"  updated  '{name}' (id {resp['id']})")
        return resp["id"]

    status, resp = _req("POST", "/api/collections", token=token, body=spec)
    if status not in (200, 201):
        raise SystemExit(f"ERROR: create collection '{name}' failed ({status}): {resp}")
    print(f"  created  '{name}' (id {resp['id']})")
    return resp["id"]


def run(dry_run=True):
    token = None if dry_run else authenticate()

    print(f"→ Provisioning collections on {PB_URL}")

    # 1. users (auth) — custom fields only; system auth fields are automatic.
    users_spec = {
        "name": "users", "type": "auth",
        "fields": [
            f_text("seed_id", required=True, pattern="^usr-[a-z0-9-]+$"),
            f_text("name", required=True),
            f_text("github_handle"),
            f_select("role", ROLE_VALUES),
            f_text("org"),
            f_bool("active"),
        ],
        # NOTE: `users` is PocketBase's pre-existing default auth collection. We EXTEND
        # it with custom fields; `seed_id` is a plain matching field (NO unique index —
        # forcing one on a pre-populated system collection fails). Upsert keys on seed_id
        # via a filter query (see pb_import.py), and email uniqueness is enforced natively.
        "indexes": [],
        "listRule": RULE_AUTHED, "viewRule": RULE_AUTHED,
        "createRule": None, "updateRule": None, "deleteRule": None,
    }
    users_id = upsert_collection(token, users_spec, dry_run)

    # 2. projects (base) — owner -> users (real id).
    projects_spec = {
        "name": "projects", "type": "base",
        "fields": [
            f_text("lab_id", required=True, pattern="^LAB-\\d{3}$"),
            f_text("slug", required=True),
            f_text("name", required=True),
            f_text("descriptor"),
            f_select("archetype", ["control-plane", "mini-app", "research", "data-collection", "verification"]),
            f_relation("owner", users_id, required=True, cascade=False),
            f_url("repo_url"),
            f_url("reference_url"),
            f_select("dev_environment", ["cloud", "local"]),
            f_select("status_source", ["local", "remote"]),
        ],
        "indexes": ["CREATE UNIQUE INDEX `idx_projects_lab_id` ON `projects` (`lab_id`)"],
        "listRule": RULE_AUTHED, "viewRule": RULE_AUTHED,
        "createRule": None,
        # MVP minimum-RBAC: owner-or-not write on their own project (RFC-LAB-000-006 §4).
        "updateRule": '@request.auth.id != "" && owner = @request.auth.id',
        "deleteRule": None,
    }
    projects_id = upsert_collection(token, projects_spec, dry_run)

    # 3. memberships (base) — user -> users, project -> projects (real ids).
    memberships_spec = {
        "name": "memberships", "type": "base",
        "fields": [
            f_text("seed_id", required=True, pattern="^mem-[a-z0-9-]+$"),
            f_relation("user", users_id, required=True, cascade=True),
            f_relation("project", projects_id, required=True, cascade=True),
            f_select("role", ROLE_VALUES),
        ],
        "indexes": ["CREATE UNIQUE INDEX `idx_membership` ON `memberships` (`user`, `project`)"],
        "listRule": RULE_AUTHED, "viewRule": RULE_AUTHED,
        "createRule": None, "updateRule": None, "deleteRule": None,
    }
    upsert_collection(token, memberships_spec, dry_run)

    print("✅ Provision plan complete." if dry_run else "✅ Collections provisioned.")
    return 0


def main():
    dry_run = "--apply" not in sys.argv[1:]
    if not dry_run and not (PB_ADMIN_EMAIL and PB_ADMIN_PASSWORD):
        raise SystemExit("ERROR: --apply requires PB_ADMIN_EMAIL and PB_ADMIN_PASSWORD.")
    if dry_run:
        print("DRY-RUN (no changes). Pass --apply with PB_ADMIN_* env to create.\n")
    return run(dry_run=dry_run)


if __name__ == "__main__":
    sys.exit(main())
