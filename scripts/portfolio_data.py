#!/usr/bin/env python3
"""
Cetana Labs — Relational Data Access Layer (BK-009 / RFC-LAB-000-002)

Lightweight, zero-dependency accessor for the data/ JSON masters
(users, portfolio, memberships). Consumer scripts prefer this structured
source over regex-parsing Markdown, with graceful fallback when data/ is
absent (returns empty lookups so callers can fall back to their old paths).

Designed to map directly onto future PocketBase collections.
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"

ARCHETYPE_DISPLAY = {
    "control-plane": ("💻", "Control Plane"),
    "mini-app": ("💻", "Mini-App"),
    "research": ("📑", "Research"),
    "data-collection": ("📊", "Data Collection"),
    "verification": ("🔬", "Verification"),
}


def _load(name: str):
    path = DATA_DIR / name
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def load_users() -> list:
    return _load("users.json")


def load_projects() -> list:
    return _load("portfolio.json")


def load_memberships() -> list:
    return _load("memberships.json")


def users_by_id() -> dict:
    return {u["id"]: u for u in load_users()}


def projects_by_id() -> dict:
    return {p["id"]: p for p in load_projects()}


def owner_name_for(project_id: str) -> str:
    """Resolve a project's primary owner name via owner_id -> users master."""
    proj = projects_by_id().get(project_id)
    if not proj:
        return ""
    return users_by_id().get(proj.get("owner_id", ""), {}).get("name", "")


def members_for(project_id: str) -> list:
    """Return [{user, role}] for a project via the memberships join table."""
    ubi = users_by_id()
    out = []
    for m in load_memberships():
        if m.get("project_id") == project_id:
            out.append({"user": ubi.get(m.get("user_id"), {}), "role": m.get("role")})
    return out


def archetype_display(archetype_key: str):
    """(icon, name) tuple for an archetype enum key."""
    return ARCHETYPE_DISPLAY.get(archetype_key, ("💻", archetype_key or "Mini-App"))


def enrich_project_data(project_id: str, data: dict) -> dict:
    """
    Overlay structural fields from the data/ layer onto a STATUS-parsed dict.
    Prefers JSON values; leaves existing values untouched when data/ is absent.
    Mutates and returns `data`.
    """
    proj = projects_by_id().get(project_id)
    if not proj:
        return data  # data/ absent or project not registered -> caller falls back

    # repo/reference URL
    ref = proj.get("repo_url") or proj.get("reference_url")
    if ref:
        data["repo_url"] = ref

    # archetype (icon + name)
    icon, name = archetype_display(proj.get("archetype"))
    data["archetype_icon"] = icon
    data["archetype_name"] = name

    # owner (authoritative from users master)
    owner = users_by_id().get(proj.get("owner_id", ""), {})
    if owner.get("name"):
        data["lead"] = owner["name"]
        data["owner_id"] = proj.get("owner_id")
        data["owner_github"] = owner.get("github_handle")

    # dev environment
    if proj.get("dev_environment"):
        data["dev_environment"] = proj["dev_environment"]

    return data
