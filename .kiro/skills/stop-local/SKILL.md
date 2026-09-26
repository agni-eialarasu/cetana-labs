---
name: stop-local
description: >-
  Stops the local Cetana Labs development stack — the PocketBase backend and the SvelteKit dev server. Use when the user runs /stop-local or asks to shut down / stop the local app.
---

# Skill: Stop Local Dev Stack (`/stop-local`)

## Objective
Cleanly shut down the local development servers started by `/start-local` (PocketBase on :8090 and the SvelteKit dev server on :5173), leaving data intact.

## Trigger Patterns
- `/stop-local`
- "stop the local app", "shut down the dev servers"

## Steps

### 1. Stop the frontend (Vite/SvelteKit :5173)
```bash
pkill -f "vite" 2>/dev/null || true
```

### 2. Stop PocketBase (:8090)
```bash
pkill -f "pocketbase serve" 2>/dev/null || true
```

### 3. Verify ports are free
```bash
for p in 5173 8090; do
  (command -v lsof >/dev/null && lsof -i :$p) || (command -v ss >/dev/null && ss -ltnp | grep ":$p ") || echo "port $p: free"
done
```

### 4. Report
- Confirm both servers stopped.
- Note that PocketBase data (`app/pocketbase/pb_data/`) is preserved on disk (gitignored) — restarting with `/start-local` resumes the same DB.

## Notes
- Non-destructive: this never deletes `pb_data/`. To reset data, remove `app/pocketbase/pb_data/` manually and re-import via `scripts/pb_import.py --apply`.
