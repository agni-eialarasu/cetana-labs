#!/usr/bin/env python3
"""
Cetana Labs — PocketBase Seed Importer (BK-008 P1 / RFC-LAB-000-003 §8)

Idempotently imports the data/ relational masters into a running PocketBase
instance: users -> projects (owner relation) -> memberships (user/project
relations). Resolves data/ slug IDs to PocketBase record IDs and upserts by a
natural key so re-runs are safe.

Uses only the Python standard library (urllib). Configure via env:
    PB_URL            (default http://127.0.0.1:8090)
    PB_ADMIN_EMAIL
    PB_ADMIN_PASSWORD

Usage:
    python3 scripts/pb_import.py            # dry-run: print planned upserts
    python3 scripts/pb_import.py --apply     # perform the import against PB_URL
"""

import os
import sys
import json
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"

PB_URL = os.environ.get("PB_URL", "http://127.0.0.1:8090").rstrip("/")
PB_ADMIN_EMAIL = os.environ.get("PB_ADMIN_EMAIL", "")
PB_ADMIN_PASSWORD = os.environ.get("PB_ADMIN_PASSWORD", "")


def _load(name):
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


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
        raise SystemExit(f"ERROR: cannot reach PocketBase at {PB_URL} ({e}). Is the server running?")


def authenticate():
    """Superuser auth -> token. (PocketBase _superusers auth-with-password.)"""
    status, resp = _req(
        "POST", "/api/collections/_superusers/auth-with-password",
        body={"identity": PB_ADMIN_EMAIL, "password": PB_ADMIN_PASSWORD},
    )
    if status != 200 or "token" not in resp:
        raise SystemExit(f"ERROR: PocketBase admin auth failed (status {status}): {resp}")
    return resp["token"]


def find_by(token, collection, field, value):
    """Return an existing record (dict) matching field==value, or None."""
    filt = urllib.parse.quote(f'{field}="{value}"')
    status, resp = _req("GET", f"/api/collections/{collection}/records?filter={filt}&perPage=1", token=token)
    items = resp.get("items", []) if status == 200 else []
    return items[0] if items else None


def upsert(token, collection, natural_field, natural_value, payload, dry_run,
           fallback_field=None, fallback_value=None, create_only_keys=None,
           seed_if_empty_keys=None):
    """
    Create or update a record, matching first on `natural_field`, then on an optional
    `fallback_field` (e.g. email) so re-runs UPDATE instead of hitting a unique
    conflict. `create_only_keys` (e.g. password) are sent only on create, never on
    update. `seed_if_empty_keys` (e.g. status_health) are sent on update ONLY when the
    existing record's current value is empty — so an initial seed lands, but a later
    owner edit is never clobbered (R2.3). Idempotent and re-runnable. Returns the record id.
    """
    if dry_run:
        print(f"  [dry-run] upsert {collection} where {natural_field}={natural_value!r}")
        return f"<{collection}:{natural_value}>"

    existing = find_by(token, collection, natural_field, natural_value)
    if not existing and fallback_field and fallback_value:
        existing = find_by(token, collection, fallback_field, fallback_value)

    create_only_keys = create_only_keys or []
    seed_if_empty_keys = seed_if_empty_keys or []

    if existing:
        existing_id = existing["id"]
        skip = set(create_only_keys)
        # Only seed a "seed-if-empty" key when the record currently has no value for it.
        for k in seed_if_empty_keys:
            if existing.get(k):  # already set (e.g. an owner edit) → don't overwrite
                skip.add(k)
        update_payload = {k: v for k, v in payload.items() if k not in skip}
        status, resp = _req("PATCH", f"/api/collections/{collection}/records/{existing_id}",
                            token=token, body=update_payload)
        if status != 200:
            raise SystemExit(f"ERROR: update {collection}/{existing_id} failed ({status}): {resp}")
        return existing_id

    status, resp = _req("POST", f"/api/collections/{collection}/records", token=token, body=payload)
    if status not in (200, 201):
        raise SystemExit(f"ERROR: create {collection} failed (status {status}): {resp}")
    return resp["id"]


def run(dry_run=True):
    users = _load("users.json")
    projects = _load("portfolio.json")
    memberships = _load("memberships.json")
    # M3–M4: seed the owner-editable status_health from the status.json snapshot health
    # where resolvable (RFC-LAB-000-008 §9.1a, R2.3). Keyed by lab_id.
    try:
        status_health_by_id = {s["id"]: s.get("health", "") for s in _load("status.json")}
    except (FileNotFoundError, KeyError):
        status_health_by_id = {}

    token = None if dry_run else authenticate()

    # 1. Users (natural key: the data/ slug id, stored in a 'seed_id' field)
    print(f"→ Importing {len(users)} users")
    user_id_map = {}
    for u in users:
        email = u.get("email") or f'{u["id"]}@cetana.local'
        pw = os.urandom(9).hex() + "A1!"   # meet auth password rules on create
        payload = {
            "seed_id": u["id"], "name": u["name"], "email": email,
            "github_handle": u.get("github_handle") or "", "role": u.get("role", "contributor"),
            "org": u.get("org") or "", "active": bool(u.get("active", True)),
            # password fields are create-only (never re-sent on update).
            "password": pw, "passwordConfirm": pw,
        }
        # Match on seed_id, then fall back to email so re-runs update (no unique conflict).
        user_id_map[u["id"]] = upsert(
            token, "users", "seed_id", u["id"], payload, dry_run,
            fallback_field="email", fallback_value=email,
            create_only_keys=["password", "passwordConfirm"],
        )

    # 2. Projects (owner relation resolved via user_id_map)
    print(f"→ Importing {len(projects)} projects")
    project_id_map = {}
    for p in projects:
        payload = {
            "lab_id": p["id"], "slug": p["slug"], "name": p["name"], "descriptor": p.get("descriptor") or "",
            "archetype": p["archetype"], "owner": user_id_map.get(p["owner_id"]),
            "repo_url": p.get("repo_url") or "", "reference_url": p.get("reference_url") or "",
            "dev_environment": p["dev_environment"], "status_source": p["status_source"],
            # Seed the initial owner-editable health from the snapshot.
            "status_health": status_health_by_id.get(p["id"], ""),
        }
        # status_health is seeded only when currently empty — a later owner edit (M4) is
        # preserved across re-seeds (R2.3 idempotency).
        project_id_map[p["id"]] = upsert(
            token, "projects", "lab_id", p["id"], payload, dry_run,
            seed_if_empty_keys=["status_health"],
        )

    # 3. Memberships (both relations resolved)
    print(f"→ Importing {len(memberships)} memberships")
    for m in memberships:
        payload = {
            "seed_id": m["id"], "user": user_id_map.get(m["user_id"]),
            "project": project_id_map.get(m["project_id"]), "role": m["role"],
        }
        upsert(token, "memberships", "seed_id", m["id"], payload, dry_run)

    # 4. Settings (RFC-LAB-000-013, natural key: 'key')
    settings = _load("settings.json") if (DATA_DIR / "settings.json").exists() else []
    print(f"→ Importing {len(settings)} settings")
    for s in settings:
        payload = {
            "key": s["key"],
            "value": s.get("value", ""),
            "type": s.get("type", "string"),
            "group": s.get("group", ""),
        }
        upsert(token, "settings", "key", s["key"], payload, dry_run)

    print("✅ Import plan complete." if dry_run else "✅ Import applied to PocketBase.")
    return 0


def main():
    dry_run = "--apply" not in sys.argv[1:]
    if not dry_run and not (PB_ADMIN_EMAIL and PB_ADMIN_PASSWORD):
        raise SystemExit("ERROR: --apply requires PB_ADMIN_EMAIL and PB_ADMIN_PASSWORD env vars.")
    if dry_run:
        print("DRY-RUN (no changes). Pass --apply with PB_ADMIN_* env to import.\n")
    return run(dry_run=dry_run)


if __name__ == "__main__":
    sys.exit(main())
