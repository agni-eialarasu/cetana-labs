# Deploy Scaffold — Design

> Companion to `requirements.md`. Implements `RFC-LAB-000-012`: CLI deploy config + wrapper, the build-artifact assertion helper, the casual→qualified runbook, and the `status.json` date-drift fix (`BK-020`). Scriptable, secret-free, reproducible.

---

## 1. Approach: small, independent DX pieces

Three loosely-coupled deliverables that can be built/verified in any order (§ in `requirements`):
- **A — CLI deploy scaffold:** `railway.json` + `scripts/deploy.sh` + `make deploy-staging`.
- **B — artifact-assertion helper:** `scripts/verify-bundle.sh` + `make verify-bundle`.
- **C — status-drift fix (`BK-020`):** the highest-value, lowest-risk piece — do it first (it unblocks *every* future PR).

All shell/config/Python; no app-feature code. Secrets never touched in-repo.

## 2. C — status-drift fix (`BK-020`, do first)

**Root cause (verified):** `generate_status_json.py --check` full-string-compares the committed `data/status.json` against a fresh `build()`, and `build()` recomputes `days_ago` from *today* → the file "goes stale" purely by time.

**Chosen fix (OQ-1 lean): stop storing `days_ago`; compute at read-time.**
- `generate_status_json.py build()`: **drop the `days_ago` key** from the emitted record (keep `last_updated`, the source of truth). Regenerate `data/status.json` without it.
- **SPA (`app/web/src/lib/data.ts` + `types.ts`):** where `days_ago` was read from `status.json`, **compute it from `last_updated`** at load (`floor((now - last_updated)/86400000)`). This is *more* correct anyway — the displayed "days ago" is now always current, not frozen at last commit.
- **Result:** the file no longer contains a time-relative field, so `--check` is stable across any elapsed time (R5.2). No manual regenerate for time alone, ever again.
- **Guard:** confirm nothing else consumes stored `days_ago` (grep `scripts/` + `app/web/src`); the `is_stale` flag, if date-derived, is computed the same read-time way or left as-is if parser-sourced.

*(Fallback if compute-at-read proves messy: exclude `days_ago` from the `--check` comparison only — but that leaves a stale value in the file, so compute-at-read is preferred.)*

## 3. A — CLI deploy scaffold

### `railway.json` (repo root or `app/pocketbase/`)
Pin the builder to the Dockerfile so Railway doesn't Railpack-auto-detect (the spike papercut):
```json
{ "build": { "builder": "DOCKERFILE", "dockerfilePath": "app/pocketbase/Containerfile" } }
```
Comment documents the one-time [HUMAN] volume attach at `/pb/pb_data`.

### `scripts/deploy.sh` + `make deploy-staging`
- Reads `.env.staging` (gitignored); errors with the `.example` pointer if missing (R2.3).
- Sub-commands: `deploy-backend` (Railway CLI `up` from `app/pocketbase/` context → sidesteps Root-Directory doubling), `deploy-frontend` (Vercel CLI `deploy`), `all`.
- Captures URLs (`railway domain`/`status`, vercel deploy output); **before trusting the frontend, calls `verify-bundle.sh` (B)**.
- Prints the **irreducibly-manual checklist** (CLI login, Railway volume attach, GitHub OAuth app) — documented, not faked (R2.2).
- `make deploy-staging` → `bash scripts/deploy.sh all` (Makefile cheat-sheet style).
- **Zero secrets in the script**; all creds come from `.env.staging` / CLI-set env.

## 4. B — artifact-assertion helper (the false-negative fix, RFC-012 §5)

`scripts/verify-bundle.sh <expected-url> [<forbidden-url>]`:
```sh
# after `pnpm --dir app/web build`
grep -rq "$EXPECTED" app/web/build || fail "expected backend URL not baked in"
[ -n "$FORBIDDEN" ] && grep -rq "$FORBIDDEN" app/web/build && fail "forbidden backend URL present in bundle"
echo "✅ bundle baked-in backend = $EXPECTED"
```
- Catches exactly the BK-018 false negative (a preview silently carrying the prod `VITE_PB_URL`).
- `make verify-bundle EXPECTED=… FORBIDDEN=…`; also called by `deploy.sh` post-build.

## 5. D — runbook (`developer-guide.md` Deploy Operations)
A new section: the CLI-first flow, the **casual→qualified** lifecycle (throwaway creds → verify → rotate real secrets → qualify), the artifact-verification rule, and the one-time manual steps. Cross-links `RFC-LAB-000-012`.

## 6. Verification (feeds `tasks.md` + `/verification-done`)
Maps to V1–V6: **V1** the status-drift fix is the headline (check passes across elapsed time; SPA still shows correct days-ago); **V2** verify-bundle catches a wrong bundle; V3 railway.json pins the builder; V4 deploy wrapper runs/errs helpfully; V5 runbook followable; V6 no secrets, gates green.

## 7. Trade-offs
| Decision | Chosen | Rejected | Why |
| :--- | :--- | :--- | :--- |
| status fix | drop stored `days_ago`, compute at read-time | exclude from `--check` only | Kills the drift class *and* makes displayed days-ago always-current; leaves no stale field. |
| deploy wrapper | one `deploy.sh` w/ sub-commands + `make` | separate scripts | One entry point; consistent with Makefile. |
| manual steps | document, don't automate | script the un-scriptable | CLI login / volume attach / OAuth are one-time + interactive; faking them causes false confidence. |
| artifact helper | standalone script, called by deploy | inline only | Reusable + independently testable (V2). |
