# Cetana Labs — Make command layer (RFC-LAB-000-007)
# Mirrors the Kiro /commands so behavior is identical in Web + IDE terminals.
# Targets delegate to the same scripts the skills call (single source of behavior).

.DEFAULT_GOAL := help
SHELL := /bin/bash

# Node/pnpm are provided via nvm and may not be on PATH; source it for web targets.
NVM := export NVM_DIR="$$HOME/.nvm"; [ -s "$$NVM_DIR/nvm.sh" ] && . "$$NVM_DIR/nvm.sh";
# Podman-first, Docker fallback (RFC-LAB-000-007 §2.3).
CONTAINER := $(shell command -v podman 2>/dev/null || command -v docker 2>/dev/null)

.PHONY: help validate-local validate-staging status-local start-local stop-local \
        seed clean-data web-dev web-build pb-serve pb-image env-doctor

help: ## Show this cheat-sheet
	@echo ""
	@echo "  Cetana Labs — command cheat-sheet (make <target>  ==  /<command>)"
	@echo "  ---------------------------------------------------------------"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*?## "}{printf "  %-18s %s\n", $$1, $$2}'
	@echo ""
	@echo "  Governance runs on any surface; server targets need Kiro IDE / local."
	@echo ""

# ---- Validation (mirror /validate-local, /validate-staging) ----
validate-local: ## /validate-local — full local pre-flight (Python validators + web build)
	python3 scripts/validate_portfolio.py
	python3 scripts/generate_registry.py --check
	python3 scripts/generate_pb_schema.py --check
	python3 scripts/generate_status_json.py --check
	python3 scripts/project_validate.py --allow-dirty
	$(NVM) cd app/web && pnpm install --frozen-lockfile && pnpm check && pnpm build

validate-staging: ## /validate-staging — probe staging health (PLACEHOLDER: GCP/Vercel, pending org transfer)
	@echo "Staging not provisioned yet — target GCP (backend+frontend), optional Vercel. See /validate-staging skill."

# ---- Local stack lifecycle (mirror /start-local, /stop-local, /status-local) ----
start-local: ## /start-local — start PocketBase (:8090) + SvelteKit dev (:5173)
	@echo "Starting local stack — see .kiro/skills/start-local for the full procedure."
	@[ -x app/pocketbase/pocketbase ] || bash .devcontainer/setup-pocketbase.sh || true
	@cd app/pocketbase && ./pocketbase serve --http=0.0.0.0:8090 & echo "PocketBase → http://127.0.0.1:8090 (admin /_/)"
	$(NVM) cd app/web && pnpm install --frozen-lockfile && pnpm dev

stop-local: ## /stop-local — stop dev servers (frees :5173 and :8090)
	-@pkill -f "vite" 2>/dev/null || true
	-@pkill -f "pocketbase serve" 2>/dev/null || true
	@echo "Stopped local servers (pb_data preserved)."

status-local: ## /status-local — is the local stack up?
	@pgrep -fl "vite" >/dev/null && echo "Web (:5173): ● ONLINE" || echo "Web (:5173): ○ OFFLINE"
	@pgrep -fl "pocketbase serve" >/dev/null && echo "PocketBase (:8090): ● ONLINE" || echo "PocketBase (:8090): ○ OFFLINE"
	@curl -s -o /dev/null -w "PocketBase health: %{http_code}\n" http://127.0.0.1:8090/api/health 2>/dev/null || echo "PocketBase: unreachable"

# ---- Data (seed / clean) — maps to the data/ relational layer ----
seed: ## Seed PocketBase from data/ (requires PB_ADMIN_* env; runs pb_import --apply)
	python3 scripts/pb_import.py --apply

clean-data: ## Reset local PocketBase data to a clean slate (removes pb_data/)
	@echo "This removes app/pocketbase/pb_data/ (local DB). Ctrl-C to abort."; sleep 3
	rm -rf app/pocketbase/pb_data && echo "Clean slate — re-seed with 'make seed'."

# ---- Web app helpers ----
web-dev: ## SvelteKit dev server only (:5173)
	$(NVM) cd app/web && pnpm install --frozen-lockfile && pnpm dev

web-build: ## SvelteKit production build
	$(NVM) cd app/web && pnpm install --frozen-lockfile && pnpm build

# ---- Containers (Podman-first, Docker fallback — RFC-LAB-000-007 §2.3) ----
pb-serve: ## Run PocketBase directly (binary, no container — the local default)
	cd app/pocketbase && ./pocketbase serve --http=0.0.0.0:8090

pb-image: ## Build the PocketBase container image (Podman-first) for staging/GCP parity
	@[ -n "$(CONTAINER)" ] || { echo "No podman/docker found."; exit 1; }
	$(CONTAINER) build -t cetana-pocketbase -f app/pocketbase/Containerfile app/pocketbase

env-doctor: ## /env-doctor — surface-aware environment readiness check
	@echo "Run the /env-doctor skill for the full surface-aware diagnostic."
	@echo "Quick probe:"; python3 --version; ($(NVM) node --version && pnpm --version) 2>/dev/null || echo "node/pnpm: not on PATH (source nvm)"
	@[ -x app/pocketbase/pocketbase ] && echo "pb binary: present" || echo "pb binary: missing"
	@[ -n "$(CONTAINER)" ] && echo "container engine: $(CONTAINER)" || echo "container engine: none (podman recommended)"
