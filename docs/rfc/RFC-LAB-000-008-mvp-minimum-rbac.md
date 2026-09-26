# RFC-LAB-000-008: MVP Definition & Minimum RBAC

| Property | Value |
| :--- | :--- |
| **RFC ID** | `RFC-LAB-000-008` |
| **Title** | Control Hub Web App — MVP Definition & Minimum RBAC |
| **Author** | Eialarasu (LAB-000 Control Hub) |
| **Status** | 🟡 Proposed (Scoping — awaiting refinement) |
| **Date** | 2026-09-24 |
| **Builds On** | `RFC-LAB-000-003` (PocketBase), `-005` (Sleek UI), `-006` (auth/RBAC), `-007` (work env) |
| **Foundation verified** | Local stack proven: provisioning + seed live on PocketBase v0.40 (3 users, 6 projects, 6 memberships). |

---

## 1. Purpose

Define **"done" for the MVP** and the **minimum RBAC** it ships — a tight, achievable target now that the backend (PocketBase provisioning + seed) and the read-only Sleek UI both work locally. This is a scoping RFC: it sets the boundary and the acceptance criteria; it is intentionally conservative on scope so the MVP ships.

## 2. MVP Definition ("done")

> **A logged-in user sees the live portfolio from PocketBase; an authenticated project owner can edit their own project's status in-app; everyone else has read-only access. The app is deployed and usable.**

Concretely, the MVP is achieved when:
1. The Sleek UI reads **live PocketBase data** (not the static `data/status.json` snapshot).
2. A user can **sign in** (GitHub OAuth).
3. **Minimum RBAC** is enforced (§4): public read, authenticated detail, owner-writes-own.
4. An **owner can edit their project's status** in the UI, and it persists to PocketBase.
5. The authenticated app is **deployed** (target: GCP / Vercel per `RFC-LAB-000-007`, post org-transfer).

## 3. The Gap the MVP Closes

Today (verified locally): backend live + seeded ✅, UI live ✅ — **but disconnected**. The UI reads a bundled `data/status.json`; PocketBase holds the real records. The MVP's spine is **connecting these** and adding the thinnest useful auth + one write path.

## 4. Minimum RBAC (the "minimum" is deliberate)

Three effective tiers — using the **1:1 `owner_id`** already in the data model (no `memberships` join needed for MVP):

| Tier | Can | PocketBase API rule (on `projects`) |
| :--- | :--- | :--- |
| **Public / anon** | Read portfolio summaries | `listRule` / `viewRule` = `""` (open) |
| **Authenticated** | Read full detail | `@request.auth.id != ""` |
| **Owner** | Edit **their own** project's status | `updateRule`: `@request.auth.id != "" && owner = @request.auth.id` |

The `owner`-write rule is **already provisioned** (`pb_provision.py`) — the MVP wires the UI to it.

**Explicitly DEFERRED past MVP** (documented so scope stays honest):
- The full 5-role model (`lead`/`contributor`/`reviewer`/`stakeholder`) and **`memberships`-based multi-role writes**.
- The audit trail (`RFC-LAB-000-006` §6).
- Status-history / `status_snapshots` migration (stays in `STATUS.md` for MVP).
- Create/delete of projects in-app (owner edits existing status only).

> Rationale: "minimum" = **owner-or-not**, resolved by `owner_id` (fast, no join). It exercises the *real* auth + rule path end-to-end while deferring the relational-role complexity until there's a concrete need. The `memberships` layer remains in the schema, ready for the post-MVP RBAC expansion.

## 5. Auth (minimum)

- **GitHub OAuth2** on the PocketBase `users` collection (per `RFC-LAB-000-006` §2), linked to the seeded user by `github_handle`.
- Superuser (admin UI) remains the control-hub owner's escape hatch.
- Email/password is available as a fallback but not required for MVP.

## 6. Phase Breakdown (candidate tasks)

| Phase | Scope | Exit criteria |
| :--- | :--- | :--- |
| **M1 — Wire UI → live PocketBase** | Flip `app/web/src/lib/data.ts` from the static snapshot to the PocketBase JS SDK (`getFullList({ expand: 'owner' })`); env-configurable PB URL | UI renders from live DB; read-parity preserved |
| **M2 — Auth (GitHub OAuth)** | Sign-in flow via PB SDK; auth store; account-link by `github_handle`; route guard for member views | User can sign in; UI reflects auth state |
| **M3 — Minimum RBAC** | Apply/verify the §4 rule matrix on `projects`; public summary tier stays open | Non-member sees summary; owner sees/edits own; superuser all |
| **M4 — Owner write path** | Owner edits their project's status field(s) in-app; persists via PB; optimistic UI | Owner edits own project; denied on others |
| **M5 — Deploy** | Authenticated app to GCP / Vercel; PocketBase hosted; env + secrets | Live, authenticated, usable URL |

M1 is the highest-leverage first step (closes the core disconnect) and is buildable/testable entirely on the local stack.

## 7. Live-Status During MVP

The UI's *structural* data (projects, owner) comes from PocketBase in M1. **Live status fields** (health, wins, focus, blockers) still originate from `STATUS.md` → `data/status.json` until a later phase migrates them into `status_snapshots`. For MVP, the UI can merge live PB structural data with the `status.json` snapshot (as it does today for status), OR the owner-editable status writes to a PB field — decided at M4 build start (see §9).

## 8. Acceptance Criteria (MVP demo script)

1. Visit the app unauthenticated → see the portfolio summary (public tier).
2. Sign in with GitHub → see full detail; data is live from PocketBase (edit a record in the admin UI, refresh, see it change).
3. As an owner, edit **your** project's status → it persists.
4. Attempt to edit a project you don't own → denied (rule-enforced).
5. The app is reachable at a deployed URL.

## 9. Open Questions (resolve at build start)

1. **Status ownership for M4**: does "edit status" write to a new PocketBase field on `projects`, or do we bring `status_snapshots` forward from the deferred list? *(Leaning: a minimal status field on `projects` for MVP; full `status_snapshots` post-MVP.)*
2. **Public tier granularity**: which project fields are public-summary vs. authenticated-detail.
3. **Deploy target sequencing**: GCP vs. Vercel-first for the frontend; depends on org-transfer timing.
4. **Does the classic dashboard / `STATUS.md` cadence stay** as the executive channel during MVP, with the app as the interactive layer? *(Leaning: yes — dual-run continues.)*

## 10. Risks & Mitigations

| Risk | Mitigation |
| :--- | :--- |
| Scope creep into full RBAC | §4 hard-defers roles/memberships/audit; MVP is owner-or-not. |
| Two status sources (STATUS.md + PB) confusion | §7/§9.1 decides one path at M4; document clearly. |
| Deploy blocked on org-transfer | M1–M4 are fully local; deploy (M5) is the only transfer-dependent phase. |
| Auth complexity balloons | GitHub OAuth only for MVP; email/password + extra providers deferred. |
