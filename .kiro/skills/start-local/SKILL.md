---
name: start-local
description: >-
  Starts the local Cetana Labs development stack — the PocketBase backend (app/pocketbase) and the SvelteKit Sleek UI dev server (app/web). Use when the user runs /start-local or asks to spin up / run the app locally.
---

# Skill: Start Local Dev Stack (`/start-local`)

## Objective
Bring up the local development environment for the `BK-008` web app: the PocketBase backend and the SvelteKit "Sleek UI" frontend, so the user can develop and test end-to-end on their machine.

> **Environment note:** Node is provided via nvm (source it if `node`/`pnpm` are missing). PocketBase is a single binary (not committed) fetched by `.devcontainer/setup-pocketbase.sh`. This stack runs on a local machine or Codespace — not in the Kiro Web sandbox.

## Trigger Patterns
- `/start-local`
- "start the app locally", "run the dev servers", "spin up local"

## Steps

### 1. Ensure toolchain
```bash
# Node/pnpm via nvm if not on PATH
export NVM_DIR="$HOME/.nvm"; [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
node --version && pnpm --version
```

### 2. Start PocketBase (backend) on :8090
```bash
cd app/pocketbase
[ -x ./pocketbase ] || bash ../../.devcontainer/setup-pocketbase.sh   # fetch binary if missing
./pocketbase serve --http=0.0.0.0:8090 &     # Admin UI: http://127.0.0.1:8090/_/
```
- First run: create the superuser and import `app/pocketbase/pb_schema.json`, then seed with `/status-local` guidance or `python3 scripts/pb_import.py --apply`.

### 3. Start the Sleek UI (frontend) on :5173
```bash
cd app/web
pnpm install --frozen-lockfile   # first run only
pnpm dev                          # http://localhost:5173
```

### 4. Report
- Print the URLs: backend `http://127.0.0.1:8090`, admin `/_/`, frontend `http://localhost:5173`.
- Remind the user that Phase 2 UI currently reads the bundled `data/` snapshot; wiring the live PocketBase SDK is a Phase 2→3 step.

## Notes
- Long-running servers: run in the background / separate terminals; never block.
- To stop, use `/stop-local`. To check state, use `/status-local`.
