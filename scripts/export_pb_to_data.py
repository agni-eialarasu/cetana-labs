#!/usr/bin/env python3
"""
Cetana Labs — PocketBase Data Exporter / Reconciliation Engine (BK-014 / RFC-LAB-000-008 D-CRUD-1)

Reconciles the live PocketBase database back into committed data/*.json masters:
- Reads live `projects` and `users` collections from PocketBase via REST API.
- Resolves PocketBase internal record IDs back to natural slug IDs (seed_id / lab_id).
- Exports data/portfolio.json and data/users.json in committed canonical format.
- Reverse of scripts/pb_import.py.

Usage:
    python3 scripts/export_pb_to_data.py          # Dry-run: shows planned export and diff
    python3 scripts/export_pb_to_data.py --apply  # Applies export to data/*.json
    just export-live-data                         # Via task runner
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

# Auto-read .env if present and environment variables not already set
ENV_FILE = REPO_ROOT / ".env"
if ENV_FILE.exists():
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip().strip("'\"")
        if k not in os.environ:
            os.environ[k] = v

PB_URL = os.environ.get("PB_URL", "http://127.0.0.1:8090").rstrip("/")
PB_ADMIN_EMAIL = os.environ.get("PB_ADMIN_EMAIL", "admin@cetana.local")
PB_ADMIN_PASSWORD = os.environ.get("PB_ADMIN_PASSWORD", "CetanaLocal2026!")


def is_pb_reachable(timeout=1.5):
    """Probe PocketBase health endpoint without throwing fatal errors."""
    url = f"{PB_URL}/api/health"
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status == 200
    except Exception:
        return False


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
    """Authenticate as superuser to access users list and projects."""
    status, resp = _req(
        "POST", "/api/collections/_superusers/auth-with-password",
        body={"identity": PB_ADMIN_EMAIL, "password": PB_ADMIN_PASSWORD}
    )
    if status != 200 or "token" not in resp:
        raise SystemExit(f"ERROR: PocketBase superuser auth failed (status {status}): {resp}")
    return resp["token"]


def get_all_records(token, collection, expand=None):
    records = []
    page = 1
    per_page = 200
    while True:
        expand_param = f"&expand={expand}" if expand else ""
        status, resp = _req("GET", f"/api/collections/{collection}/records?page={page}&perPage={per_page}{expand_param}", token=token)
        if status != 200:
            raise SystemExit(f"ERROR: failed to fetch records from '{collection}' ({status}): {resp}")
        items = resp.get("items", [])
        records.extend(items)
        total_pages = resp.get("totalPages", 1)
        if page >= total_pages or not items:
            break
        page += 1
    return records


def get_export_payloads():
    """Fetch live records and build canonical JSON strings for users and portfolio."""
    token = authenticate()
    raw_users = get_all_records(token, "users")
    raw_projects = get_all_records(token, "projects", expand="owner")

    # 1. Process users
    user_id_map = {}
    users_export = []

    for u in raw_users:
        pb_id = u["id"]
        seed_id = u.get("seed_id")
        if seed_id:
            user_id = seed_id
        elif u.get("github_handle"):
            user_id = f"usr-{u['github_handle'].lower()}"
        else:
            user_id = f"usr-{pb_id}"

        user_id_map[pb_id] = user_id

        email = u.get("email")
        if email and (email.endswith("@cetana.local") or email == f"{user_id}@cetana.local"):
            email = None

        rec = {
            "id": user_id,
            "name": u.get("name") or "",
            "email": email or None,
            "github_handle": u.get("github_handle") or None,
            "role": u.get("role") or "contributor",
            "org": u.get("org") or None,
            "active": bool(u.get("active", True))
        }
        users_export.append(rec)

    users_path = DATA_DIR / "users.json"
    existing_user_order = []
    if users_path.exists():
        try:
            existing_user_order = [x["id"] for x in json.loads(users_path.read_text(encoding="utf-8"))]
        except Exception:
            pass
    def user_sort_key(x):
        uid = x["id"]
        return (0, existing_user_order.index(uid)) if uid in existing_user_order else (1, uid)
    users_export.sort(key=user_sort_key)

    # 2. Process projects
    projects_export = []
    for p in raw_projects:
        owner_id = None
        owner_val = p.get("owner")
        if owner_val and owner_val in user_id_map:
            owner_id = user_id_map[owner_val]
        elif p.get("expand", {}).get("owner"):
            owner_rec = p["expand"]["owner"]
            owner_id = owner_rec.get("seed_id") or f"usr-{owner_rec['id']}"

        if not owner_id:
            owner_id = "usr-unknown"

        rec = {
            "id": p.get("lab_id") or p.get("id"),
            "slug": p.get("slug") or "",
            "name": p.get("name") or "",
            "descriptor": p.get("descriptor") or None,
            "archetype": p.get("archetype") or "mini-app",
            "owner_id": owner_id,
            "repo_url": p.get("repo_url") or None,
            "reference_url": p.get("reference_url") or None,
            "dev_environment": p.get("dev_environment") or "cloud",
            "status_source": p.get("status_source") or "local"
        }
        projects_export.append(rec)

    portfolio_path = DATA_DIR / "portfolio.json"
    existing_proj_order = []
    if portfolio_path.exists():
        try:
            existing_proj_order = [x["id"] for x in json.loads(portfolio_path.read_text(encoding="utf-8"))]
        except Exception:
            pass
    def proj_sort_key(x):
        pid = x["id"]
        return (0, existing_proj_order.index(pid)) if pid in existing_proj_order else (1, pid)
    projects_export.sort(key=proj_sort_key)

    users_json_str = json.dumps(users_export, indent=2) + "\n"
    portfolio_json_str = json.dumps(projects_export, indent=2) + "\n"
    return users_json_str, portfolio_json_str, users_export, projects_export


def check_export_freshness(timeout=1.5):
    """
    Checks if live PocketBase is reachable and whether committed data/*.json matches live PB.
    Returns:
        dict: {"reachable": bool, "in_sync": bool, "error": str or None, "details": list}
    """
    if not is_pb_reachable(timeout=timeout):
        return {
            "reachable": False,
            "in_sync": False,
            "error": f"PocketBase is not reachable at {PB_URL}",
            "details": []
        }

    try:
        users_json_str, portfolio_json_str, users_export, projects_export = get_export_payloads()
    except Exception as e:
        return {
            "reachable": True,
            "in_sync": False,
            "error": f"Failed to retrieve PocketBase records: {e}",
            "details": [str(e)]
        }

    users_path = DATA_DIR / "users.json"
    portfolio_path = DATA_DIR / "portfolio.json"
    cur_users_str = users_path.read_text(encoding="utf-8") if users_path.exists() else ""
    cur_portfolio_str = portfolio_path.read_text(encoding="utf-8") if portfolio_path.exists() else ""

    users_changed = cur_users_str != users_json_str
    portfolio_changed = cur_portfolio_str != portfolio_json_str

    details = []
    if users_changed:
        details.append(f"data/users.json divergence ({len(users_export)} export rows vs {cur_users_str.count('{')} current)")
    if portfolio_changed:
        details.append(f"data/portfolio.json divergence ({len(projects_export)} export rows vs {cur_portfolio_str.count('{')} current)")

    if not users_changed and not portfolio_changed:
        return {
            "reachable": True,
            "in_sync": True,
            "error": None,
            "details": ["Committed data/ export matches live PocketBase records."]
        }

    return {
        "reachable": True,
        "in_sync": False,
        "error": "Committed data/ export diverges from live PocketBase",
        "details": details
    }


def export_data(dry_run=True):
    print(f"→ Fetching live records from PocketBase ({PB_URL})")
    users_json_str, portfolio_json_str, users_export, projects_export = get_export_payloads()
    print(f"  Live counts: {len(users_export)} users, {len(projects_export)} projects")

    users_path = DATA_DIR / "users.json"
    portfolio_path = DATA_DIR / "portfolio.json"

    # Compare with existing
    cur_users_str = users_path.read_text(encoding="utf-8") if users_path.exists() else ""
    cur_portfolio_str = portfolio_path.read_text(encoding="utf-8") if portfolio_path.exists() else ""

    users_changed = cur_users_str != users_json_str
    portfolio_changed = cur_portfolio_str != portfolio_json_str

    if not users_changed and not portfolio_changed:
        print("✅ Data is in full sync: live PocketBase matches committed data/*.json.")
        return 0

    print(f"⚠️  Divergence detected:")
    if users_changed:
        print(f"   - data/users.json has updates ({len(users_export)} export rows vs {cur_users_str.count('{')} current)")
    if portfolio_changed:
        print(f"   - data/portfolio.json has updates ({len(projects_export)} export rows vs {cur_portfolio_str.count('{')} current)")

    if dry_run:
        print("\n[DRY-RUN] No files modified. Run with --apply (or 'just export-live-data') to overwrite data/*.json.")
        return 0

    users_path.write_text(users_json_str, encoding="utf-8")
    portfolio_path.write_text(portfolio_json_str, encoding="utf-8")
    print("\n✅ Successfully exported live PocketBase records to:")
    print(f"   - {users_path}")
    print(f"   - {portfolio_path}")
    print("\nNext step: Run `just validate-local` and commit changes via a pull request.")
    return 0


def main():
    if "--check" in sys.argv[1:]:
        res = check_export_freshness()
        if not res["reachable"]:
            print(f"⚠️  PocketBase unreachable at {PB_URL} (skipping live export freshness check).")
            return 0
        if not res["in_sync"]:
            print("❌ Committed data/ export is stale compared to live PocketBase:", file=sys.stderr)
            for d in res["details"]:
                print(f"   • {d}", file=sys.stderr)
            print("\nRun: just export-live-data", file=sys.stderr)
            return 1
        print("✅ Committed data/ export is in sync with live PocketBase.")
        return 0

    dry_run = "--apply" not in sys.argv[1:]
    return export_data(dry_run=dry_run)


if __name__ == "__main__":
    sys.exit(main())
