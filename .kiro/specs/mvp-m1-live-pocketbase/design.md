# M1 — Wire Sleek UI to Live PocketBase — Design

> Companion to `requirements.md` (the EARS DoD). Covers the technical approach, interfaces, and trade-offs for flipping `app/web/src/lib/data.ts` from static snapshots to the PocketBase JS SDK, while status stays snapshot-sourced (M1 scope).

---

## 1. Current state (verified)

- **Data layer:** `app/web/src/lib/data.ts` exposes `loadProjects(fetch): Promise<Project[]>`, called by `src/routes/+page.ts`'s `load`. It fetches `${base}/data/{users,portfolio,status}.json`, builds `Map`s, merges, derives (`severity`/`priority_score`/`tags`/…), and sorts.
- **Snapshots:** `app/web/scripts/copy-data.js` copies repo `data/*.json` into `static/data/` on `predev`/`prebuild`.
- **App shape:** static SPA — `+layout.ts` sets `ssr = false; prerender = true`. So data access is **client-side**; env vars must be `VITE_`-prefixed to reach the browser bundle.
- **SDK:** `pocketbase@^0.26.0` is already in `app/web/package.json` `dependencies` (no install needed).
- **PocketBase schema** (`scripts/pb_provision.py`): `projects` uses `lab_id` (pattern `^LAB-\d{3}$`), `slug`, `name`, `descriptor`, `archetype`, `owner` (relation→`users`), `repo_url`, `reference_url`, `dev_environment`, `status_source`; `list/viewRule = @request.auth.id != ""`. `users` (auth) adds `seed_id`, `name`, `github_handle`, `role`, `org`, `active`.

## 2. Design decision: how M1 reads before auth exists

Requirement §3 flags that seeded `projects` rules are authenticated-only, but M1 has no auth. **Chosen approach (resolving OQ-1, leaning (a)):**

- **Open the `projects` `listRule`/`viewRule` to public (`""`) via `pb_provision.py`.** This is the *eventual public-summary tier* anyway (`RFC-LAB-000-008` §4, "public / anon → read portfolio summaries"), so M1 is bringing a planned rule forward, not inventing a temporary hack. Field-level public-vs-authenticated granularity is refined in **M3** (noted in the provision comment).
- **`users` stays authenticated-only**, so M1 reads projects with `expand: 'owner'` — but the expand of an authenticated-only relation may be stripped for anon requests. **Mitigation:** the design does not depend on `users` being public; owner display fields are the only need, so if the expand is unavailable to anon, `pb_provision.py` opens `users` `viewRule` to public as well for the seeded, non-sensitive display fields (name/github_handle). This is scoped in the provision change and documented as M3-refinable.

> This keeps M1 **self-contained and locally testable with an anonymous client**, exercises the real SDK read path, and moves only rules that are on the public roadmap. The alternative (defer live read to M2) was rejected because it couples the highest-leverage step to auth, defeating M1's purpose.

**Fallback (R5):** retain the existing snapshot code path behind an env switch. If the PB URL is unreachable or returns zero records, `loadProjects` logs a warning and falls back to `fetchJson` snapshots — preserving the dual-run posture (`RFC-LAB-000-008` §9.4) and guaranteeing the dashboard never blanks.

## 3. Target `data.ts` structure

Introduce a thin PocketBase source alongside the existing derivation, preserving the public `loadProjects(fetch): Promise<Project[]>` contract (R5.2).

```
loadProjects(fetch)
  ├─ loadProjectRecords(fetch)          # NEW: source switch
  │    ├─ if PB configured & reachable → loadFromPocketBase()   # SDK path
  │    └─ else → loadFromSnapshot(fetch)                        # existing fetchJson path (fallback)
  ├─ loadStatuses(fetch)                # UNCHANGED: status.json (M1 keeps status snapshot-sourced)
  └─ merge + derive + sort              # UNCHANGED helpers (severityFor/priorityScore/tagsFor/…)
```

### 3.1 PocketBase client
```ts
import PocketBase from 'pocketbase';
const PB_URL = import.meta.env.VITE_PB_URL ?? 'http://127.0.0.1:8090';   // R4.1
const pb = new PocketBase(PB_URL);
pb.autoCancellation(false);   // avoid auto-cancel on the single portfolio load
```

### 3.2 Fetch + map
```ts
// R1.1 / R1.2 / R1.3
const records = await pb.collection('projects').getFullList({ expand: 'owner' });
const users: User[] = [];      // built from expanded owners (dedup by seed_id)
const projects: ProjectRecord[] = records.map((r) => ({
  id: r.lab_id,                       // lab_id → UI id
  slug: r.slug,
  name: r.name,
  descriptor: r.descriptor ?? null,
  archetype: r.archetype,
  owner_id: r.expand?.owner?.seed_id ?? r.owner,   // prefer seed_id for status/owner join
  repo_url: r.repo_url || null,
  reference_url: r.reference_url || null,
  dev_environment: r.dev_environment,
  status_source: r.status_source
}));
```
Owner resolution feeds the same `usersById` map the merge step already uses (keyed by `seed_id` → UI `User.id`), so §R3 derivation is untouched.

### 3.3 Merge, derive, sort — UNCHANGED
The existing `severityFor`, `priorityScore`, `tagsFor`, `stripId`, `emptyStatus`, the `usersById`/`statusById` maps, and the final `.sort(...)` are reused verbatim. This is what guarantees read-parity (R3) and confines the change to sourcing (R5.2). Status is still merged from `status.json` (R2), keyed by `lab_id`.

## 4. Configuration & env

- Add `VITE_PB_URL` to `app/web/.env.example` (create if absent) and to the repo-root `.env.example` PocketBase section, documenting the default `http://127.0.0.1:8090` (R4.2).
- Optional `VITE_PB_SOURCE=pocketbase|snapshot` switch to force the source in dev/CI (supports OQ-2 dual-run and deterministic parity testing). Default: auto (PB with snapshot fallback).
- No change to `svelte.config.js` / adapter — still static SPA.

## 5. `pb_provision.py` change (rule relaxation, §2)

Minimal, documented edit: set `projects` (and, if required for owner expand, `users`) `listRule`/`viewRule` to `""` with an inline comment tying it to `RFC-LAB-000-008` §4 public tier and noting M3 will refine field granularity. This keeps provisioning idempotent (existing upsert path handles the rule PATCH). `updateRule` on `projects` (owner-write) is left as-is — M1 does not touch writes.

## 6. Trade-offs & alternatives considered

| Decision | Chosen | Rejected alternative | Why |
| :--- | :--- | :--- | :--- |
| Read before auth | Open `projects` (+`users` display) read rules — the planned public tier | Defer live read to M2 | M1's whole point is closing the disconnect; coupling to auth defeats it. |
| Snapshot path | Retain as env-switchable fallback | Delete it now | Dual-run posture (`RFC-008` §9.4); zero-blank guarantee (R5). |
| Sort | Keep JS sort | Push to PB `sort` | Exact parity; PB sort can't express the composite `priority_score`. |
| Owner join key | `seed_id` | PB record `id` | `status.json` + existing maps key on the seed id (`usr-…`/`LAB-…`). |

## 7. Verification (feeds `tasks.md` and `RFC-LAB-000-009` Phase 3)

1. **Local stack:** `make setup` (provision + seed) then `make start-local`; set `VITE_PB_URL=http://127.0.0.1:8090`.
2. **Parity check:** load the dashboard against PocketBase; compare card set / order / owner pills / severity / KPI counts to a `VITE_PB_SOURCE=snapshot` render of the same seed. They must match (R3.2).
3. **Fallback check:** stop PocketBase (`make stop-local`) → dashboard falls back to snapshot without crashing (R5.1).
4. **Gates:** `pnpm --dir app/web check && pnpm --dir app/web build && pnpm --dir app/web lint`; `make validate-local` (R6).

## 8. AIDLC spike notes (`RFC-LAB-000-009` §7 — record findings during build)

This is the first Spec executed under the new lifecycle. During Build, capture (for the M1 `REPORT.md` / a Decision Journal entry): whether Autonomous mode executed this `tasks.md` directly or re-planned from `requirements.md`; the Web→IDE hand-off point that worked; and whether the EARS criteria were sufficient as the self-validation target.
