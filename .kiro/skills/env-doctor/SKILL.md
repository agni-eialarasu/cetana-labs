---
name: env-doctor
description: >-
  Surface-aware environment readiness check for Cetana Labs — reports whether the CURRENT surface (Kiro Web vs Kiro IDE) has what it needs (toolchain versions, PocketBase binary, container engine, git sync, secrets). Diagnostic-only; never runs validators or builds. Use when the user runs /env-doctor or asks "is my environment set up / why isn't X working".
---

# Skill: Environment Doctor (`/env-doctor`)

## Objective
Answer one question: **"Can I work correctly on the surface I'm on right now?"** Probe the environment, report readiness, and tell the user exactly what to fix. This is **readiness diagnosis only** — it does NOT run the governance validators or the SvelteKit build (that is `/validate-local`). If work-correctness is the question, defer to `/validate-local`; if staging health is the question, defer to `/validate-staging` (RFC-LAB-000-007 §2.5).

## Trigger Patterns
- `/env-doctor`
- "is my environment set up?", "why isn't node/pocketbase working?", "check my setup"

## Steps

### 1. Detect the surface
- If there is no local filesystem / running-server capability (cloud sandbox), treat as **Kiro Web (stateless)**; otherwise **Kiro IDE / local (stateful)**.
- State which surface was detected and what "ready" means for it (RFC-LAB-000-007 §2.1).

### 2. Universal checks (both surfaces)
```bash
python3 --version                      # 3.11+ expected
git rev-parse --abbrev-ref HEAD; git status --short   # branch + cleanliness
git rev-list --left-right --count @{u}...HEAD 2>/dev/null || echo "no upstream"
[ -d .kiro/skills ] && echo ".kiro/skills: present" || echo ".kiro/skills: MISSING"
[ -f .nvmrc ] && echo ".nvmrc: $(cat .nvmrc)" || echo ".nvmrc: missing"
```

### 3. Surface-specific checks
**Kiro Web (stateless — governance/docs):**
- Confirm Python + governance scripts are runnable; note that servers / PocketBase binary are **not expected here** (report as "n/a for this surface", not a failure).
- Personal `~/.kiro/` config comes via Configuration Sync (remind if personal skills seem missing).

**Kiro IDE / local (stateful — servers):**
```bash
export NVM_DIR="$HOME/.nvm"; [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
node --version; pnpm --version                 # match .nvmrc / packageManager
[ -x app/pocketbase/pocketbase ] && echo "pb binary: present" || echo "pb binary: missing (bash .devcontainer/setup-pocketbase.sh)"
command -v podman || command -v docker || echo "container engine: none (podman recommended)"
[ -f .env ] && echo ".env: present" || echo ".env: missing (cp .env.example .env)"
[ -d app/web/node_modules ] && echo "web deps: installed" || echo "web deps: run pnpm install"
```

### 4. Report
- A per-check ✅ / ⚠️ / ❌ table, headed by the detected surface.
- Mark surface-irrelevant items as **n/a** (e.g. PocketBase binary on Web) — not failures.
- End with a short "To be fully ready here: …" fix list, and point to `/validate-local` for the actual work-correctness gate.

## Rules
- **Read-only.** Never mutate state, never run validators/builds/servers.
- Be honest about surface limits (Web can't run persistent servers) rather than flagging them as errors.
