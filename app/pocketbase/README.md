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

## Version note (PocketBase >= 0.23)

PocketBase v0.23 was a major refactor. This scaffold targets **v0.23+** (collections
use the `fields` format; admins are `_superusers` auth records — no `/api/admins`).
If you have a system PocketBase via Homebrew (`pb`, e.g. v0.28+), use it directly.
The JS SDK in `app/web` is pinned `>=0.26` for compatibility.

## Setup (one command)

From the **repo root**:
```bash
make setup     # env + deps + superuser + PROVISION collections + seed — zero manual UI steps
```

## Manual equivalent

```bash
# 1. Start PocketBase on :8090
pb serve --http=0.0.0.0:8090          # macOS Homebrew (WORK_MACHINE guide); or ./pocketbase ...

# 2. Superuser (first run)
pb superuser upsert admin@cetana.local 'CetanaLocal2026!'

# 3. Provision collections VIA API (version-robust — no schema-file import)
export PB_URL=http://127.0.0.1:8090 PB_ADMIN_EMAIL=admin@cetana.local PB_ADMIN_PASSWORD='CetanaLocal2026!'
python3 scripts/pb_provision.py            # dry-run: show the create plan
python3 scripts/pb_provision.py --apply     # create users -> projects -> memberships

# 4. Seed from the relational masters
python3 scripts/pb_import.py --apply
```

> **Why provisioning, not schema import?** PocketBase's collections-import JSON format
> is version-sensitive and relations must reference real generated collection ids —
> a hand-written `pb_schema.json` fails to import cleanly (confirmed on v0.40).
> `scripts/pb_provision.py` creates collections through the REST API in dependency
> order, resolving real relation ids at create time. It is **idempotent** (re-runnable).
>
> `app/pocketbase/pb_schema.json` is retained as a **human-readable reference** of the
> intended shape (generated from `data/`). The **authoritative** on-disk schema, if you
> want one, is the **export** from a provisioned instance (Admin UI > Settings > Export).

> **Containers are optional.** Local dev runs the bare binary (fast, ~0 extra RAM).
> Use the `Containerfile` (Podman-first) only for staging/GCP parity. On the MBP work
> machine, `pod-start` / `pod-stop` manage the Podman VM's 3 GB budget.

## Deploy on Railway (`railway.json`, `RFC-LAB-000-012` / `BK-017`)

`railway.json` (in this directory) pins the build so Railway does **not** auto-detect
the stack and run Railpack — the papercut the M5 spike hit. It sets
`build.builder = DOCKERFILE` with `dockerfilePath = Containerfile` (relative to this
directory). Deploy the backend with the Railway CLI from **this** directory so the
service root and the config align (avoids the Root-Directory path-doubling that
silently fails builds):

```bash
cd app/pocketbase && railway up      # or: make deploy-staging  (from repo root)
```

### One-time [HUMAN] step — persistent volume (CLI cannot do this)

PocketBase stores all state in `pb_data/`. The container serves it from **`/pb/pb_data`**
(see the `Containerfile`). Railway Volumes **cannot be attached via the CLI** — you must,
**once per service**, attach a Railway Volume mounted at **`/pb/pb_data`** in the Railway
dashboard (Service → Settings → Volumes). Without it, the SQLite database is ephemeral and
every redeploy wipes users/projects. The `Containerfile` deliberately omits a `VOLUME`
instruction because Railway rejects Dockerfile `VOLUME` declarations.

Other irreducibly-manual one-time steps (documented, not automated): Railway CLI login,
and the GitHub OAuth app + callback. See
[`docs/guides/developer-guide.md` → Deploy Operations](../../docs/guides/developer-guide.md).

## Access rules (draft — seeds `BK-007` RBAC)

Drafted in `pb_schema.json` per collection; refined in Phase 3:
- **projects / memberships**: readable by authenticated members; writable by the
  project `owner` and superusers.
- **users**: self-viewable; managed by superusers.

See `RFC-LAB-000-003` §5 for the full auth/RBAC model.
