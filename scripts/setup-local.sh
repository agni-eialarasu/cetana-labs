#!/usr/bin/env bash
# Cetana Labs — one-time local development setup (BK-008 / RFC-LAB-000-007)
#
# Idempotent first-run bootstrap for the local stack:
#   toolchain check -> .env -> web deps -> PocketBase superuser -> schema import -> seed.
# Safe to re-run. Uses sensible local-dev defaults; override via env vars or .env.
#
# Usage:
#   bash scripts/setup-local.sh            # full setup with defaults
#   PB_ADMIN_PASSWORD='...' bash scripts/setup-local.sh
#   bash scripts/setup-local.sh --no-seed   # skip the data/ seed
#
# NOTE: run from the repo root. Local dev only (not the Kiro Web sandbox).
set -uo pipefail

# --- Repo root ---
cd "$(cd "$(dirname "$0")/.." && pwd)"
ROOT="$(pwd)"

# --- Defaults (override via environment) ---
PB_URL="${PB_URL:-http://127.0.0.1:8090}"
PB_ADMIN_EMAIL="${PB_ADMIN_EMAIL:-admin@cetana.local}"
PB_ADMIN_PASSWORD="${PB_ADMIN_PASSWORD:-CetanaLocal2026!}"   # >=8 chars (PocketBase requirement)
PB_PORT="${PB_PORT:-8090}"
DO_SEED=1
[ "${1:-}" = "--no-seed" ] && DO_SEED=0

# Prefer a system PocketBase (Homebrew `pocketbase`/`pb`), else the fetched local binary.
PB_BIN="$(command -v pocketbase 2>/dev/null || echo "$ROOT/app/pocketbase/pocketbase")"

say()  { printf "\n\033[1;36m▶ %s\033[0m\n" "$*"; }
ok()   { printf "  \033[1;32m✓\033[0m %s\n" "$*"; }
warn() { printf "  \033[1;33m!\033[0m %s\n" "$*"; }
die()  { printf "  \033[1;31m✗ %s\033[0m\n" "$*"; exit 1; }

# ---------------------------------------------------------------------------
say "0/6  Repo state"
if command -v git >/dev/null 2>&1 && git rev-parse --git-dir >/dev/null 2>&1; then
  HEAD_SHA="$(git log --oneline -1 2>/dev/null)"
  ok "running at: ${HEAD_SHA}"
  # Non-blocking staleness check: warn (don't auto-pull) if origin is ahead.
  git fetch --quiet origin 2>/dev/null || true
  BEHIND="$(git rev-list --count HEAD..@{u} 2>/dev/null || echo 0)"
  if [ "${BEHIND:-0}" -gt 0 ]; then
    warn "you are ${BEHIND} commit(s) BEHIND origin — run 'git pull' to avoid running stale code, then re-run 'make setup'."
  else
    ok "up to date with origin"
  fi
fi

# ---------------------------------------------------------------------------
say "1/6  Toolchain check"
command -v python3 >/dev/null || die "python3 not found"
ok "python3 $(python3 --version 2>&1 | awk '{print $2}')"
# Node/pnpm are Homebrew-native on the work machine; source nvm only as a sandbox fallback.
command -v node >/dev/null 2>&1 || { export NVM_DIR="$HOME/.nvm"; [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"; }
if command -v node >/dev/null 2>&1; then ok "node $(node --version)"; else warn "node not found (web dev will be unavailable)"; fi
if command -v pnpm >/dev/null 2>&1; then ok "pnpm $(pnpm --version)"; else warn "pnpm not found"; fi
if [ -x "$PB_BIN" ] || command -v pocketbase >/dev/null 2>&1; then
  ok "pocketbase $($PB_BIN --version 2>/dev/null | awk '{print $NF}')"
else
  warn "PocketBase binary missing — fetching..."; bash .devcontainer/setup-pocketbase.sh || die "could not obtain PocketBase"
fi

# ---------------------------------------------------------------------------
say "2/6  Environment (.env)"
if [ -f .env ]; then
  ok ".env already exists (leaving as-is)"
else
  cp .env.example .env
  # Apply local-dev defaults into the fresh .env
  sed -i.bak "s#^PB_ADMIN_EMAIL=.*#PB_ADMIN_EMAIL=${PB_ADMIN_EMAIL}#" .env
  sed -i.bak "s#^PB_ADMIN_PASSWORD=.*#PB_ADMIN_PASSWORD=${PB_ADMIN_PASSWORD}#" .env
  rm -f .env.bak
  ok "created .env with local defaults (PB_ADMIN_EMAIL=${PB_ADMIN_EMAIL})"
fi

# ---------------------------------------------------------------------------
say "3/6  Web dependencies"
if command -v pnpm >/dev/null 2>&1; then
  (cd app/web && pnpm install --frozen-lockfile) && ok "pnpm deps installed" || warn "pnpm install failed"
else
  warn "skipping web deps (pnpm unavailable)"
fi

# ---------------------------------------------------------------------------
say "4/6  PocketBase superuser (idempotent)"
# 0.23+: superusers are managed via the `superuser` command. upsert = create-or-update.
if "$PB_BIN" superuser upsert "$PB_ADMIN_EMAIL" "$PB_ADMIN_PASSWORD" >/dev/null 2>&1; then
  ok "superuser ready: $PB_ADMIN_EMAIL"
elif "$PB_BIN" superuser create "$PB_ADMIN_EMAIL" "$PB_ADMIN_PASSWORD" >/dev/null 2>&1; then
  ok "superuser created: $PB_ADMIN_EMAIL"
else
  warn "could not auto-create superuser (may already exist). Verify: $PB_BIN superuser --help"
fi

# ---------------------------------------------------------------------------
say "5/6  Start PocketBase + import collections schema"
# Start a temporary background server to import schema + seed, then leave it running.
"$PB_BIN" serve --http="0.0.0.0:${PB_PORT}" >/tmp/cetana-pb.log 2>&1 &
PB_PID=$!
# Wait for health
for i in $(seq 1 20); do
  curl -sf "${PB_URL}/api/health" >/dev/null 2>&1 && break
  sleep 0.5
done
if curl -sf "${PB_URL}/api/health" >/dev/null 2>&1; then
  ok "PocketBase serving on ${PB_URL} (pid ${PB_PID}, log /tmp/cetana-pb.log)"
else
  die "PocketBase did not become healthy — see /tmp/cetana-pb.log"
fi
# Provision collections programmatically via the API (version-robust; no manual UI import).
export PB_URL PB_ADMIN_EMAIL PB_ADMIN_PASSWORD
if python3 scripts/pb_provision.py --apply; then
  ok "collections provisioned (users, projects, memberships)"
else
  warn "collection provisioning reported issues — see output above"
fi

# ---------------------------------------------------------------------------
say "6/6  Seed data from data/"
if [ "$DO_SEED" = "1" ]; then
  # Collections now exist (step 5), so the seed can apply directly.
  if python3 scripts/pb_import.py --apply; then
    ok "seeded users/projects/memberships from data/"
  else
    warn "seed --apply failed — inspect output; re-run: python3 scripts/pb_import.py --apply"
  fi
else
  warn "seed skipped (--no-seed) — run later: make seed"
fi

# ---------------------------------------------------------------------------
say "Setup complete"
cat <<EOF
  Local stack is ready:
    • PocketBase : ${PB_URL}   (admin: ${PB_URL}/_/  ·  ${PB_ADMIN_EMAIL})
    • Sleek UI   : run 'make web-dev'  → http://localhost:5173
    • Stop PB    : kill ${PB_PID}   (or: make stop-local)

  Credentials are in .env (gitignored). Re-run this script any time (idempotent).
EOF
