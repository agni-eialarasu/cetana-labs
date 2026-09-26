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
warn "Import collections in the Admin UI: ${PB_URL}/_/  →  Settings → Import collections → paste app/pocketbase/pb_schema.json"
warn "(Programmatic schema import varies by version; the Admin UI import is the reliable path.)"

# ---------------------------------------------------------------------------
say "6/6  Seed data from data/ (dry-run, then apply)"
if [ "$DO_SEED" = "1" ]; then
  export PB_URL PB_ADMIN_EMAIL PB_ADMIN_PASSWORD
  python3 scripts/pb_import.py || warn "dry-run reported issues"
  echo ""
  read -r -p "  Apply the seed now? (requires collections imported above) [y/N] " ans
  if [ "${ans:-N}" = "y" ] || [ "${ans:-N}" = "Y" ]; then
    python3 scripts/pb_import.py --apply && ok "seeded users/projects/memberships" || warn "seed --apply failed (import collections first?)"
  else
    warn "skipped apply — run later: python3 scripts/pb_import.py --apply"
  fi
else
  warn "seed skipped (--no-seed)"
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
