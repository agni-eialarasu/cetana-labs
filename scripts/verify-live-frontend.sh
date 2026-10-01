#!/usr/bin/env bash
# Cetana Labs — LIVE frontend assertion (RFC-LAB-000-012, BK-023 part 2 / TSK-063).
#
# The post-deploy backstop (option B) to the /review-pr Vercel-status gate (option C):
#   C answers "did Vercel's build/deploy for this commit SUCCEED?" (pre-merge, at the gate).
#   B answers "is the RIGHT bundle actually SERVED on the live site?" (post-merge, here).
#
# This reuses the scripts/verify-bundle.sh idea (BK-017) but inspects the LIVE Vercel
# site instead of the local app/web/build/ artifact — so it catches a deploy that
# "succeeded" yet served the wrong backend, or regressed the OAuth flow.
#
# ASSERTIONS (against the live, served bundle):
#   1. the served JS references the EXPECTED VITE_PB_URL (the Railway PocketBase)  — positive
#   2. (optional) a FORBIDDEN backend URL is NOT present                           — negative
#   3. (optional) the realtime-popup OAuth call-site is NOT present                — negative
#
# On #3 — IMPORTANT (verified against the live bundle, 2026-10-01): the PocketBase JS
# SDK ALWAYS ships BOTH the string "/api/realtime" (its realtime subscription client)
# AND the method definitions `authWithOAuth2(` / `authWithOAuth2Code(` — regardless of
# which auth flow OUR app actually calls. So asserting the bare presence/absence of any
# of those strings is a FALSE POSITIVE (they are SDK-internal, not app-call evidence).
# Therefore #3 is OPT-IN and OFF BY DEFAULT: set FORBID_OAUTH_PATTERN=<string> only if
# you have an app-specific, distinctive marker to forbid. The AUTHORITATIVE signal of a
# correct deploy is assertion #1 — the expected VITE_PB_URL baked into the served bundle
# (mirroring verify-bundle.sh / BK-017, which also keys on the backend URL).
#
# Usage:
#   scripts/verify-live-frontend.sh <live-url> [<expected-pb-url>]
#   # env overrides:
#   #   EXPECTED_PB_URL=<url>         (else arg 2, else VITE_PB_URL in env)
#   #   FORBIDDEN_PB_URL=<url>        (optional negative assertion)
#   #   FORBID_OAUTH_PATTERN=<string> (OPTIONAL, off by default — see note below)
#
# Examples:
#   scripts/verify-live-frontend.sh https://cetana-labs.vercel.app https://my-pb.up.railway.app
#   EXPECTED_PB_URL=https://my-pb.up.railway.app scripts/verify-live-frontend.sh https://cetana-labs.vercel.app
#
# Exit codes: 0 = live bundle OK; 1 = assertion failed; 2 = usage / fetch error.
#
# OPS-ALERT, NOT A GATE: run this POST-MERGE (on demand or via the workflow). A failure
# here is a red check + logs to investigate — it NEVER reverts the already-merged
# commit (`done` = the gated merge; Decision Journal Entry 014, D50). It is deliberately
# NOT part of the PR-gating CI job (RFC-LAB-000-009 R5.2).
set -euo pipefail

fail()  { echo "❌ verify-live-frontend: $*" >&2; exit 1; }
usage() {
  echo "usage: scripts/verify-live-frontend.sh <live-url> [<expected-pb-url>]" >&2
  echo "   env: EXPECTED_PB_URL=<url> [FORBIDDEN_PB_URL=<url>] [FORBID_OAUTH_PATTERN=<regex>]" >&2
  exit 2
}

URL="${1:-}"
[ -n "$URL" ] || usage
# strip a single trailing slash for clean concatenation
URL="${URL%/}"

EXPECTED="${2:-${EXPECTED_PB_URL:-${VITE_PB_URL:-}}}"
FORBIDDEN="${FORBIDDEN_PB_URL:-}"
# OPT-IN only: the SDK ships authWithOAuth2(/authWithOAuth2Code/ /api/realtime regardless
# of our flow, so there is no reliable DEFAULT negative here — leave empty unless the
# caller supplies an app-specific marker. (See the header note on #3.)
FORBID_OAUTH_PATTERN="${FORBID_OAUTH_PATTERN:-}"

if [ -z "$EXPECTED" ]; then
  echo "❌ verify-live-frontend: no expected PB URL." >&2
  echo "   pass it as arg 2, or set EXPECTED_PB_URL / VITE_PB_URL." >&2
  usage
fi

command -v curl >/dev/null 2>&1 || fail "curl is required but not found on PATH."

echo "🔎 verify-live-frontend: inspecting live site $URL"
echo "   expected backend : $EXPECTED"
[ -n "$FORBIDDEN" ] && echo "   forbidden backend: $FORBIDDEN"
[ -n "$FORBID_OAUTH_PATTERN" ] && echo "   forbid OAuth call: $FORBID_OAUTH_PATTERN (opt-in; SDK's own method/realtime strings are expected & NOT this)"

CURL=(curl -fsSL --retry 2 --retry-delay 2 --max-time 30)

# 1. Fetch the landing HTML (the SPA shell).
HTML="$("${CURL[@]}" "$URL/" 2>/dev/null)" \
  || fail "could not fetch $URL/ — is the site live? (deploy may be in-flight or failed)"

# 2. Discover the JS bundle(s) the shell loads (SvelteKit emits hashed modules under
#    /_app/immutable/). Collect both the modulepreload/script srcs and any immutable paths.
ASSETS="$(printf '%s\n' "$HTML" | grep -oE '/_app/immutable/[A-Za-z0-9._/-]+\.js' | sort -u)"

# Fallback: if the shell inlines nothing (unlikely), scan the HTML itself.
HAYSTACK="$HTML"
FETCHED=0
while IFS= read -r asset; do
  [ -n "$asset" ] || continue
  if BODY="$("${CURL[@]}" "$URL$asset" 2>/dev/null)"; then
    HAYSTACK="$HAYSTACK"$'\n'"$BODY"
    FETCHED=$((FETCHED + 1))
  fi
done <<EOF
$ASSETS
EOF
echo "   fetched bundles  : $FETCHED JS module(s) from the live shell"

if [ "$FETCHED" -eq 0 ]; then
  echo "⚠️  verify-live-frontend: found no /_app/immutable/*.js in the shell; asserting against the HTML only." >&2
fi

# ── Assertion 1 (R2.1): the EXPECTED backend URL must be present in what is served.
if ! printf '%s' "$HAYSTACK" | grep -qF -- "$EXPECTED"; then
  fail "expected backend URL NOT found in the live bundle: $EXPECTED
        the deployed frontend is not pointed at this backend (check VITE_PB_URL in the Vercel project env)."
fi
echo "   ✓ expected backend URL present in live bundle"

# ── Assertion 2 (R2.3, optional): a forbidden backend URL must NOT be present.
if [ -n "$FORBIDDEN" ] && printf '%s' "$HAYSTACK" | grep -qF -- "$FORBIDDEN"; then
  fail "forbidden backend URL present in the live bundle: $FORBIDDEN
        the live frontend is baked against the wrong backend."
fi
[ -n "$FORBIDDEN" ] && echo "   ✓ forbidden backend URL absent"

# ── Assertion 3 (R2.1, OPT-IN only): a caller-supplied forbidden OAuth marker.
#    Off by default — the SDK's own authWithOAuth2(/ /api/realtime strings are always
#    present and are NOT evidence of our app's flow (see header note). Only runs when
#    the caller sets FORBID_OAUTH_PATTERN to an app-specific marker.
if [ -n "$FORBID_OAUTH_PATTERN" ] && printf '%s' "$HAYSTACK" | grep -qF -- "$FORBID_OAUTH_PATTERN"; then
  fail "forbidden OAuth marker present in the live bundle: $FORBID_OAUTH_PATTERN
        a regression of the realtime-popup OAuth flow (BK-018) may be back — the fixed flow uses authWithOAuth2Code (redirect)."
fi
[ -n "$FORBID_OAUTH_PATTERN" ] && echo "   ✓ forbidden OAuth marker absent"

echo "✅ verify-live-frontend: $URL serves the expected bundle (backend = $EXPECTED)"
