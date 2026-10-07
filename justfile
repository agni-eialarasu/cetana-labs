# Cetana Labs — just task runner (RFC-LAB-000-007). Shared Agni core first; Cetana extras below.
set shell := ["/bin/bash", "-c"]

# --- resolved toolchain vars (mirror the Makefile's; Homebrew-first with sandbox fallbacks) ---
PYTHON := env_var_or_default("PYTHON", "python3")
PB := `command -v pocketbase 2>/dev/null || echo ./pocketbase`
CONTAINER := `command -v podman 2>/dev/null || command -v docker 2>/dev/null || true`

# Node/pnpm are expected on PATH (Homebrew-native on the MBP work machine; nvm is
# intentionally not used). In cloud sandboxes where Node lives under nvm, source it.
NVM := 'if ! command -v node >/dev/null 2>&1; then export NVM_DIR="$HOME/.nvm"; [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"; fi;'

default:
    @just --list

# ============================================================
# SHARED AGNI CORE — identical recipe names across all repos. DO NOT RENAME.
# ============================================================

# Show this cheat-sheet (mirror help -> @just --list)
help:
    @just --list

# /start-local — start PocketBase (:8090) + SvelteKit dev (:5173)
start-local:
    @echo "Starting local stack — see .kiro/skills/start-local for the full procedure."
    @command -v pocketbase >/dev/null 2>&1 || [ -x app/pocketbase/pocketbase ] || bash .devcontainer/setup-pocketbase.sh || true
    @cd app/pocketbase && {{PB}} serve --http=0.0.0.0:8090 & echo "PocketBase → http://127.0.0.1:8090 (admin /_/)"
    {{NVM}} cd app/web && pnpm install --frozen-lockfile && pnpm dev

# /stop-local — stop dev servers (frees :5173 and :8090)
stop-local:
    -@pkill -f "vite" 2>/dev/null || true
    -@pkill -f "pocketbase serve" 2>/dev/null || true
    @echo "Stopped local servers (pb_data preserved)."

# /status-local — is the local stack up?
status-local:
    @pgrep -fl "vite" >/dev/null && echo "Web (:5173): ● ONLINE" || echo "Web (:5173): ○ OFFLINE"
    @pgrep -fl "pocketbase serve" >/dev/null && echo "PocketBase (:8090): ● ONLINE" || echo "PocketBase (:8090): ○ OFFLINE"
    @curl -s -o /dev/null -w "PocketBase health: %{http_code}\n" http://127.0.0.1:8090/api/health 2>/dev/null || echo "PocketBase: unreachable"

# /validate-local — full local pre-flight (Python validators + web build)
validate-local:
    {{PYTHON}} scripts/validate_portfolio.py
    {{PYTHON}} scripts/generate_registry.py --check
    {{PYTHON}} scripts/generate_pb_schema.py --check
    {{PYTHON}} scripts/generate_status_json.py --check
    {{PYTHON}} scripts/project_validate.py --allow-dirty
    {{NVM}} cd app/web && pnpm install --frozen-lockfile && pnpm check && pnpm build

# /validate-staging — probe the staging (single reference) env: Railway backend + Vercel frontend health
validate-staging:
    @echo "Staging = the single reference environment (auto-deployed on merge to main):"
    @echo "  backend  → Railway PocketBase (deploy-backend.yml)"
    @echo "  frontend → Vercel (Git integration)"
    @echo "Set PB_URL / WEB_URL in .env.staging to probe health. See the /validate-staging skill."

# Reset local PocketBase data to a clean slate (removes pb_data/)
clean-data:
    @echo "This removes app/pocketbase/pb_data/ (local DB). Ctrl-C to abort."; sleep 3
    rm -rf app/pocketbase/pb_data && echo "Clean slate — re-seed with 'just seed'."

# ============================================================
# CETANA-SPECIFIC RECIPES (below the core; may differ per repo)
# ============================================================

# One-time local bootstrap (env, deps, superuser, provision collections, seed) — zero manual steps
setup:
    bash scripts/setup-local.sh

# Create PocketBase collections via API (requires PB_ADMIN_* env; version-robust)
provision:
    {{PYTHON}} scripts/pb_provision.py --apply

# Provision collections + seed PocketBase from data/ (requires PB_ADMIN_* env)
seed:
    {{PYTHON}} scripts/pb_provision.py --apply
    {{PYTHON}} scripts/pb_import.py --apply

# SvelteKit dev server only (:5173)
web-dev:
    {{NVM}} cd app/web && pnpm install --frozen-lockfile && pnpm dev

# SvelteKit production build
web-build:
    {{NVM}} cd app/web && pnpm install --frozen-lockfile && pnpm build

# Assert app/web/build bakes in EXPECTED backend URL (FORBIDDEN optional) — run after web-build
verify-bundle EXPECTED="" FORBIDDEN="":
    #!/bin/bash
    raw_exp="{{EXPECTED}}"
    [ -n "$raw_exp" ] || raw_exp="$EXPECTED"
    raw_forb="{{FORBIDDEN}}"
    [ -n "$raw_forb" ] || raw_forb="$FORBIDDEN"
    exp="${raw_exp#EXPECTED=}"
    forb="${raw_forb#FORBIDDEN=}"
    if [ -z "$exp" ]; then
        echo "usage: just verify-bundle EXPECTED=<url> [FORBIDDEN=<url>]"
        exit 2
    fi
    bash scripts/verify-bundle.sh "$exp" "$forb"

# Assert the LIVE Vercel site serves the EXPECTED backend URL (post-deploy ops-alert, BK-023)
verify-live-frontend URL="" EXPECTED="":
    #!/bin/bash
    raw_url="{{URL}}"
    [ -n "$raw_url" ] || raw_url="$URL"
    raw_exp="{{EXPECTED}}"
    [ -n "$raw_exp" ] || raw_exp="$EXPECTED"
    url_val="${raw_url#URL=}"
    exp_val="${raw_exp#EXPECTED=}"
    if [ -z "$url_val" ]; then
        echo "usage: just verify-live-frontend URL=<live-url> [EXPECTED=<pb-url>]"
        exit 2
    fi
    bash scripts/verify-live-frontend.sh "$url_val" "$exp_val"

# Manual OVERRIDE re-deploy of the staging env (normal staging deploy is AUTOMATIC on merge to main)
deploy-staging:
    @echo "NOTE: the normal staging deploy is AUTOMATIC on merge to main (Vercel + deploy-backend.yml)."
    @echo "      This recipe is a manual override re-deploy of that same env — not 'the pipeline'. (Entry 014)"
    bash scripts/deploy.sh all

# /deploy-adhoc — DEV TOOL: on-demand deploy to ANY instance. usage: just deploy-adhoc ENV=<env-file> [WHAT=all|deploy-backend|deploy-frontend]
deploy-adhoc ENV="" WHAT="all":
    #!/bin/bash
    raw_env="{{ENV}}"
    [ -n "$raw_env" ] || raw_env="$ENV"
    raw_what="{{WHAT}}"
    [ -n "$raw_what" ] && [ "$raw_what" != "all" ] || raw_what="${WHAT:-all}"
    env_val="${raw_env#ENV=}"
    what_val="${raw_what#WHAT=}"
    [ -n "$what_val" ] || what_val="all"
    if [ -z "$env_val" ]; then
        echo "usage: just deploy-adhoc ENV=<env-file> [WHAT=all|deploy-backend|deploy-frontend]"
        echo "  (ENV points at a GITIGNORED env file, e.g. .env.throwaway — NOT the staging pipeline; see /deploy-adhoc)"
        exit 2
    fi
    ENV_FILE="$env_val" bash scripts/deploy.sh "$what_val"

# Run PocketBase directly (binary, no container — the local default)
pb-serve:
    cd app/pocketbase && {{PB}} serve --http=0.0.0.0:8090

# Build the PocketBase container image (Podman-first) for local/Railway (Containerfile) parity
pb-image:
    #!/bin/bash
    container="{{CONTAINER}}"
    if [ -z "$container" ]; then
        echo "No podman/docker found."
        exit 1
    fi
    $container build -t cetana-pocketbase -f app/pocketbase/Containerfile app/pocketbase

# /env-doctor — surface-aware environment readiness check
env-doctor:
    @echo "Run the /env-doctor skill for the full surface-aware diagnostic."
    @echo "Quick probe:"; {{PYTHON}} --version; ({{NVM}} node --version && pnpm --version) 2>/dev/null || echo "node/pnpm: not on PATH (source nvm)"
    @[ -x app/pocketbase/pocketbase ] && echo "pb binary: present" || echo "pb binary: missing"
    @[ -n "{{CONTAINER}}" ] && echo "container engine: {{CONTAINER}}" || echo "container engine: none (podman recommended)"
