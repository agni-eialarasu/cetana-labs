# Tech — Cetana Labs

## Stack
- **Governance engine:** zero-dependency **Python 3** scripts in `scripts/` (status generation, dashboard, validators, importer). No external Python deps.
- **Relational data layer (`data/`):** JSON masters — `users.json`, `portfolio.json`, `memberships.json` — with Draft-07 JSON Schemas. Source of truth for structural metadata (`RFC-LAB-000-002`).
- **Web app (`BK-008`):**
  - **Backend:** PocketBase (single Go binary + embedded SQLite) under `app/pocketbase/` — schema generated from `data/`.
  - **Frontend ("Sleek UI"):** SvelteKit 5 (Runes) + **pnpm** + Tailwind + `adapter-static`, PocketBase JS SDK, IBM Plex via `@fontsource`, under `app/web/`.
- **CI:** GitHub Actions — `ci-validate.yml` (Python validators + registry/pb-schema/status checks + SvelteKit build). **Deploy:** SvelteKit → **Vercel**, PocketBase → **Railway** (`RFC-LAB-000-011`); the old `deploy-pages.yml` GitHub-Pages dashboard was retired at M5.

## Toolchain notes
- **Node/pnpm** are **Homebrew-managed** and on the default PATH (`/opt/homebrew/bin/node`, `/opt/homebrew/bin/pnpm`) — no `nvm`. (nvm/Volta were removed 2026-09-30 in a toolchain consolidation onto Homebrew; see `~/my-works/WORK_MACHINE_GUIDE.md` §4.) Just run `node`/`pnpm` directly.
- **Task runner:** **`just`** (`justfile`) is the standard task runner across Agni repos (shared-core cross-repo rationale matching Nexus Pulse). Run `just --list` for all available recipes. A thin `Makefile` forwarding shim is maintained for one sprint (`make <target>` forwards to `just <target>`).
- **PocketBase** binary is not committed; fetched by `.devcontainer/setup-pocketbase.sh`. `pb_data/` and the binary are gitignored.
- Local dev runs on a machine (Kiro IDE Executor) or Codespace — not the KiroCrew Operator or the Kiro Web fallback (neither runs persistent servers).

## Key commands
- Validate everything locally: `just validate-local` or `/validate-local` (mirrors CI).
- List tasks: `just --list` (or bare `just`).
- Local stack: `just start-local`, `just stop-local`, `just status-local`.
- Governance validators: `scripts/validate_portfolio.py`, `scripts/project_validate.py`, and the `--check` modes of `generate_registry.py` / `generate_pb_schema.py` / `generate_status_json.py`.
- Web: `pnpm dev` / `pnpm build` / `pnpm check` in `app/web/` (or `just web-dev`, `just web-build`).

## Staging (planned, not yet provisioned)
- Target **GCP** (backend + frontend); optional **Vercel** for frontend quick wins. Begins after the repo transfers to the org account.
