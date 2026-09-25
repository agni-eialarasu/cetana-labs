# PocketBase Backend — Control Hub Web App (`BK-008` Phase 1)

Scaffolding for the PocketBase backend that will replace the static, file-based
control plane, per [`RFC-LAB-000-003`](../../docs/rfc/RFC-LAB-000-003-pocketbase-web-app.md).
This directory holds the **declarative schema** and **seed importer**; the running
server is provisioned by the dev container (Codespaces) — see §Running below.

> **Phase 1 status:** collections defined, importer written, API rules drafted.
> Live server run + UI parity are Phase 1→2 work; this scaffolding is runnable as
> soon as a PocketBase binary/service is available (it is not present in the
> Kiro Web sandbox by design — see `RFC-LAB-000-001`).

## Contents

| Path | Purpose |
| :--- | :--- |
| `pb_schema.json` | PocketBase collections import (generated from `data/` by `scripts/generate_pb_schema.py`). |
| `../../scripts/generate_pb_schema.py` | Renders `pb_schema.json` from the `data/*.schema.json` + masters. |
| `../../scripts/pb_import.py` | Idempotently imports `data/*.json` into a running PocketBase instance. |

## Collections (derived from `data/`)

| Collection | Type | Source | Notes |
| :--- | :--- | :--- | :--- |
| `users` | auth | `data/users.json` | Login identity + ownership target. |
| `projects` | base | `data/portfolio.json` | `owner` → relation to `users`. |
| `memberships` | base | `data/memberships.json` | `user`/`project` relations; many-to-many join. |

`status_snapshots` and `sprints` are deferred to Phase 4 (`RFC-LAB-000-003` §7).

## Running (Codespaces / any host with the PocketBase binary)

```bash
# 1. Start PocketBase (binary or devcontainer service) on :8090
./pocketbase serve --http=0.0.0.0:8090

# 2. Create the admin/superuser (first run only)
./pocketbase superuser upsert admin@cetana.local <password>

# 3. Import the schema (Admin UI > Settings > Import collections, or via API)
#    then seed the data:
export PB_URL=http://127.0.0.1:8090
export PB_ADMIN_EMAIL=admin@cetana.local
export PB_ADMIN_PASSWORD=<password>
python3 scripts/pb_import.py            # dry-run preview
python3 scripts/pb_import.py --apply     # perform the import
```

## Access rules (draft — seeds `BK-007` RBAC)

Drafted in `pb_schema.json` per collection; refined in Phase 3:
- **projects / memberships**: readable by authenticated members; writable by the
  project `owner` and superusers.
- **users**: self-viewable; managed by superusers.

See `RFC-LAB-000-003` §5 for the full auth/RBAC model.
