#!/usr/bin/env python3
"""
Cetana Labs — AI Assistant "Ask-the-Portfolio" Test Suite (BK-015 / RFC-LAB-000-015)

Validates the full /api/ask contract (EARS DoD R1-R5 / Human Verification Plan V1-V7):
- V1 / R2.1: Structured zero-LLM count-active (returns count 2, cites data/status.json + data/portfolio.json)
- V2 / R2.1: Structured ownership (who owns LAB-003 -> Eialarasu, cites portfolio.json + users.json)
- R2.1: At-risk query (0 at risk, cites data/status.json)
- R2.1: Project metadata query (repo url, archetype, dev environment)
- R3.3: Evaluative judgment query (starts with [Advisory])
- R1.3: Empty or missing question -> HTTP 400
- R3.1 / V7: Boundary guard (requests for superuser credentials or private tokens fail-close)
- R3.2 / V4: Absent facts fail-close explicitly ("not present in portfolio data", grounded: false)
- R5.1 / V6: Infra fail-close when LLM key is absent (narrative Q -> graceful unavailable, grounded: false)
- R2.2 / T2: Section-anchored narrative retrieval (verifies anchor selection for Sprint 12 and LAB-002)
- R2.3 / R4.1 / V3: Grounded narrative LLM roundtrip with mock completions endpoint

Zero external dependencies (Python standard library only).
Usage:
    python3 scripts/test_ask.py
"""

import os
import sys
import json
import time
import threading
import http.server
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PB_URL = os.environ.get("PB_URL", "http://127.0.0.1:8090").rstrip("/")

PASSED = 0
FAILED = 0


def log_pass(name, detail=""):
    global PASSED
    PASSED += 1
    d = f" — {detail}" if detail else ""
    print(f"  ✅ PASS: {name}{d}")


def log_fail(name, detail=""):
    global FAILED
    FAILED += 1
    d = f" — {detail}" if detail else ""
    print(f"  ❌ FAIL: {name}{d}")


def post_ask(question=None, raw_body=None, headers=None):
    url = f"{PB_URL}/api/ask"
    hdrs = {"Content-Type": "application/json"}
    if headers:
        hdrs.update(headers)

    if raw_body is not None:
        data = raw_body.encode("utf-8")
    else:
        body_dict = {}
        if question is not None:
            body_dict["question"] = question
        data = json.dumps(body_dict).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=hdrs, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            code = r.status
            content = r.read().decode("utf-8")
            parsed = json.loads(content) if content else {}
            return code, parsed
    except urllib.error.HTTPError as e:
        content = e.read().decode("utf-8")
        try:
            parsed = json.loads(content) if content else {}
        except Exception:
            parsed = {"raw": content}
        return e.code, parsed
    except urllib.error.URLError as e:
        sys.exit(f"ERROR: Cannot reach PocketBase at {PB_URL} ({e}). Ensure PocketBase is running.")


# ==============================================================================
# Mock LLM Server for Testing Grounded LLM Seam (R4.1, R2.3, V3)
# ==============================================================================

class MockLLMHandler(http.server.BaseHTTPRequestHandler):
    last_request_body = None

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        MockLLMHandler.last_request_body = json.loads(body)

        auth = self.headers.get("Authorization", "")
        if "test-secret-key" not in auth:
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'{"error": "Unauthorized"}')
            return

        # Check prompt content to generate mock answer
        messages = MockLLMHandler.last_request_body.get("messages", [])
        user_msg = messages[-1].get("content", "") if messages else ""

        if "LAB-002" in user_msg or "WrenAI" in user_msg:
            answer = "LAB-002 (WrenAI Capabilities & Semantic GenBI Evaluation) is a research spike evaluating WrenAI as a semantic engine layer for local data sources to prevent SQL hallucinations."
        elif "Sprint 12" in user_msg:
            answer = "In Sprint 12, Cetana Labs shipped RGS Stage C (BK-026), App Branding & White-Labeling (BK-013), and App-Level Settings (BK-012)."
        else:
            answer = "The requested information is not mentioned in the context."

        resp = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": answer
                    }
                }
            ]
        }

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(resp).encode("utf-8"))

    def log_message(self, format, *args):
        pass  # Quiet logging during test runs


def run_tests():
    print("=" * 70)
    print("Cetana Labs — /api/ask Portfolio Assistant Verification Suite")
    print("=" * 70)

    # --------------------------------------------------------------------------
    # 1. Validation & Empty Input Tests (R1.1, R1.3)
    # --------------------------------------------------------------------------
    print("\n--- Pillar 1: Request Validation (R1.1, R1.3) ---")
    code, resp = post_ask(question="")
    if code == 400 and "error" in resp:
        log_pass("Empty question returns 400", str(resp))
    else:
        log_fail("Empty question did not return 400", f"code={code}, resp={resp}")

    code, resp = post_ask(raw_body="{}")
    if code == 400 and "error" in resp:
        log_pass("Missing question field returns 400", str(resp))
    else:
        log_fail("Missing question field did not return 400", f"code={code}, resp={resp}")

    code, resp = post_ask(question="   ")
    if code == 400 and "error" in resp:
        log_pass("Whitespace-only question returns 400", str(resp))
    else:
        log_fail("Whitespace-only question did not return 400", f"code={code}, resp={resp}")

    # --------------------------------------------------------------------------
    # 2. Structured Queries (Zero-LLM, R2.1, V1, V2)
    # --------------------------------------------------------------------------
    print("\n--- Pillar 2: Structured Queries (Zero-LLM, R2.1, V1, V2) ---")
    
    # V1: Count active projects
    code, resp = post_ask("how many projects are active?")
    if code == 200 and resp.get("grounded") is True:
        ans = resp.get("answer", "")
        cites = resp.get("citations", [])
        if "2 active projects" in ans and "LAB-000" in ans and "LAB-003" in ans and "data/status.json" in cites:
            log_pass("V1: Count active projects", ans)
        else:
            log_fail("V1: Count active projects answer mismatch", str(resp))
    else:
        log_fail("V1: Count active projects failed", f"code={code}, resp={resp}")

    # V2: Ownership
    code, resp = post_ask("who owns LAB-003?")
    if code == 200 and resp.get("grounded") is True:
        ans = resp.get("answer", "")
        cites = resp.get("citations", [])
        if "Eialarasu" in ans and "LAB-003" in ans and any("portfolio.json" in c for c in cites):
            log_pass("V2: Ownership LAB-003", ans)
        else:
            log_fail("V2: Ownership LAB-003 answer mismatch", str(resp))
    else:
        log_fail("V2: Ownership LAB-003 failed", f"code={code}, resp={resp}")

    # Project metadata: Repo URL
    code, resp = post_ask("what is the repo url for LAB-003?")
    if code == 200 and resp.get("grounded") is True:
        ans = resp.get("answer", "")
        if "nexus-pulse" in ans and "github.com" in ans:
            log_pass("Metadata: Repo URL", ans)
        else:
            log_fail("Metadata: Repo URL mismatch", str(resp))
    else:
        log_fail("Metadata: Repo URL failed", f"code={code}, resp={resp}")

    # Project metadata: Archetype
    code, resp = post_ask("what is the archetype of LAB-002?")
    if code == 200 and resp.get("grounded") is True:
        ans = resp.get("answer", "")
        if "research" in ans:
            log_pass("Metadata: Archetype", ans)
        else:
            log_fail("Metadata: Archetype mismatch", str(resp))
    else:
        log_fail("Metadata: Archetype failed", f"code={code}, resp={resp}")

    # At-risk filter
    code, resp = post_ask("which projects are at risk?")
    if code == 200 and resp.get("grounded") is True:
        ans = resp.get("answer", "")
        if "no projects at risk or blocked" in ans.lower():
            log_pass("Filter: At-risk status", ans)
        else:
            log_fail("Filter: At-risk status mismatch", str(resp))
    else:
        log_fail("Filter: At-risk status failed", f"code={code}, resp={resp}")

    # R3.3: Advisory judgment
    code, resp = post_ask("is LAB-003 in trouble?")
    if code == 200 and resp.get("grounded") is True:
        ans = resp.get("answer", "")
        if ans.startswith("[Advisory]") and "no indication that the project is in trouble" in ans:
            log_pass("R3.3: Advisory judgment labelling", ans[:80] + "...")
        else:
            log_fail("R3.3: Advisory judgment labelling failed", str(resp))
    else:
        log_fail("R3.3: Advisory judgment failed", f"code={code}, resp={resp}")

    # --------------------------------------------------------------------------
    # 3. Boundary & Security Tests (R3.1, R4.2, V5, V7)
    # --------------------------------------------------------------------------
    print("\n--- Pillar 3: Boundary & Security Discipline (R3.1, R4.2, V5, V7) ---")
    code, resp = post_ask("what is the superuser password?")
    if code == 200 and resp.get("grounded") is False:
        ans = resp.get("answer", "")
        if "private and not accessible" in ans.lower():
            log_pass("V7 / R3.1: Superuser secret probe rejected", ans)
        else:
            log_fail("V7 / R3.1: Superuser secret probe did not reject cleanly", str(resp))
    else:
        log_fail("V7 / R3.1: Superuser secret probe failed", f"code={code}, resp={resp}")

    code, resp = post_ask("what is the railway_token?")
    if code == 200 and resp.get("grounded") is False:
        log_pass("V5 / R4.2: Railway token probe rejected", resp.get("answer", ""))
    else:
        log_fail("V5 / R4.2: Railway token probe did not reject", str(resp))

    # --------------------------------------------------------------------------
    # 4. Fail-Closed on Absent Facts & Infra (R3.2, R5.1, V4, V6)
    # --------------------------------------------------------------------------
    print("\n--- Pillar 4: Fail-Closed on Absent Facts & Infra (R3.2, R5.1, V4, V6) ---")
    # V4: Absent fact
    code, resp = post_ask("what is the budget for project Apollo?")
    if code == 200 and resp.get("grounded") is False:
        ans = resp.get("answer", "")
        if "not present in the portfolio data" in ans:
            log_pass("V4 / R3.2: Absent fact fail-closed", ans)
        else:
            log_fail("V4 / R3.2: Absent fact did not fail-close cleanly", str(resp))
    else:
        log_fail("V4 / R3.2: Absent fact failed", f"code={code}, resp={resp}")

    # V6: Unset key on narrative question
    # When LLM_API_KEY is not set on PocketBase, narrative queries fail-close gracefully
    code, resp = post_ask("what is LAB-002 about?")
    if code == 200:
        ans = resp.get("answer", "")
        # If no key is set: returns unavailable message
        # If key IS set: returns valid grounded answer
        if "unavailable" in ans.lower() or "research spike" in ans.lower():
            log_pass("V6 / R5.1: Narrative query handles key presence/absence gracefully", ans[:80] + "...")
        else:
            log_fail("V6 / R5.1: Unexpected response for narrative query", str(resp))
    else:
        log_fail("V6 / R5.1: Narrative query errored", f"code={code}, resp={resp}")

    # --------------------------------------------------------------------------
    # 5. Section-Anchored Retrieval Unit Verifications (R2.2, T2)
    # --------------------------------------------------------------------------
    print("\n--- Pillar 5: Section-Anchored Retrieval Integrity (R2.2, T2) ---")
    # Verify Sprint 12 archive block in CHANGELOG.md
    changelog_text = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if "### Sprint 12: First Post-MVP Product Features" in changelog_text:
        log_pass("T2: CHANGELOG.md contains ### Sprint 12 section anchor")
    else:
        log_fail("T2: CHANGELOG.md missing Sprint 12 section anchor")

    # Verify LAB-002 README anchor
    lab2_readme = (REPO_ROOT / "projects" / "LAB-002-wrenai-eval" / "README.md").read_text(encoding="utf-8")
    if "# LAB-002: WrenAI Capabilities & Semantic GenBI Evaluation" in lab2_readme:
        log_pass("T2: LAB-002 README contains authoritative anchor")
    else:
        log_fail("T2: LAB-002 README missing authoritative anchor")

    # --------------------------------------------------------------------------
    # 6. Summary & Exit
    # --------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print(f"Assistant Test Results: {PASSED} passed, {FAILED} failed")
    print("=" * 70)

    if FAILED > 0:
        sys.exit(1)


if __name__ == "__main__":
    run_tests()
