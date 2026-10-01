# RFC-LAB-000-007: Work-Environment Standardization (KiroCrew Operator + Kiro IDE Executor)

| Property | Value |
| :--- | :--- |
| **RFC ID** | `RFC-LAB-000-007` |
| **Title** | Standardized Work Environment — KiroCrew (Operator) + Kiro IDE (Executor) + Kiro Web (fallback) |
| **Author** | Eialarasu (LAB-000 Control Hub) |
| **Status** | ✅ Accepted |
| **Date** | 2026-09-24 |
| **Amended** | 2026-10-01 — surface model updated to the three-role Operator/Executor/fallback split (see §2.1 Amendment) |
| **Backlog** | `BK` / `TSK-039` (SPRINT-08) |
| **Builds On** | `RFC-LAB-000-001` (cloud dev), `RFC-LAB-000-004` (branching), Kiro-native skillset (`TSK-038`) |
| **Influenced By** | Nexus Pulse (`LAB-003`) Developer Onboarding & Operations Guide — adapted, not copied |

---

## 1. Context & Problem Statement

Development spans **two surfaces on the same repo**: **Kiro Web** (cloud sandbox — clones the repo, no local filesystem, cannot run persistent servers) and **Kiro IDE** (local machine — full filesystem, `~/.kiro`, runs servers). The skillset is standardized (`TSK-038`), but the broader *work environment* is not: toolchain versions can drift, container tooling is unspecified, personal-config sync is a manual ritual, and there's no single "am I set up correctly here?" check. This RFC standardizes the environment so switching surfaces is friction-free.

## 2. Decisions

### 2.1 Surface Roles (intentional split, not a hard wall)

> **Amendment (2026-10-01).** The original two-surface model (Kiro Web + Kiro IDE) is superseded
> by a three-role model. **KiroCrew** (this control layer) becomes the **Operator** — it absorbs
> and extends the former "Kiro Web = brainstorm & plan" role with persistent memory, scheduled
> jobs, and orchestration. **Kiro Web** is demoted to a **stateless fallback**. See
> [`ai-collaboration-model.md §2`](../governance/ai-collaboration-model.md#2-two-surfaces-two-roles-rfc-lab-000-007).

| Surface | Primary role | Typical work |
| :--- | :--- | :--- |
| **KiroCrew** (Operator) | **Stateful** — brainstorm, plan, govern | RFCs, Spec authoring, backlog/changelog/journal, `data/` edits, PR review, status broadcasts, `scripts/` (Python), persistent per-project memory |
| **Kiro IDE** (Executor/Worker) | **Stateful** — servers & data | Running the stack (`/start-local`), PocketBase DB work, SvelteKit UI dev, `/spec-run`, secrets/OAuth, local verification, pushing `feat/` branches, staging deploys |
| **Kiro Web** | **Stateless fallback** | Throwaway brainstorm with no persistent memory, no-install access from any machine, config-sync parity checks |

This is guidance to reach for the right surface — not a restriction. The **Operator never merges**:
it opens PRs, self-validates, and STOP-and-holds at the human gate. Decisions and coordination
default to the Operator; code execution is delegated to the Executor. Kiro Web remains able to
edit anything but holds no persistent state, so use it only as a fallback. Consistent with
`RFC-LAB-000-001` (cloud-first for stateless work).

### 2.2 Toolchain Pinning
- **`.nvmrc`** pins Node (22); `package.json` `packageManager` pins pnpm (10). Both surfaces resolve identical versions.
- **Python 3.11+** (zero-dependency scripts; no venv required for governance).

### 2.3 Container Strategy — Podman-first
- **Podman is the default** container engine; **Docker is the documented fallback** (commands written `podman … || docker …`).
- **Important scope:** PocketBase runs as a **single binary + SQLite file** and does **not require a container for local dev**. Podman is provisioned for (a) **staging/GCP parity** (containerized PocketBase image) and (b) the **forward path** if the datastore ever grows (e.g. Postgres). Local dev stays binary-first for speed; the `Containerfile` is opt-in.

### 2.4 Personal Config-Sync Protocol (one-way)
- **Local `~/.kiro/` is the source of truth** for personal skills/steering. Kiro Web cannot read it directly.
- After editing personal config locally, **re-upload** via Kiro Web → **Settings → Sync** (one-way local→cloud). Web-side edits do **not** flow back — never treat Web as the personal-config source.
- Project config (`.kiro/` committed) needs no sync — it travels with the repo to both surfaces.

### 2.5 Skill Boundary — `/env-doctor` vs `/validate-*`
- **`/env-doctor`** = *environment readiness only* (surface-aware; probes toolchain/binary/secrets/git). **Read-only; never runs validators or builds.** Delegates work-correctness to `/validate-local`.
- **`/validate-local`** = *work correctness* (Python validators + SvelteKit build). If the environment is unfit, it points back to `/env-doctor` rather than diagnosing the environment.
- **`/validate-staging`** = *remote staging health* (unchanged). No overlap; each owns one layer.

## 3. Adoption from Nexus Pulse (`LAB-003`) — Adapted

The Nexus Pulse Developer Guide is the reference. Adopted patterns, translated to our stack:

| Nexus Pulse | LAB-000 adaptation |
| :--- | :--- |
| `make` cheat-sheet + `make help` | **Adopt** — `Makefile` mirroring the `/commands` (single entry point, works in Web + IDE terminals). |
| Podman/Docker for local DB | **Adopt (forward)** — Podman-first `Containerfile` for PocketBase; local dev stays binary-first. |
| State A (clean) / State B (seeded) | **Adapt** — clean = fresh `pb_data/`; seeded = `scripts/pb_import.py --apply` from `data/`. |
| Test personas + passwords | **Adapt (forward)** — documented against Phase 3 RBAC roles (`RFC-LAB-000-006`); provisioned when auth lands. |
| Roles & PR / Gatekeeper rule | **Reference** — already codified in `RFC-LAB-000-004`; cross-linked, not duplicated. |
| `.env.example` + env parity | **Adopt** — `.env.example` for PocketBase/OAuth/deploy vars. |
| Ports 8000/3000, Alembic, Supabase, Postgres | **Skip/translate** — ours: PocketBase `:8090`, SvelteKit `:5173`, SQLite. |

## 4. Deliverables (`TSK-039`)
- This RFC.
- `.nvmrc` (Node 22), `.env.example` (documented vars).
- `Makefile` — `make help` cheat-sheet mirroring `/commands`; targets delegate to existing scripts.
- `Containerfile` — Podman-first PocketBase image (Docker fallback documented).
- `.kiro/skills/env-doctor/SKILL.md` — surface-aware diagnostic; cross-refs added to `validate-local` / `validate-staging`.
- `docs/work-environment.md` — onboarding & operations guide (adapted from the Nexus Pulse guide). *(Renamed to [`docs/guides/developer-guide.md`](../guides/developer-guide.md) and regrouped under `docs/guides/` by the docs-reorganization refactor, `TSK-052`.)*

## 5. Risks & Mitigations
| Risk | Mitigation |
| :--- | :--- |
| Podman forced where a binary suffices | Local dev stays binary-first; container is opt-in for staging/forward only. |
| Toolchain drift across surfaces | `.nvmrc` + `packageManager` pin exact versions. |
| Personal config confusion (one-way sync) | §2.4 protocol documented in `work-environment.md`. |
| `/env-doctor` scope creep into validation | §2.5 hard boundary: diagnostic-only, delegates to `/validate-local`. |
| Makefile diverges from `/commands` | Targets call the same scripts the skills call; single source of behavior. |

## 6. Open Questions
1. Whether to add a `podman-compose.yml` now or defer until staging (GCP) is provisioned. *Leaning defer — single binary needs no compose yet.*
2. Secret management for OAuth/deploy in staging (GCP Secret Manager vs. env files) — decided during Phase 3 build / staging setup.
