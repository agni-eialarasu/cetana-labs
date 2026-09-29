#!/usr/bin/env bash
# Cetana Labs — build-artifact assertion helper (RFC-LAB-000-012 §5, BK-017).
#
# Asserts that the built SvelteKit bundle (app/web/build/) has the EXPECTED backend
# URL baked in (VITE_PB_URL, inlined at build time), and — optionally — does NOT
# contain a FORBIDDEN backend URL. This catches the exact BK-018 false negative: a
# preview/staging bundle silently carrying the wrong (e.g. prod) VITE_PB_URL, which
# no health check on the running service would ever reveal.
#
# Usage:
#   scripts/verify-bundle.sh <expected-url> [<forbidden-url>]
#   make verify-bundle EXPECTED=https://staging.example [FORBIDDEN=https://prod.example]
#
# Exit codes: 0 = bundle OK; 1 = assertion failed; 2 = usage / missing build.
#
# NOTE: run AFTER `pnpm --dir app/web build`. This script never builds; it only
# inspects the emitted artifact so the assertion is about what actually ships.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${BUILD_DIR:-$REPO_ROOT/app/web/build}"

fail() { echo "❌ verify-bundle: $*" >&2; exit 1; }

EXPECTED="${1:-${EXPECTED:-}}"
FORBIDDEN="${2:-${FORBIDDEN:-}}"

if [ -z "$EXPECTED" ]; then
  echo "usage: scripts/verify-bundle.sh <expected-url> [<forbidden-url>]" >&2
  echo "   or: make verify-bundle EXPECTED=<url> [FORBIDDEN=<url>]" >&2
  exit 2
fi

if [ ! -d "$BUILD_DIR" ]; then
  echo "❌ verify-bundle: no build at $BUILD_DIR — run 'pnpm --dir app/web build' first." >&2
  exit 2
fi

echo "🔎 verify-bundle: inspecting $BUILD_DIR"
echo "   expected backend : $EXPECTED"
[ -n "$FORBIDDEN" ] && echo "   forbidden backend: $FORBIDDEN"

# R3.1 — the expected backend URL MUST be baked into the shipped bundle.
if ! grep -rqF -- "$EXPECTED" "$BUILD_DIR"; then
  fail "expected backend URL not found in bundle: $EXPECTED
        the frontend was NOT built against this backend (check VITE_PB_URL at build time)."
fi

# R3.1 — a specified other-backend URL MUST NOT be present (the BK-018 false negative).
if [ -n "$FORBIDDEN" ] && grep -rqF -- "$FORBIDDEN" "$BUILD_DIR"; then
  fail "forbidden backend URL present in bundle: $FORBIDDEN
        the bundle is baked against the wrong backend — do NOT deploy it."
fi

echo "✅ verify-bundle: bundle baked-in backend = $EXPECTED (no forbidden URL present)"
