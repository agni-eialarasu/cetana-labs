---
name: validate-local
description: >-
  Runs the full local pre-flight for Cetana Labs — Python governance validators (portfolio, registry, pb-schema, status-json, 5-pillar gate) plus the SvelteKit type-check and build. The single "is everything green locally?" command. Use when the user runs /validate-local or asks to validate before commit/PR.
---

# Skill: Local Pre-Flight Validation (`/validate-local`)

## Objective
One command that runs **every** local check the CI would run, so the user knows a change is green before committing or opening a PR. This is the local mirror of the `pull_request` CI workflow (`.github/workflows/ci-validate.yml`).

## Trigger Patterns
- `/validate-local`
- "validate locally", "run all checks", "pre-flight before PR"

## Steps

### 1. Python governance validators
```bash
python3 scripts/validate_portfolio.py          # structural + protocol + referential integrity
python3 scripts/generate_registry.py --check     # README registry in sync with data/
python3 scripts/generate_pb_schema.py --check     # PocketBase schema in sync with data/
python3 scripts/generate_status_json.py --check    # data/status.json in sync with STATUS.md
python3 scripts/project_validate.py --allow-dirty  # Two-Phase Governance 5-pillar gate
```

### 2. Web app (SvelteKit) checks
```bash
export NVM_DIR="$HOME/.nvm"; [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
cd app/web
pnpm install --frozen-lockfile
pnpm check      # svelte-check (0 errors expected)
pnpm build       # static build must succeed
cd -
```

### 3. Report
- Emit a PASS/FAIL line per check.
- If any `--check` reports "stale", run the matching generator (without `--check`) to regenerate, then re-run.
- Only report "green" when **all** checks pass — a command exiting 0 per step, not an assumption.

## Notes
- This is the pre-flight gate before `/sprint-done` or opening any PR (RFC-LAB-000-004).
- Governance-only changes still run step 1; app changes run both steps.
- **Scope boundary (RFC-LAB-000-007 §2.5):** this validates *work correctness*. If the toolchain/binary isn't set up (e.g. `node`/`pnpm` missing), don't diagnose the environment here — point the user to **`/env-doctor`** and stop.
