---
name: status-local
description: >-
  Reports the health of the local Cetana Labs dev stack — whether the PocketBase backend and SvelteKit dev server are running, ports, and DB/seed state. Use when the user runs /status-local or asks whether the local app is up.
---

# Skill: Local Dev Stack Status (`/status-local`)

## Objective
Give a quick, factual snapshot of the local development environment: which services are up, on which ports, and whether the PocketBase DB is seeded.

## Trigger Patterns
- `/status-local`
- "is the local app running?", "local dev status"

## Steps

### 1. Process / port checks
```bash
echo "== Frontend (SvelteKit :5173) ==";  pgrep -fl "vite" || echo "  not running"
echo "== Backend (PocketBase :8090) ==";  pgrep -fl "pocketbase serve" || echo "  not running"
```

### 2. Backend reachability + seed state
```bash
curl -s -o /dev/null -w "PocketBase HTTP: %{http_code}\n" http://127.0.0.1:8090/api/health 2>/dev/null || echo "PocketBase: unreachable"
# Seed check (if reachable): count projects
curl -s "http://127.0.0.1:8090/api/collections/projects/records?perPage=1" 2>/dev/null | grep -o '"totalItems":[0-9]*' || true
```

### 3. Local artifacts
```bash
[ -x app/pocketbase/pocketbase ] && echo "pb binary: present" || echo "pb binary: missing (run setup-pocketbase.sh)"
[ -d app/pocketbase/pb_data ] && echo "pb_data: present (seeded)" || echo "pb_data: none (not yet seeded)"
[ -d app/web/node_modules ] && echo "web deps: installed" || echo "web deps: run pnpm install"
```

### 4. Report
Summarize as a short table: Frontend up/down · Backend up/down · DB seeded yes/no · toolchain ready. Suggest `/start-local` if down, `/stop-local` if the user wants to shut down.
