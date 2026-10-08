# `is_admin` Auth Tier — Requirements

| Property | Value |
| :--- | :--- |
| **Spec ID** | `is-admin-auth` |
| **Feature** | Add the application-level **`is_admin`** boolean tier to the `users` auth collection + the write-rule matrix that lets an admin manage projects, settings, and users in-app — **no UI** (the UIs are their own Specs). |
| **Backlog** | `BK-030` (`TSK-069`, SPRINT-13) |
| **Work class** | **Sprint deliverable** (auth/RBAC — a real capability users exercise) → **FULL gate**: Spec → `/spec-run` → `/review-pr` scorecard → human merge. |
| **Design record** | `RFC-LAB-000-008` **Amendment A1** (D67, Accepted 2026-10-08). This Spec implements A1. |
| **RFCs** | `RFC-LAB-000-008` (MVP RBAC + A1), `RFC-LAB-000-003` (PocketBase), `RFC-LAB-000-002` (relational data) |
| **Executor role** | **Kiro IDE** (budgeted) — auth/RBAC is high-stakes + touches the live rule path + needs rule-behavior verification; escalated above the Antigravity default per `RFC-LAB-000-014` cost-first routing (reason: security-sensitive, not routine). |
| **Source** | Operator brainstorm 2026-10-08 — unblocks the App Settings UI (`BK-031`) + Projects/Developers CRUD (`BK-014`). |

---

## 1. Introduction

Today's RBAC is **owner-or-not**: an authenticated project owner edits their own project's status; **nobody** can create/delete projects in-app, and `settings` is **superuser-only** write. Three queued UI features need in-app administration by someone who is **not** a PocketBase superuser. A1 decided the minimum surface: **one `is_admin` boolean**. This Spec adds that field and the write rules — isolated from any UI so the auth change is independently verifiable.

**This Spec deliberately ships NO UI.** The settings editor (`BK-031`) and CRUD (`BK-014`) are separate Specs that consume the rules landed here.

## 2. Current-state facts (verified 2026-10-08 on `main`)

The **authoritative rule source is `scripts/pb_provision.py`** (it creates collections via the REST API, version-robust). `scripts/generate_pb_schema.py` emits a CI-checked **reference** `app/pocketbase/pb_schema.json` that must stay in sync. Both must be edited.

Live rules (`pb_provision.py`):
- `users`: `listRule = RULE_AUTHED`, `viewRule = RULE_PUBLIC`, `createRule = RULE_PUBLIC` (OAuth sign-in creates the record), `updateRule = None`, `deleteRule = None`. Fields: `seed_id`, `name`, `github_handle`, `role` (select, optional), `org`, `active` (bool). **No `is_admin` field today.**
- `projects`: `createRule = None`; **`updateRule = '@request.auth.id != "" && @request.auth.github_handle != "" && owner.github_handle = @request.auth.github_handle'`** (owner match is **by `github_handle`**, NOT relation id — because an OAuth identity's record id differs from the seeded owner); `deleteRule = None`.
- `settings`: `listRule`/`viewRule = RULE_PUBLIC`; `createRule`/`updateRule`/`deleteRule = None` (superuser-only).

> **Grounding correction to A1's matrix:** A1 §A1.3 wrote the owner rule as `owner = @request.auth.id` (the simplified schema-reference form). The LIVE rule is the `github_handle` form above. This Spec ORs `RULE_ADMIN` into the **live** rule, preserving the existing owner path exactly.

## 3. Requirements (EARS acceptance criteria = Definition of Done)

### R1 — The `is_admin` field
- **R1.1** The `users` auth collection SHALL gain a boolean field **`is_admin`** (not required; default `false`), added in BOTH `scripts/pb_provision.py` (authoritative) and `scripts/generate_pb_schema.py` (reference).
- **R1.2** `is_admin` SHALL be a plain application flag, distinct from the PocketBase **superuser** (schema/collection power) and from the deferred `role` select. It carries on the auth token so `@request.auth.is_admin` resolves in rules.

### R2 — Admin predicate + rule matrix (in `pb_provision.py`, mirrored in the generator)
- **R2.1** Define `RULE_ADMIN = '@request.auth.id != "" && @request.auth.is_admin = true'`.
- **R2.2** `projects.createRule` SHALL become `RULE_ADMIN` (was `None`).
- **R2.3** `projects.updateRule` SHALL become the existing owner rule **OR** admin: `(@request.auth.id != "" && @request.auth.github_handle != "" && owner.github_handle = @request.auth.github_handle) || (@request.auth.id != "" && @request.auth.is_admin = true)`. The owner path MUST remain byte-for-byte unchanged inside the OR.
- **R2.4** `projects.deleteRule` SHALL become `RULE_ADMIN` (was `None`).
- **R2.5** `settings.createRule`, `settings.updateRule`, `settings.deleteRule` SHALL each become `RULE_ADMIN` (were `None`). `listRule`/`viewRule` stay `RULE_PUBLIC` (branding renders pre-auth — unchanged).
- **R2.6** `users.updateRule` SHALL become `RULE_ADMIN` (was `None`) so an admin can manage users (set `name`/`role`/`active`/`is_admin`). `createRule` stays `RULE_PUBLIC` (OAuth sign-in). `deleteRule` stays `None`.

### R3 — Generated-artifact lockstep
- **R3.1** `app/pocketbase/pb_schema.json` SHALL be regenerated from the updated `generate_pb_schema.py` so `python3 scripts/generate_pb_schema.py --check` passes (it is a generated artifact — never hand-edited).

### R4 — Bootstrap the first admin
- **R4.1** The Spec SHALL document (in `REPORT.md`) the one-time bootstrap: a **superuser** sets `is_admin = true` on the first admin user via the PocketBase admin UI (`/_/`). No code grants the first admin (chicken-and-egg); the flag is granted out-of-band once, then admins can grant others via R2.6.
- **R4.2** `pb_import.py`/seed MAY set `is_admin = true` on a designated seed user for local dev (optional; document if done). Production bootstrap stays the admin-UI step.

### R5 — Guardrails (verified, not just asserted)
- **R5.1 — No self-escalation:** a non-admin SHALL have no write path to their own `users` record (`users.updateRule = RULE_ADMIN` means only admins write `users`; a non-admin cannot set their own `is_admin`). Verify: signed-in non-admin PATCH on own `users` record → denied.
- **R5.2 — Superuser unaffected:** the PocketBase superuser retains full admin-UI/schema power; `is_admin` never grants schema power.
- **R5.3 — Owner path preserved:** an owner (non-admin) can still edit their own project's status; a non-owner non-admin still denied.

### R6 — Rule-behavior tests (the DoD proof — fail-closed)
Against a locally provisioned instance (`just setup`), with one admin (`is_admin=true`), one owner (non-admin), one plain authed user:
- **R6.1** Admin creates a project → **allowed**; writes a `settings` row → **allowed**; edits a project they don't own → **allowed**; deletes a project → **allowed**.
- **R6.2** Owner edits **their own** project status → **allowed**; edits another's project → **denied**; writes `settings` → **denied**; creates/deletes a project → **denied**.
- **R6.3** Plain authed user: all writes **denied**; reads (public summary + authed detail) **allowed**.
- **R6.4** Non-admin PATCH on own `users.is_admin` → **denied** (R5.1).
- **R6.5** Anonymous: public read of `projects`/`settings` → **allowed**; any write → **denied**.
- These tests SHALL be captured as a runnable script (extend the existing `test-settings.js` pattern or a small `scripts/test-rbac-admin.*`) and their results recorded in `REPORT.md`.

### R7 — Quality gates / scope floor
- **R7.1** `just validate-local` (5 validators + `generate_pb_schema --check` + `pnpm check && build`) green.
- **R7.2** Scope floor: `scripts/pb_provision.py`, `scripts/generate_pb_schema.py`, `app/pocketbase/pb_schema.json` (regenerated), optionally the seed (`pb_import.py`/`data/users.json` for a local admin) and the rule-test script. **NO web UI** (`app/web/**` unchanged except none). **NO** new collection, **NO** `memberships`/5-role change.

## 4. Out of scope
Any admin UI (settings editor = `BK-031`; CRUD = `BK-014`); the 5-role `memberships` model (stays deferred per §4/A1); an audit trail for admin writes (A1 known gap — later RFC); email/password auth.

## 4b. Human Verification Plan (emitted by `/spec-run`; recorded by `/verification-done`)
On the local stack (`just setup && just start-local`), with a bootstrapped admin + a non-admin owner:
- **V1 — field present:** `users` has `is_admin` (admin UI shows it); token carries it.
- **V2 — admin writes:** as admin, create a project + edit a settings row via API/SDK → persists.
- **V3 — owner preserved:** as a non-admin owner, edit own project status → persists; edit another's → denied.
- **V4 — non-admin denied:** as a plain authed user, any write → denied; as a non-admin, PATCH own `is_admin` → denied.
- **V5 — anon read:** signed out, portfolio summary + branding still render.
- **V6 — gates:** `just validate-local` green; `pb_schema.json --check` green; rule-test script all-pass.
