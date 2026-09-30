# Cetana Labs — Sleek UI (SvelteKit → Vercel)

The executive portfolio SPA. SvelteKit static SPA (`adapter-static`) → **Vercel**;
reads PocketBase → **Railway** at runtime via `VITE_PB_URL`. See
[`docs/guides/developer-guide.md`](../../docs/guides/developer-guide.md) §9 / §9A for the
deployment model, and [`RFC-LAB-000-011`](../../docs/rfc/RFC-LAB-000-011-deployment.md).

## Local dev
```bash
pnpm install
pnpm dev        # :5173 (prebuild copies repo data/ → static/data/)
pnpm check      # type-check
pnpm build      # static build → build/
```

## Vercel deployment config (`vercel.json`)

`vercel.json` pins the build so it is **repo config, not a per-project dashboard setting**:

| Key | Value | Why |
| :--- | :--- | :--- |
| `framework` | `null` | We use `adapter-static` — bypass Vercel's SvelteKit auto-detection. |
| `outputDirectory` | `build` | `adapter-static` writes to `build/`; Vercel defaults to `dist/` and fails *"No Output Directory named dist"* (the M5 papercut). |
| `buildCommand` | `pnpm build` | — |
| `installCommand` | `pnpm install --frozen-lockfile` | — |
| `rewrites` | `/(.*) → /index.html` | **SPA fallback (BK-023).** `adapter-static` emits `fallback: index.html`, but Vercel (`framework:null`) 404s on client-side deep routes with no matching file (e.g. `/oauth/callback` — the OAuth return leg, and the `(member)` routes). This rewrite sends unmatched paths to the SPA shell so client-side routing resolves them. Static assets (existing files, `_app/…`) are served directly — the rewrite only catches paths with no file. |

- The Vercel project **Root Directory must be `app/web`**; the app is served at the domain root, so `BASE_PATH` stays empty.
- **Do NOT add a `"//"` comment key (or any non-schema property) to `vercel.json`.** Vercel validates the file against its schema and **fails the build** on additional properties (*"should NOT have additional property"*) — this silently broke every deploy from commit `3ff88fc` until `BK-023`. Keep `vercel.json` schema-pure; put rationale here instead.

Refs: `RFC-LAB-000-011` (Vercel + Railway), `RFC-LAB-000-012` (deploy ops), `BK-023`.
