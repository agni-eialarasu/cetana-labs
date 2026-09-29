#!/usr/bin/env bash
# Cetana Labs — CLI deploy wrapper (RFC-LAB-000-012 / BK-017).
#
# CLI-first staging deploy: backend (PocketBase) to Railway, frontend (SvelteKit)
# to Vercel. Reads config from `.env.staging` (gitignored — NEVER commit secrets).
# The frontend deploy is only trusted after `verify-bundle.sh` confirms the built
# bundle bakes in the expected backend URL (the BK-018 false-negative guard).
#
# Usage:
#   scripts/deploy.sh deploy-backend    # Railway only
#   scripts/deploy.sh deploy-frontend   # Vercel only (builds + verifies bundle first)
#   scripts/deploy.sh all               # backend then frontend  (== make deploy-staging)
#   scripts/deploy.sh checklist         # print the one-time [HUMAN] steps and exit
#
# Config (.env.staging — copy from .env.staging.example):
#   PB_URL        the deployed Railway PocketBase base URL (also the frontend's backend)
#   VITE_PB_URL   backend URL baked into the frontend bundle (normally == PB_URL)
#   FORBIDDEN_PB_URL  (optional) a URL that MUST NOT appear in the bundle (e.g. prod)
#
# SECRETS DISCIPLINE: this script contains NO credentials. Railway/Vercel auth comes
# from `railway login` / `vercel login` (one-time, interactive) and the CLIs' own
# stored tokens. Admin passwords / OAuth secrets live in the Railway service vars and
# the PocketBase admin — never here, never in the repo.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ENV_FILE:-$REPO_ROOT/.env.staging}"
PB_DIR="$REPO_ROOT/app/pocketbase"
WEB_DIR="$REPO_ROOT/app/web"

c_info()  { printf '\033[36m▶ %s\033[0m\n' "$*"; }
c_ok()    { printf '\033[32m✅ %s\033[0m\n' "$*"; }
c_warn()  { printf '\033[33m⚠️  %s\033[0m\n' "$*"; }
die()     { printf '\033[31m❌ deploy: %s\033[0m\n' "$*" >&2; exit 1; }

# --- The irreducibly-manual one-time steps (documented, NOT automated) ---------------
print_checklist() {
  cat <<'EOF'

────────────────────────────────────────────────────────────────────────────
ONE-TIME [HUMAN] STEPS — cannot be scripted (interactive / console-only)
────────────────────────────────────────────────────────────────────────────
  1. CLI login (once per machine):
       railway login          # opens browser
       vercel login
  2. Railway persistent volume (once per service) — CLI CANNOT attach volumes:
       Railway dashboard → PocketBase service → Settings → Volumes →
       attach a Volume mounted at  /pb/pb_data
       (without it, every redeploy wipes the SQLite DB)
  3. GitHub OAuth app (once per environment):
       - create/point a GitHub OAuth app's callback at  <PB_URL>/api/oauth2-redirect
       - set client id/secret in the Railway PocketBase admin
         (Collections → users → Options → OAuth2 → GitHub)
  4. Frontend env in Vercel (once, or via `vercel env add`):
       VITE_PB_URL = <the Railway PB URL>
────────────────────────────────────────────────────────────────────────────
EOF
}

require_cli() {
  command -v "$1" >/dev/null 2>&1 \
    || die "'$1' CLI not found — install it and run 'scripts/deploy.sh checklist' for one-time setup."
}

load_env() {
  if [ ! -f "$ENV_FILE" ]; then
    die "no $ENV_FILE — copy the template and fill it in:
        cp .env.staging.example .env.staging   # then edit (it is gitignored)
     (.env.staging holds the staging URLs; real secrets live in Railway/Vercel, not here.)"
  fi
  # shellcheck disable=SC1090
  set -a; source "$ENV_FILE"; set +a
  : "${PB_URL:?PB_URL must be set in $ENV_FILE}"
  : "${VITE_PB_URL:=$PB_URL}"   # default the bundle backend to PB_URL
}

deploy_backend() {
  require_cli railway
  c_info "Deploying PocketBase → Railway (from app/pocketbase; railway.json pins the Containerfile builder)"
  ( cd "$PB_DIR" && railway up ) \
    || die "railway up failed — are you logged in ('railway login') and linked ('railway link')?"
  c_ok "Backend deploy triggered. Expected backend URL: $PB_URL"
  c_warn "Confirm the Railway Volume is mounted at /pb/pb_data (see checklist) or data is ephemeral."
}

deploy_frontend() {
  require_cli vercel
  c_info "Building frontend with VITE_PB_URL=$VITE_PB_URL"
  ( cd "$WEB_DIR" && VITE_PB_URL="$VITE_PB_URL" pnpm install --frozen-lockfile && VITE_PB_URL="$VITE_PB_URL" pnpm build ) \
    || die "frontend build failed"

  # Trust nothing until the artifact proves it baked in the right backend (BK-018 guard).
  c_info "Verifying the built bundle bakes in the expected backend URL"
  bash "$REPO_ROOT/scripts/verify-bundle.sh" "$VITE_PB_URL" "${FORBIDDEN_PB_URL:-}" \
    || die "bundle verification failed — NOT deploying a frontend baked against the wrong backend."

  c_info "Deploying frontend → Vercel"
  ( cd "$WEB_DIR" && vercel deploy --prebuilt --yes 2>/dev/null || vercel deploy --yes ) \
    || die "vercel deploy failed — are you logged in ('vercel login') and linked ('vercel link')?"
  c_ok "Frontend deploy triggered (bundle verified against $VITE_PB_URL)."
}

main() {
  local cmd="${1:-all}"
  case "$cmd" in
    checklist)        print_checklist ;;
    deploy-backend)   load_env; deploy_backend; print_checklist ;;
    deploy-frontend)  load_env; deploy_frontend; print_checklist ;;
    all)              load_env; deploy_backend; deploy_frontend; print_checklist ;;
    -h|--help|help)
      grep -E '^#( |$)' "$0" | sed -E 's/^# ?//' | head -n 30 ;;
    *) die "unknown command '$cmd' — use: deploy-backend | deploy-frontend | all | checklist" ;;
  esac
}

main "$@"
