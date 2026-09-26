# M1 — Wire Sleek UI to Live PocketBase — Tasks

> Ordered implementation plan for Autonomous mode / a delegated agent (`RFC-LAB-000-009` §3 Build). Each task cites the requirement(s) it satisfies. Execute on **Kiro IDE** (stateful — needs the running local stack). Do NOT merge; open a PR for the human gate (Phase 4).

---

- [ ] **T1 — Prepare & verify the local stack (baseline)**
  - Run `make setup` (provision collections + seed 3 users / 6 projects / 6 memberships) and `make start-local` (PocketBase `:8090`, SvelteKit `:5173`).
  - Confirm the dashboard currently renders from the **snapshot** (baseline for the parity comparison in T7).
  - _Refs: R3.2 (baseline), verification design §7.1._

- [ ] **T2 — Relax `projects` read rules to the planned public tier**
  - In `scripts/pb_provision.py`, set `projects` `listRule`/`viewRule` to `""` (public), with an inline comment referencing `RFC-LAB-000-008` §4 (public-summary tier) and noting M3 refines field granularity. If anon `expand: 'owner'` is stripped, also open `users` `viewRule` to `""` for the seeded non-sensitive display fields (name/github_handle).
  - Re-run `make provision` (idempotent upsert) and verify an **anonymous** SDK/curl read of `/api/collections/projects/records` returns the 6 seeded projects.
  - _Refs: R-access §3, design §2/§5._

- [ ] **T3 — Add env config for the PocketBase URL**
  - Add `VITE_PB_URL` (default `http://127.0.0.1:8090`) and optional `VITE_PB_SOURCE` (`pocketbase|snapshot`, default auto) to `app/web/.env.example` (create if absent) and document `VITE_PB_URL` in the repo-root `.env.example` PocketBase section.
  - _Refs: R4.1, R4.2, design §4._

- [ ] **T4 — Implement the PocketBase source in `data.ts`**
  - Add a PocketBase client (`import PocketBase from 'pocketbase'`; `autoCancellation(false)`), read `VITE_PB_URL`.
  - Implement `loadFromPocketBase()`: `pb.collection('projects').getFullList({ expand: 'owner' })`, map records to `ProjectRecord` per field-mapping §2 (`lab_id`→`id`, expanded `owner`→`owner_id`/user), build the `User[]` from expanded owners (dedup by `seed_id`).
  - _Refs: R1.1, R1.2, R1.3, design §3.1/§3.2._

- [ ] **T5 — Add the source switch + snapshot fallback**
  - Introduce `loadProjectRecords(fetch)` that selects PocketBase when configured/reachable else the existing `fetchJson` snapshot path; keep `loadFromSnapshot` = today's behavior.
  - On PB unreachable / zero records, log a warning and fall back (no unhandled throw, no blank dashboard).
  - Preserve the public `loadProjects(fetch): Promise<Project[]>` signature exactly.
  - _Refs: R5.1, R5.2, design §2/§3._

- [ ] **T6 — Keep status merge + derivation + sort unchanged**
  - Ensure status is still merged from `status.json` keyed by `lab_id`; reuse `severityFor`/`priorityScore`/`tagsFor`/`stripId`/`emptyStatus` and the final JS sort verbatim. No edits to `+page.ts`, `+page.svelte`, components, or the `Project` type.
  - _Refs: R2.1, R2.2, R3.1, R5.2, design §3.3._

- [ ] **T7 — Read-parity verification**
  - Render the dashboard against PocketBase (`VITE_PB_SOURCE=pocketbase`) and against the snapshot (`VITE_PB_SOURCE=snapshot`) for the same seed; confirm identical card set, ordering, owner pills, severity styling, and KPI counts.
  - Record any discrepancy and reconcile until parity holds.
  - _Refs: R3.2, design §7.2._

- [ ] **T8 — Fallback verification**
  - Stop PocketBase (`make stop-local`), reload → confirm graceful snapshot fallback with a clear log and no crash.
  - _Refs: R5.1, design §7.3._

- [ ] **T9 — Quality gates green**
  - `pnpm --dir app/web check` (svelte-check + tsc), `pnpm --dir app/web build` (static adapter), `pnpm --dir app/web lint` (prettier), and `make validate-local` — all green.
  - _Refs: R6.1, R6.2, R6.3._

- [ ] **T10 — Open PR for the human gate (do NOT merge)**
  - Branch `feat/mvp-m1-live-pocketbase` (per `RFC-LAB-000-004` naming). Commit with a semantic message referencing `BK-011` / M1.
  - Open a PR into `main` via `gh api …/pulls` (REST); ensure CI is green. STOP-and-hold for human review (`RFC-LAB-000-009` Phase 4).
  - _Refs: `RFC-LAB-000-004`, `RFC-LAB-000-009` §3._

- [ ] **T11 — Record AIDLC spike findings**
  - In the PR body and/or the M1 `REPORT.md` (and a Decision Journal entry if it produced a decision), note: whether Autonomous ran this `tasks.md` directly or re-planned from `requirements.md`; the Web→IDE hand-off that worked; whether EARS was sufficient as the self-validation target.
  - _Refs: `RFC-LAB-000-009` §7, design §8._

---

### Governance lockstep reminder (Phase 5, after merge)
Update CHANGELOG / BACKLOG (`TSK`/`BK-011` M1 → progress) and `data/` if touched; keep the validator green. M1 does **not** implement auth, writes, or deploy (M2/M4/M5) — hold that line.
