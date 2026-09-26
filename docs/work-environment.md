# Cetana Labs — Work Environment & Operations Guide

> 📋 Decision of record: [`RFC-LAB-000-007`](rfc/RFC-LAB-000-007-work-environment.md).
> Adapted from the Nexus Pulse (`LAB-003`) Developer Guide, translated to this stack
> (PocketBase + SQLite + SvelteKit, not Postgres/Supabase).

This is the authoritative guide for developing on Cetana Labs across **Kiro Web** and **Kiro IDE**.

---

## ⚡ Command Cheat-Sheet

Every command exists as both a Kiro `/command` and a `make` target (identical behavior).

| Category | Make | Slash command | What it does |
|---|---|---|---|
| **Readiness** | `make env-doctor` | `/env-doctor` | Surface-aware check: is *this* environment ready? (diagnostic only) |
| **Validate** | `make validate-local` | `/validate-local` | Full local pre-flight: Python validators + SvelteKit type-check/build |
| | `make validate-staging` | `/validate-staging` | Probe staging health (placeholder: GCP/Vercel) |
| **Local stack** | `make start-local` | `/start-local` | Start PocketBase (:8090) + SvelteKit dev (:5173) |
| | `make stop-local` | `/stop-local` | Stop dev servers (preserves data) |
| | `make status-local` | `/status-local` | Are the servers up? |
| **Data** | `make seed` | — | Seed PocketBase from `data/` (`pb_import.py --apply`) |
| | `make clean-data` | — | Reset local DB to a clean slate |
| **Containers** | `make pb-image` | — | Build PocketBase image (Podman-first) for staging parity |
| **Sprint** | — | `/sprint-start`, `/sprint-done` | Open / close a sprint |
| **Audit** | — | `/audit-doc`, `/audit-project` | Doc review / project health sweep |

> Run `make` (or `make help`) any time for this list.

---

## 1. Surface Roles (Kiro Web vs Kiro IDE)

Two surfaces, one repo. Use the right one for the job (`RFC-LAB-000-007` §2.1):

| Surface | Role | Do this here |
|---|---|---|
| **Kiro Web** | **Stateless** governance/docs | RFCs, backlog/changelog/journal, `data/` edits, PR review, planning, Python `scripts/`, status broadcasts |
| **Kiro IDE** (local) | **Stateful** servers/data | `/start-local`, PocketBase DB, SvelteKit UI dev, secrets/OAuth, staging deploys |

Not a hard wall — Web can edit anything, it just can't run persistent servers.

---

## 2. Prerequisites (Kiro IDE / local)

Toolchain is **Homebrew-native** on the reference MBP work machine (nvm/pyenv shell
hooks are intentionally disabled for fast terminal startup — do **not** rely on `nvm`).

- **Python 3.11+** (governance scripts are zero-dependency; no venv needed). `uv` is the standard if deps are ever added.
- **Node** & **pnpm 10.27** via Homebrew (`/opt/homebrew/bin/node`, `/opt/homebrew/bin/pnpm`). `package.json` pins `packageManager: pnpm@10.27.0`; Corepack keeps it consistent. No per-project Node switching.
- **PocketBase >= 0.23** — system binary via Homebrew (`pb`), or fetched by `.devcontainer/setup-pocketbase.sh` in cloud/CI.
- **Podman** (preferred; `pod-start`/`pod-stop` manage the VM) or Docker context — only for containerized workflows; local dev runs the `pb` binary directly.

Kiro Web needs none of the server tooling — it's for stateless work.

---

## 3. Initial Setup (first time, local)

```bash
# 1. Environment config
cp .env.example .env          # fill in PB_ADMIN_* etc.

# 2. Node deps (Node/pnpm are Homebrew-native; no nvm)
cd app/web && pnpm install --frozen-lockfile && cd ../..

# 3. PocketBase — use the Homebrew `pb` binary (or fetch in cloud/CI)
pb --version                   # confirm >= 0.23; else: bash .devcontainer/setup-pocketbase.sh

# 4. Sanity check
make env-doctor
```

---

## 4. Starting the Local Stack

Two modes, mirroring Nexus Pulse's State A / State B:

### State A — Clean slate (recommended default)
```bash
make start-local
```
Starts PocketBase (`:8090`, admin `/_/`) and SvelteKit dev (`:5173`) with an empty DB — good for onboarding/intake flows.

### State B — Seeded from `data/`
```bash
make start-local            # in one terminal
# then, with PB_ADMIN_* set in .env:
make seed                    # imports users/projects/memberships from data/
```
Seeds the 3 users, 6 projects, and memberships from the relational masters (`RFC-LAB-000-002`).

### Stop
```bash
make stop-local              # frees :5173 and :8090; pb_data preserved
```

---

## 5. Database & Auth (local)

| Parameter | Value |
|---|---|
| PocketBase URL | `http://127.0.0.1:8090` |
| Admin UI | `http://127.0.0.1:8090/_/` |
| Data file | `app/pocketbase/pb_data/` (SQLite, gitignored) |
| Superuser | from `.env` (`PB_ADMIN_EMAIL` / `PB_ADMIN_PASSWORD`) |

**Test personas & RBAC (forward — Phase 3, `RFC-LAB-000-006`):** once GitHub OAuth + roles land, personas map to the `memberships` roles (`owner`/`lead`/`contributor`/`reviewer`/`stakeholder`). Provisioning steps will be added here when auth is built.

---

## 6. Full Clean Reset

```bash
# Fast: wipe local DB data, keep schema/binary
make clean-data && make seed

# Deep (container path): rebuild the PocketBase image
podman build -t cetana-pocketbase -f app/pocketbase/Containerfile app/pocketbase   # or: docker build ...
```

---

## 7. Config Sync — Personal vs Project (one-way)

- **Project config** (`.kiro/skills/`, `.kiro/steering/`) is **committed** → travels with the repo to both surfaces automatically. No action needed.
- **Personal config** (`~/.kiro/skills/` — `/sign-in`, `/sign-off`, `/session-save`, `/session-resume`) is **local**. Kiro Web can't read it directly.
  - **Local `~/.kiro/` is the source of truth.** After editing, push via **Kiro Web → Settings → Sync** (one-way local→cloud). Web edits do NOT flow back.
  - A temporary `my-kiro` symlink to `~/.kiro` (for viewing in the IDE) is gitignored — never commit it.

---

## 8. Development Process & PR Protocol

Governed by [`RFC-LAB-000-004`](rfc/RFC-LAB-000-004-branching-model.md) (hybrid, path-scoped):
- **App code / `data/` / migrations** → feature branch → PR → green CI → squash-merge to `main`.
- **Governance / docs** → may fast-path to `main`.
- Always run `make validate-local` (`/validate-local`) before opening a PR or `/sprint-done`.
- Never force-push `main`; roll back via revert PR.

---

## 9. Staging (planned — not yet provisioned)

Target **GCP** for backend (PocketBase) + frontend; optional **Vercel** for frontend quick-wins. Begins after the repo transfers to the **org account**. `/status-staging` and `/validate-staging` are placeholders until then.
