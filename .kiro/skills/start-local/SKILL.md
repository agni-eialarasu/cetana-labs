---
name: start-local
description: >-
  Starts the local Cetana Labs development stack — the PocketBase backend (app/pocketbase) and the SvelteKit Sleek UI dev server (app/web). Use when the user runs /start-local or asks to spin up / run the app locally.
---

# Skill: Start Local Dev Stack (`/start-local`)

## Objective
Bring up the local development environment for the `BK-008` web app: the PocketBase backend and the SvelteKit "Sleek UI" frontend, so the user can develop and test end-to-end on their machine.

> **Environment note:** On the work machine, **Node/pnpm and PocketBase are all Homebrew-managed and on PATH** (`/opt/homebrew/bin`) — just run them directly, no nvm. PocketBase is a **PATH binary**, NOT a `./pocketbase` file in the repo (the repo copy is gitignored and usually absent). In a cloud host/Codespace with no PocketBase on PATH, `.devcontainer/setup-pocketbase.sh` fetches the right OS/arch binary into `app/pocketbase/`. **Always prefer the `just` recipes** (`just start-local` / `just seed`) — they resolve the PATH binary and the canonical `pb_data` dir for you. This stack runs on a local machine or Codespace — not in the Kiro Web sandbox.
>
> **Canonical rule:** never run a bare `./pocketbase` or `pocketbase serve` from an arbitrary directory — PocketBase resolves `pb_data` relative to CWD, so a wrong dir silently serves an empty DB. Use `just start-local` (it `cd`s into `app/pocketbase`) or `pocketbase serve --dir app/pocketbase/pb_data` from the repo root.

## Trigger Patterns
- `/start-local`
- "start the app locally", "run the dev servers", "spin up local"

## Steps

> **Recommended: one command.** `just start-local` brings up PocketBase (`:8090`) **and** the SvelteKit dev server (`:5173`) using the PATH binary and the canonical data dir. The manual steps below are only for debugging a single tier.

### 1. Ensure toolchain
```bash
# All Homebrew-managed on the work machine — just verify they're on PATH.
node --version && pnpm --version && pocketbase --version
# (Cloud host only: if node/pnpm are under nvm — export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh")
```

### 2. (First run) create the superuser
PocketBase is a **PATH binary** — run from the repo root, pointing at the canonical data dir (NO `cd`, NO `./`):
```bash
pocketbase superuser upsert "$PB_ADMIN_EMAIL" "$PB_ADMIN_PASSWORD" --dir app/pocketbase/pb_data
```
(`$PB_ADMIN_*` come from the root `.env`, now auto-loaded by `just`; `set -a && source .env && set +a` first if calling PocketBase directly outside a recipe.)

### 3. Start the stack
```bash
just start-local     # PocketBase :8090 (admin /_/) + SvelteKit dev :5173
```
In a cloud host with no PocketBase on PATH, `start-local` auto-runs `.devcontainer/setup-pocketbase.sh` to fetch the correct OS/arch binary first.

### 4. Seed
```bash
just seed            # provision collections (API) + import users/projects/memberships from data/
```

### 5. Report
- Print the URLs: backend `http://127.0.0.1:8090` (admin `/_/`), frontend `http://localhost:5173`.
- Open the app at **`http://localhost:5173`** (use `localhost`, matching the GitHub OAuth callback — avoids the token-exchange 400).

## Notes
- Long-running servers: run in the background / separate terminals; never block.
- To stop, use `/stop-local`. To check state, use `/status-local`.
