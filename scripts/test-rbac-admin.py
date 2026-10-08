#!/usr/bin/env python3
"""
Cetana Labs — RBAC Admin Tier Test Harness (BK-030 / RFC-LAB-000-008 A1)

Validates the is_admin boolean auth tier and write-rule matrix:
- R5.1 / R6.4: Non-admin self-escalation forbidden (PATCH users.is_admin denied)
- R5.2: Superuser unaffected (full administrative access)
- R5.3 / R6.2: Owner path preserved (owner writes own project, denied on others)
- R6.1: Admin writes (create project, write settings, edit any project, delete project)
- R6.2: Owner writes (edit own project allowed, edit other denied, write settings denied, create/delete denied)
- R6.3: Plain authed user (reads allowed, all writes denied)
- R6.5: Anonymous (public reads allowed, all writes denied)

Fail-closed: Any violation immediately exits non-zero.
Zero external dependencies (Python standard library urllib).

Usage:
    python3 scripts/test-rbac-admin.py
"""

import os
import sys
import json
import urllib.request
import urllib.error
import urllib.parse

PB_URL = os.environ.get("PB_URL", "http://127.0.0.1:8090").rstrip("/")
PB_ADMIN_EMAIL = os.environ.get("PB_ADMIN_EMAIL", "admin@cetana.local")
PB_ADMIN_PASSWORD = os.environ.get("PB_ADMIN_PASSWORD", "CetanaLocal2026!")

# Test tracking
PASSED = 0
FAILED = 0


def req(method, path, token=None, body=None):
    url = f"{PB_URL}{path}"
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method)
    r.add_header("Content-Type", "application/json")
    if token:
        r.add_header("Authorization", token)
    try:
        with urllib.request.urlopen(r, timeout=15) as resp:
            resp_body = resp.read().decode()
            parsed = json.loads(resp_body) if resp_body else {}
            return resp.status, parsed
    except urllib.error.HTTPError as e:
        resp_body = e.read().decode()
        try:
            parsed = json.loads(resp_body) if resp_body else {}
        except Exception:
            parsed = {"raw": resp_body}
        return e.code, parsed
    except urllib.error.URLError as e:
        raise SystemExit(f"ERROR: Cannot reach PocketBase at {PB_URL} ({e}). Is it running?")


def check(name, condition, detail=""):
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  ✅ [PASS] {name}")
    else:
        FAILED += 1
        print(f"  ❌ [FAIL] {name}: {detail}")


def main():
    print(f"=== Cetana Labs RBAC Admin Tier Test Suite ===")
    print(f"Target: {PB_URL}\n")

    # 1. Superuser authentication
    status, super_auth = req(
        "POST", "/api/collections/_superusers/auth-with-password",
        body={"identity": PB_ADMIN_EMAIL, "password": PB_ADMIN_PASSWORD}
    )
    if status != 200 or "token" not in super_auth:
        raise SystemExit(f"FATAL: Superuser auth failed ({status}): {super_auth}")
    super_token = super_auth["token"]
    print("  Superuser authenticated successfully.")

    # Helper to clean up any leftover test records
    def find_records(collection, query_filter):
        q = urllib.parse.quote(query_filter)
        s, r = req("GET", f"/api/collections/{collection}/records?filter={q}&perPage=50", token=super_token)
        return r.get("items", []) if s == 200 else []

    # Clean existing test artifacts from previous runs if any
    for u in find_records("users", 'email ~ "test-rbac-"'):
        req("DELETE", f"/api/collections/users/records/{u['id']}", token=super_token)
    for p in find_records("projects", 'lab_id ~ "LAB-98"'):
        req("DELETE", f"/api/collections/projects/records/{p['id']}", token=super_token)
    for s in find_records("settings", 'key ~ "test_rbac_"'):
        req("DELETE", f"/api/collections/settings/records/{s['id']}", token=super_token)

    # 2. Provision test identities
    test_users = {
        "admin": {
            "email": "test-rbac-admin@cetana.local",
            "password": "TestPassword123!",
            "passwordConfirm": "TestPassword123!",
            "name": "Test Admin User",
            "github_handle": "test-rbac-admin-gh",
            "is_admin": True,
            "active": True,
        },
        "owner": {
            "email": "test-rbac-owner@cetana.local",
            "password": "TestPassword123!",
            "passwordConfirm": "TestPassword123!",
            "name": "Test Project Owner",
            "github_handle": "test-rbac-owner-gh",
            "is_admin": False,
            "active": True,
        },
        "other_owner": {
            "email": "test-rbac-other-owner@cetana.local",
            "password": "TestPassword123!",
            "passwordConfirm": "TestPassword123!",
            "name": "Test Other Project Owner",
            "github_handle": "test-rbac-other-owner-gh",
            "is_admin": False,
            "active": True,
        },
        "plain": {
            "email": "test-rbac-plain@cetana.local",
            "password": "TestPassword123!",
            "passwordConfirm": "TestPassword123!",
            "name": "Test Plain Authed User",
            "github_handle": "test-rbac-plain-gh",
            "is_admin": False,
            "active": True,
        },
    }

    user_records = {}
    tokens = {}

    for role_key, u_payload in test_users.items():
        s, rec = req("POST", "/api/collections/users/records", token=super_token, body=u_payload)
        if s not in (200, 201):
            raise SystemExit(f"FATAL: Failed to create test user {role_key} ({s}): {rec}")
        user_records[role_key] = rec

        # Authenticate as the user
        s_auth, auth_res = req(
            "POST", "/api/collections/users/auth-with-password",
            body={"identity": u_payload["email"], "password": u_payload["password"]}
        )
        if s_auth != 200 or "token" not in auth_res:
            raise SystemExit(f"FATAL: Failed to authenticate test user {role_key} ({s_auth}): {auth_res}")
        tokens[role_key] = auth_res["token"]

    print("  Created and authenticated 4 test identities (admin, owner, other_owner, plain).\n")

    # 3. Create test projects via superuser
    s_p1, owned_proj = req("POST", "/api/collections/projects/records", token=super_token, body={
        "lab_id": "LAB-980",
        "slug": "test-owned-proj",
        "name": "Test Owned Project",
        "archetype": "mini-app",
        "owner": user_records["owner"]["id"],
        "dev_environment": "local",
        "status_source": "local",
        "status_health": "🟢 On Track",
        "status_note": "Initial owner status note",
    })
    if s_p1 not in (200, 201):
        raise SystemExit(f"FATAL: Failed to create owned project ({s_p1}): {owned_proj}")

    s_p2, other_proj = req("POST", "/api/collections/projects/records", token=super_token, body={
        "lab_id": "LAB-981",
        "slug": "test-other-proj",
        "name": "Test Other Project",
        "archetype": "mini-app",
        "owner": user_records["other_owner"]["id"],
        "dev_environment": "local",
        "status_source": "local",
        "status_health": "🟢 On Track",
        "status_note": "Initial other status note",
    })
    if s_p2 not in (200, 201):
        raise SystemExit(f"FATAL: Failed to create other project ({s_p2}): {other_proj}")

    try:
        # -------------------------------------------------------------
        print("▶ Testing R6.1: Admin writes (is_admin=true)")
        # -------------------------------------------------------------
        # Admin creates project -> allowed
        s_ac, proj_admin = req("POST", "/api/collections/projects/records", token=tokens["admin"], body={
            "lab_id": "LAB-982",
            "slug": "test-admin-created",
            "name": "Admin Created Project",
            "archetype": "mini-app",
            "owner": user_records["owner"]["id"],
            "dev_environment": "local",
            "status_source": "local",
        })
        check("R6.1.1 Admin creates project -> allowed (HTTP 200/201)", s_ac in (200, 201), f"Status {s_ac}: {proj_admin}")

        # Admin writes settings -> allowed
        s_as, set_res = req("POST", "/api/collections/settings/records", token=tokens["admin"], body={
            "key": "test_rbac_admin_key",
            "value": "admin_value",
            "type": "string",
            "group": "test",
        })
        check("R6.1.2 Admin writes settings row -> allowed (HTTP 200/201)", s_as in (200, 201), f"Status {s_as}: {set_res}")

        # Admin edits project they do not own -> allowed
        s_ae, edit_res = req("PATCH", f"/api/collections/projects/records/{other_proj['id']}", token=tokens["admin"], body={
            "status_note": "Updated by admin non-owner",
        })
        check("R6.1.3 Admin edits project they do not own -> allowed (HTTP 200)", s_ae == 200, f"Status {s_ae}: {edit_res}")

        # Admin deletes project -> allowed
        if s_ac in (200, 201):
            s_ad, del_res = req("DELETE", f"/api/collections/projects/records/{proj_admin['id']}", token=tokens["admin"])
            check("R6.1.4 Admin deletes project -> allowed (HTTP 204)", s_ad == 204, f"Status {s_ad}: {del_res}")
        else:
            check("R6.1.4 Admin deletes project (skipped due to create failure)", False)

        # -------------------------------------------------------------
        print("\n▶ Testing R6.2 & R5.3: Owner writes (non-admin, matching github_handle)")
        # -------------------------------------------------------------
        # Owner edits their own project status -> allowed
        s_oe, own_edit = req("PATCH", f"/api/collections/projects/records/{owned_proj['id']}", token=tokens["owner"], body={
            "status_note": "Updated by legitimate owner",
            "status_health": "🟡 At Risk",
        })
        check("R6.2.1 Owner edits own project status -> allowed (HTTP 200)", s_oe == 200, f"Status {s_oe}: {own_edit}")

        # Owner edits another's project -> denied
        s_o_other, other_edit = req("PATCH", f"/api/collections/projects/records/{other_proj['id']}", token=tokens["owner"], body={
            "status_note": "Illicit edit by non-owner",
        })
        check("R6.2.2 Owner edits another owner's project -> denied (HTTP 400/403/404)", s_o_other in (400, 403, 404), f"Status {s_o_other}: {other_edit}")

        # Owner writes settings -> denied
        s_os, own_set = req("POST", "/api/collections/settings/records", token=tokens["owner"], body={
            "key": "test_rbac_owner_key",
            "value": "owner_val",
            "type": "string",
        })
        check("R6.2.3 Owner writes settings -> denied (HTTP 400/403)", s_os in (400, 403), f"Status {s_os}: {own_set}")

        # Owner creates project -> denied
        s_oc, own_create = req("POST", "/api/collections/projects/records", token=tokens["owner"], body={
            "lab_id": "LAB-983",
            "slug": "test-owner-created",
            "name": "Owner Created Project",
            "archetype": "mini-app",
            "owner": user_records["owner"]["id"],
            "dev_environment": "local",
            "status_source": "local",
        })
        check("R6.2.4 Owner creates project -> denied (HTTP 400/403)", s_oc in (400, 403), f"Status {s_oc}: {own_create}")

        # Owner deletes project -> denied
        s_od, own_del = req("DELETE", f"/api/collections/projects/records/{owned_proj['id']}", token=tokens["owner"])
        check("R6.2.5 Owner deletes project -> denied (HTTP 400/403/404)", s_od in (400, 403, 404), f"Status {s_od}: {own_del}")

        # -------------------------------------------------------------
        print("\n▶ Testing R6.3: Plain authed user writes & reads")
        # -------------------------------------------------------------
        # Plain authed creates project -> denied
        s_pc, p_create = req("POST", "/api/collections/projects/records", token=tokens["plain"], body={
            "lab_id": "LAB-984",
            "slug": "plain-created",
            "name": "Plain Created",
            "archetype": "mini-app",
            "owner": user_records["plain"]["id"],
            "dev_environment": "local",
            "status_source": "local",
        })
        check("R6.3.1 Plain user creates project -> denied (HTTP 400/403)", s_pc in (400, 403), f"Status {s_pc}: {p_create}")

        # Plain authed edits project -> denied
        s_pe, p_edit = req("PATCH", f"/api/collections/projects/records/{owned_proj['id']}", token=tokens["plain"], body={
            "status_note": "Illicit plain edit",
        })
        check("R6.3.2 Plain user edits project -> denied (HTTP 400/403/404)", s_pe in (400, 403, 404), f"Status {s_pe}: {p_edit}")

        # Plain authed deletes project -> denied
        s_pd, p_del = req("DELETE", f"/api/collections/projects/records/{owned_proj['id']}", token=tokens["plain"])
        check("R6.3.3 Plain user deletes project -> denied (HTTP 400/403/404)", s_pd in (400, 403, 404), f"Status {s_pd}: {p_del}")

        # Plain authed writes settings -> denied
        s_ps, p_set = req("POST", "/api/collections/settings/records", token=tokens["plain"], body={
            "key": "test_rbac_plain_key",
            "value": "plain_val",
            "type": "string",
        })
        check("R6.3.4 Plain user writes settings -> denied (HTTP 400/403)", s_ps in (400, 403), f"Status {s_ps}: {p_set}")

        # Plain authed reads projects -> allowed
        s_pr, p_read = req("GET", "/api/collections/projects/records", token=tokens["plain"])
        check("R6.3.5 Plain user reads projects list -> allowed (HTTP 200)", s_pr == 200, f"Status {s_pr}: {p_read}")

        # Plain authed reads settings -> allowed
        s_psr, p_set_read = req("GET", "/api/collections/settings/records", token=tokens["plain"])
        check("R6.3.6 Plain user reads settings list -> allowed (HTTP 200)", s_psr == 200, f"Status {s_psr}: {p_set_read}")

        # -------------------------------------------------------------
        print("\n▶ Testing R5.1 & R6.4: No self-escalation guardrail")
        # -------------------------------------------------------------
        # Plain user attempts to grant self is_admin -> denied
        s_escalate_plain, esc_p_res = req(
            "PATCH", f"/api/collections/users/records/{user_records['plain']['id']}",
            token=tokens["plain"],
            body={"is_admin": True}
        )
        check("R5.1.1 Plain user PATCHes own is_admin -> denied (HTTP 400/403/404)", s_escalate_plain in (400, 403, 404), f"Status {s_escalate_plain}: {esc_p_res}")

        # Owner user attempts to grant self is_admin -> denied
        s_escalate_owner, esc_o_res = req(
            "PATCH", f"/api/collections/users/records/{user_records['owner']['id']}",
            token=tokens["owner"],
            body={"is_admin": True}
        )
        check("R5.1.2 Owner user PATCHes own is_admin -> denied (HTTP 400/403/404)", s_escalate_owner in (400, 403, 404), f"Status {s_escalate_owner}: {esc_o_res}")

        # Verify neither user gained is_admin
        s_v1, u1 = req("GET", f"/api/collections/users/records/{user_records['plain']['id']}", token=super_token)
        s_v2, u2 = req("GET", f"/api/collections/users/records/{user_records['owner']['id']}", token=super_token)
        check("R5.1.3 Plain user record remains is_admin=false", u1.get("is_admin") is False, f"User state: {u1}")
        check("R5.1.4 Owner user record remains is_admin=false", u2.get("is_admin") is False, f"User state: {u2}")

        # Admin CAN update another user's record (R2.6)
        s_admin_edit_user, aeu_res = req(
            "PATCH", f"/api/collections/users/records/{user_records['plain']['id']}",
            token=tokens["admin"],
            body={"name": "Plain Renamed By Admin"}
        )
        check("R2.6 Admin updates user record -> allowed (HTTP 200)", s_admin_edit_user == 200, f"Status {s_admin_edit_user}: {aeu_res}")

        # -------------------------------------------------------------
        print("\n▶ Testing R6.5: Anonymous reads & writes")
        # -------------------------------------------------------------
        # Anon reads projects -> allowed
        s_ar_p, ar_p_res = req("GET", "/api/collections/projects/records")
        check("R6.5.1 Anonymous reads projects list -> allowed (HTTP 200)", s_ar_p == 200, f"Status {s_ar_p}: {ar_p_res}")

        # Anon reads settings -> allowed
        s_ar_s, ar_s_res = req("GET", "/api/collections/settings/records")
        check("R6.5.2 Anonymous reads settings list -> allowed (HTTP 200)", s_ar_s == 200, f"Status {s_ar_s}: {ar_s_res}")

        # Anon creates project -> denied
        s_ac_anon, ac_anon_res = req("POST", "/api/collections/projects/records", body={
            "lab_id": "LAB-985",
            "slug": "anon-created",
            "name": "Anon Created",
            "archetype": "mini-app",
            "owner": user_records["owner"]["id"],
            "dev_environment": "local",
            "status_source": "local",
        })
        check("R6.5.3 Anonymous creates project -> denied (HTTP 400/403)", s_ac_anon in (400, 403), f"Status {s_ac_anon}: {ac_anon_res}")

        # Anon edits project -> denied
        s_ae_anon, ae_anon_res = req("PATCH", f"/api/collections/projects/records/{owned_proj['id']}", body={
            "status_note": "Anon edit",
        })
        check("R6.5.4 Anonymous edits project -> denied (HTTP 400/403/404)", s_ae_anon in (400, 403, 404), f"Status {s_ae_anon}: {ae_anon_res}")

        # Anon deletes project -> denied
        s_ad_anon, ad_anon_res = req("DELETE", f"/api/collections/projects/records/{owned_proj['id']}")
        check("R6.5.5 Anonymous deletes project -> denied (HTTP 400/403/404)", s_ad_anon in (400, 403, 404), f"Status {s_ad_anon}: {ad_anon_res}")

        # Anon writes settings -> denied
        s_as_anon, as_anon_res = req("POST", "/api/collections/settings/records", body={
            "key": "test_rbac_anon_key",
            "value": "anon_val",
            "type": "string",
        })
        check("R6.5.6 Anonymous writes settings -> denied (HTTP 400/403)", s_as_anon in (400, 403), f"Status {s_as_anon}: {as_anon_res}")

    finally:
        # -------------------------------------------------------------
        print("\n▶ Cleanup: removing test artifacts")
        # -------------------------------------------------------------
        for u in user_records.values():
            req("DELETE", f"/api/collections/users/records/{u['id']}", token=super_token)
        for p_id in [owned_proj["id"], other_proj["id"]]:
            req("DELETE", f"/api/collections/projects/records/{p_id}", token=super_token)
        if s_as in (200, 201) and "id" in set_res:
            req("DELETE", f"/api/collections/settings/records/{set_res['id']}", token=super_token)
        print("  Cleaned test users, projects, and settings records.")

    print(f"\n==========================================")
    print(f"Results: {PASSED} passed, {FAILED} failed")
    print(f"==========================================")

    if FAILED > 0:
        print("❌ FAIL: One or more RBAC DoD criteria failed!", file=sys.stderr)
        return 1

    print("✅ All RBAC criteria verified successfully (DoD R5 & R6 satisfied).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
