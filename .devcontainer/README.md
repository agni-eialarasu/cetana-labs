# Dev Container — Cetana Labs (`LAB-000`)

Reproducible cloud development environment for the Cetana Labs Control Hub, per [`RFC-LAB-000-001`](../docs/rfc/RFC-LAB-000-001-cloud-dev-migration.md).

## What it provisions
- **Python 3.11** — runs the zero-dependency governance scripts (`generate_status.py`, `generate_dashboard.py`, `validate_portfolio.py`, `project_validate.py`).
- **GitHub CLI (`gh`)** — supports remote `STATUS.md` sync (`--sync-remote`) and the trunk-based commit workflow in [AGENTS.md](../AGENTS.md).
- On attach, it runs `validate_portfolio.py` as a smoke check.

## Where it runs
- **GitHub Codespaces** — one-click reproducible environment. Reserved as the primary target once `LAB-000` grows persistent services (db + server) per RFC §5.
- Any Dev Containers-compatible tool (VS Code Dev Containers, etc.).

> The primary day-to-day environment today is **Kiro Web** (browser-based, no container needed). This devcontainer exists so the environment is reproducible and forward-compatible with the planned full web-app (db + server) + RBAC evolution — new services get declared here, never on a local machine.

## Forward compatibility
When the server/db/auth layer lands (backlog `BK-007`, RBAC), add the services as devcontainer `features`, a `docker-compose` service set, or `forwardPorts` entries here — keeping the environment fully cloud-based and reproducible.
