# Cetana Labs — Make command layer (RFC-LAB-000-007)
# Mirrors the Kiro /commands so behavior is identical in Web + IDE terminals.
# Targets delegate to the same scripts the skills call (single source of behavior).

.DEFAULT_GOAL := help
SHELL := /bin/bash

# Node/pnpm are expected on PATH (Homebrew-native on the MBP work machine; nvm is
# intentionally not used). In cloud sandboxes where Node lives under nvm, source it.
NVM := if ! command -v node >/dev/null 2>&1; then export NVM_DIR="$$HOME/.nvm"; [ -s "$$NVM_DIR/nvm.sh" ] && . "$$NVM_DIR/nvm.sh"; fi;
# PocketBase: prefer a system binary (Homebrew `pocketbase`/`pb`), else the fetched local one.
PB := $(shell command -v pocketbase 2>/dev/null || echo ./pocketbase)
# Podman-first, Docker fallback (RFC-LAB-000-007 §2.3).
CONTAINER := $(shell command -v podman 2>/dev/null || command -v docker 2>/dev/null)

.PHONY: help setup validate-local validate-staging status-local start-local stop-local \
        provision seed clean-data web-dev web-build verify-bundle deploy-staging deploy-adhoc \
        pb-serve pb-image env-doctor

help: ## Show this cheat-sheet
	@echo ""
	@echo "  Cetana Labs — command cheat-sheet (make <target>  ==  /<command>)"
	@echo "  ---------------------------------------------------------------"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*?## "}{printf "  %-18s %s\n", $$1, $$2}'
	@echo ""
	@echo "  Governance runs on any surface; server targets need Kiro IDE / local."
	@echo ""

# ---- One-time setup ----
setup: ## One-time local bootstrap (env, deps, superuser, provision collections, seed) — zero manual steps
	bash scripts/setup-local.sh

# ---- Validation (mirror /validate-local, /validate-staging) ----
validate-local: ## /validate-local — full local pre-flight (Python validators + web build)
	python3 scripts/validate_portfolio.py
	python3 scripts/generate_registry.py --check
	python3 scripts/generate_pb_schema.py --check
	python3 scripts/generate_status_json.py --check
	python3 scripts/project_validate.py --allow-dirty
	$(NVM) cd app/web && pnpm install --frozen-lockfile && pnpm check && pnpm build

validate-staging: ## /validate-staging — probe the staging (single reference) env: Railway backend + Vercel frontend health
	@echo "Staging = the single reference environment (auto-deployed on merge to main):"
	@echo "  backend  → Railway PocketBase (deploy-backend.yml)"
	@echo "  frontend → Vercel (Git integration)"
	@echo "Set PB_URL / WEB_URL in .env.staging to probe health. See the /validate-staging skill."

# ---- Local stack lifecycle (mirror /start-local, /stop-local, /status-local) ----
start-local: ## /start-local — start PocketBase (:8090) + SvelteKit dev (:5173)
	@echo "Starting local stack — see .kiro/skills/start-local for the full procedure."
	@command -v pocketbase >/dev/null 2>&1 || [ -x app/pocketbase/pocketbase ] || bash .devcontainer/setup-pocketbase.sh || true
	@cd app/pocketbase && $(PB) serve --http=0.0.0.0:8090 & echo "PocketBase → http://127.0.0.1:8090 (admin /_/)"
	$(NVM) cd app/web && pnpm install --frozen-lockfile && pnpm dev

stop-local: ## /stop-local — stop dev servers (frees :5173 and :8090)
	-@pkill -f "vite" 2>/dev/null || true
	-@pkill -f "pocketbase serve" 2>/dev/null || true
	@echo "Stopped local servers (pb_data preserved)."

status-local: ## /status-local — is the local stack up?
	@pgrep -fl "vite" >/dev/null && echo "Web (:5173): ● ONLINE" || echo "Web (:5173): ○ OFFLINE"
	@pgrep -fl "pocketbase serve" >/dev/null && echo "PocketBase (:8090): ● ONLINE" || echo "PocketBase (:8090): ○ OFFLINE"
	@curl -s -o /dev/null -w "PocketBase health: %{http_code}\n" http://127.0.0.1:8090/api/health 2>/dev/null || echo "PocketBase: unreachable"

# ---- Data (provision / seed / clean) — maps to the data/ relational layer ----
provision: ## Create PocketBase collections via API (requires PB_ADMIN_* env; version-robust)
	python3 scripts/pb_provision.py --apply

seed: ## Provision collections + seed PocketBase from data/ (requires PB_ADMIN_* env)
	python3 scripts/pb_provision.py --apply
	python3 scripts/pb_import.py --apply

clean-data: ## Reset local PocketBase data to a clean slate (removes pb_data/)
	@echo "This removes app/pocketbase/pb_data/ (local DB). Ctrl-C to abort."; sleep 3
	rm -rf app/pocketbase/pb_data && echo "Clean slate — re-seed with 'make seed'."

# ---- Web app helpers ----
web-dev: ## SvelteKit dev server only (:5173)
	$(NVM) cd app/web && pnpm install --frozen-lockfile && pnpm dev

web-build: ## SvelteKit production build
	$(NVM) cd app/web && pnpm install --frozen-lockfile && pnpm build

# ---- Deploy DX (RFC-LAB-000-012 / BK-017) ----
verify-bundle: ## Assert app/web/build bakes in EXPECTED backend URL (FORBIDDEN optional) — run after web-build
	@[ -n "$(EXPECTED)" ] || { echo "usage: make verify-bundle EXPECTED=<url> [FORBIDDEN=<url>]"; exit 2; }
	bash scripts/verify-bundle.sh "$(EXPECTED)" "$(FORBIDDEN)"

# DEPLOY MODEL (Decision Journal Entry 014, D49–D52) — two deliberately-separated paths:
#
#   1. THE STAGING PIPELINE = THE MERGE.  Merging to `main` auto-deploys BOTH tiers to
#      the single reference environment: frontend via the Vercel Git integration, backend
#      via .github/workflows/deploy-backend.yml (path-filtered to app/pocketbase/**).
#      There is NO manual make target for the normal staging deploy — the merge is it.
#      `deploy-staging` below is only a manual OVERRIDE re-deploy of that same env.
#
#   2. `deploy-adhoc` = an on-demand DEV TOOL to deploy to ANY instance (throwaway/other),
#      parameterized by an env file. NOT a lifecycle stage, NOT "release" (see /deploy-adhoc).

deploy-staging: ## Manual OVERRIDE re-deploy of the staging env (normal staging deploy is AUTOMATIC on merge to main)
	@echo "NOTE: the normal staging deploy is AUTOMATIC on merge to main (Vercel + deploy-backend.yml)."
	@echo "      This target is a manual override re-deploy of that same env — not 'the pipeline'. (Entry 014)"
	bash scripts/deploy.sh all

deploy-adhoc: ## /deploy-adhoc — DEV TOOL: on-demand deploy to ANY instance. usage: make deploy-adhoc ENV=<file> [WHAT=all|deploy-backend|deploy-frontend]
	@[ -n "$(ENV)" ] || { echo "usage: make deploy-adhoc ENV=<env-file> [WHAT=all|deploy-backend|deploy-frontend]"; echo "  (ENV points at a GITIGNORED env file, e.g. .env.throwaway — NOT the staging pipeline; see /deploy-adhoc)"; exit 2; }
	ENV_FILE="$(ENV)" bash scripts/deploy.sh "$(if $(WHAT),$(WHAT),all)"

# ---- Containers (Podman-first, Docker fallback — RFC-LAB-000-007 §2.3) ----
pb-serve: ## Run PocketBase directly (binary, no container — the local default)
	cd app/pocketbase && $(PB) serve --http=0.0.0.0:8090

pb-image: ## Build the PocketBase container image (Podman-first) for local/Railway (Containerfile) parity
	@[ -n "$(CONTAINER)" ] || { echo "No podman/docker found."; exit 1; }
	$(CONTAINER) build -t cetana-pocketbase -f app/pocketbase/Containerfile app/pocketbase

env-doctor: ## /env-doctor — surface-aware environment readiness check
	@echo "Run the /env-doctor skill for the full surface-aware diagnostic."
	@echo "Quick probe:"; python3 --version; ($(NVM) node --version && pnpm --version) 2>/dev/null || echo "node/pnpm: not on PATH (source nvm)"
	@[ -x app/pocketbase/pocketbase ] && echo "pb binary: present" || echo "pb binary: missing"
	@[ -n "$(CONTAINER)" ] && echo "container engine: $(CONTAINER)" || echo "container engine: none (podman recommended)"
