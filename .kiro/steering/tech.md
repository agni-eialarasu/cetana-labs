# Tech — Cetana Labs

## Stack
- **Governance engine:** zero-dependency **Python 3** scripts in `scripts/` (status generation, dashboard, validators, importer). No external Python deps.
- **Relational data layer (`data/`):** JSON masters — `users.json`, `portfolio.json`, `memberships.json` — with Draft-07 JSON Schemas. Source of truth for structural metadata (`RFC-LAB-000-002`).
- **Web app (`BK-008`):**
  - **Backend:** PocketBase (single Go binary + embedded SQLite) under `app/pocketbase/` — schema generated from `data/`.
  - **Frontend ("Sleek UI"):** SvelteKit 5 (Runes) + **pnpm** + Tailwind + `adapter-static`, PocketBase JS SDK, IBM Plex via `@fontsource`, under `app/web/`.
- **CI:** GitHub Actions — `ci-validate.yml` (Python validators + registry/pb-schema/status checks + SvelteKit build) and `deploy-pages.yml` (combined dashboard + Sleek UI to GitHub Pages).

## Toolchain notes
- **Node/pnpm** are provided via **nvm** (`$HOME/.nvm`) and are NOT on the default PATH — source `nvm.sh` before `node`/`pnpm`.
- **PocketBase** binary is not committed; fetched by `.devcontainer/setup-pocketbase.sh`. `pb_data/` and the binary are gitignored.
- Local dev runs on a machine/Codespace, not the Kiro Web sandbox.

## Key commands
- Validate everything locally: `/validate-local` (mirrors CI).
- Governance validators: `scripts/validate_portfolio.py`, `scripts/project_validate.py`, and the `--check` modes of `generate_registry.py` / `generate_pb_schema.py` / `generate_status_json.py`.
- Web: `pnpm dev` / `pnpm build` / `pnpm check` in `app/web/`.

## Staging (planned, not yet provisioned)
- Target **GCP** (backend + frontend); optional **Vercel** for frontend quick wins. Begins after the repo transfers to the org account.
