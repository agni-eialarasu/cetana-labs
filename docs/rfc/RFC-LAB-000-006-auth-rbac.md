# RFC-LAB-000-006: Web App Phase 3 — Authentication & RBAC Scoping (`BK-007`)

| Property | Value |
| :--- | :--- |
| **RFC ID** | `RFC-LAB-000-006` |
| **Title** | Control Hub Web App — Phase 3 Auth & Role-Based Access Control |
| **Author** | Eialarasu (LAB-000 Control Hub) |
| **Status** | 🟡 Proposed (Scoping — `BK-008` Phase 3 / `BK-007`) |
| **Date** | 2026-09-24 |
| **Builds On** | `RFC-LAB-000-002` (relational data + `memberships`), `RFC-LAB-000-003` (PocketBase §5), `RFC-LAB-000-005` (Sleek UI) |
| **Enables** | `BK-007` (role-gated audit trail), Phase 4 write path |

---

## 1. Purpose & Scope

Scope **Phase 3**: add **authentication** and **role-based access control (RBAC)** to the PocketBase-backed Control Hub, turning the read-only Sleek UI into an access-governed application. This directly delivers the `BK-007` intent — role-gated history/access **without** a developer-surveillance perception, because access is governed by **explicit, auditable PocketBase API rules** rather than opaque logic.

**In scope:** identity/login (GitHub OAuth), the role model (via `memberships`), per-collection API rules, the UI auth flow, an audit trail, and non-surveillance safeguards.
**Out of scope (this phase):** the in-app write/edit path and `STATUS.md → status_snapshots` migration (Phase 4); telemetry (Phase 5).

## 2. Identity & Authentication

- **Provider: GitHub OAuth2.** PocketBase's `users` auth collection supports OAuth2; GitHub is chosen because it aligns with the existing `github_handle` on the user master (`RFC-LAB-000-002`) and every current lead already has a GitHub identity.
- **Fallback:** email/password remains available on the auth collection for non-GitHub stakeholders (optional, admin-provisioned).
- **Superuser:** the PocketBase superuser (admin UI) is reserved for the control-hub owner and is separate from application `users`.
- **Account linking:** on first OAuth login, match/link to the seeded `users` record by `github_handle` (or provision a pending record) so ownership/memberships resolve immediately.

## 3. Role Model

Reuse the existing enum (`RFC-LAB-000-002`), resolved through the **`memberships`** join (a user's role is **per-project**, not global):

| Role | Intent |
| :--- | :--- |
| `owner` | Full control of the project record; primary accountable lead. |
| `lead` | Manage status/content for the project. |
| `contributor` | Edit within the project (Phase 4 write path). |
| `reviewer` | Read + comment; no writes. |
| `stakeholder` | Read-only detail access. |

A **superuser** (control-hub owner) transcends memberships. Absent any membership, an authenticated user gets the **public read tier** (portfolio summaries) — matching today's public dashboard.

## 4. Access Enforcement — PocketBase API Rules

PocketBase gates every collection with five rule types; each is `null` (superuser-only), `""` (anyone, incl. unauthenticated), or a filter **expression**. Rules use `@request.auth.*` for the caller and `@collection.<name>.<field>` for cross-collection joins; multi-value relation membership uses the `?=` ("any of") operator. _Content was rephrased for compliance with licensing restrictions._ ([pocketbase.io/docs/api-rules-and-filters](https://pocketbase.io/docs/api-rules-and-filters/))

### Draft rule matrix (refined during build)

| Collection | list / view | create | update | delete |
| :--- | :--- | :--- | :--- | :--- |
| `projects` | `""` (public read tier) — summaries public, matching the current dashboard | `null` (superuser) | owner or member with write role | `null` |
| `memberships` | `@request.auth.id != ""` (authed) | `null` | `null` | `null` |
| `users` | self + authed peers (limited fields) | `null` | self-update limited fields; else `null` | `null` |
| `status_snapshots` (P4) | `""` public read | member write role | member write role | `null` |

**Membership-gated write example** (the documented "users↔orgs via a join with role" pattern):

```text
// projects.updateRule — owner OR a member holding lead/contributor on THIS project
@request.auth.id != "" && (
  owner = @request.auth.id ||
  @collection.memberships.project ?= id &&
  @collection.memberships.user  ?= @request.auth.id &&
  @collection.memberships.role  ?~ "owner|lead|contributor"
)
```

> **Constraint noted:** a filter can join a given collection only once; where a rule needs multiple independent membership checks, we model it via a DB **view collection** or denormalized flag rather than a second join (decided at build time).

## 5. UI Auth Flow (Sleek UI)

- **Public tier (unchanged):** the dashboard's portfolio summaries remain publicly viewable (no login required) — preserving the current experience and the `BK-007` anti-surveillance stance.
- **Sign in with GitHub:** a header action starts the PocketBase OAuth2 flow via the JS SDK; on success the SDK stores the auth token, and the UI reveals member-scoped detail for the user's projects.
- **Client-side SDK** continues (per `RFC-LAB-000-005`): PocketBase enforces rules server-side, so the browser simply gets 200s or 403/404s — the UI adapts to what the token can see.
- **Route guard:** member-only views redirect to sign-in when unauthenticated; the public dashboard never blocks.

## 6. Audit Trail (`BK-007`)

- **Access-change audit:** membership/role and project mutations are recorded (PocketBase logs + an append-only `audit` collection capturing actor, action, target, timestamp).
- **Status history:** once `status_snapshots` lands (P4), health/win transitions become queryable history — the "role-gated history" `BK-007` describes — visible per the same API rules.
- **Auditable by design:** because access is expressed as readable API-rule filters (not hidden code), the governance model is inspectable — the explicit `BK-007` non-surveillance requirement.

## 7. Non-Surveillance Safeguards (explicit `BK-007` requirement)

- Public **summary** tier stays open; RBAC gates **detail/history**, not basic visibility.
- Access rules are **version-controlled and human-readable** (committed alongside the schema), so "who can see what" is transparent to the team.
- Audit captures **access/administration events**, not developer activity monitoring.
- No per-user productivity metrics; history is about **project status**, not people.

## 8. Phased Build Steps (Phase 3)

1. Enable GitHub OAuth2 on the PocketBase `users` collection; wire account-linking by `github_handle`.
2. Commit the API-rule matrix (§4) as part of the versioned schema; extend `pb_schema.json` + generator.
3. Add the `audit` collection (append-only).
4. Sleek UI: "Sign in with GitHub", auth store, member-scoped views, route guard.
5. Seed importer: assign memberships/roles from `data/memberships.json` (already modeled).
6. Tests: rule matrix verified (member sees own; non-member gets summary; superuser sees all).

## 9. Risks & Mitigations

| Risk | Mitigation |
| :--- | :--- |
| Single-join limitation in filters | Use a view collection / denormalized flag for complex checks (§4). |
| OAuth misconfig locks out access | Superuser admin path retained; email/password fallback. |
| Over-restrictive rules break public dashboard | Public summary tier is `""` (open) by design; RBAC only gates detail. |
| Perceived surveillance | §7 safeguards: open summaries, transparent rules, access-only audit. |
| Rules drift from intent | Rules are version-controlled + covered by the §8.6 test matrix. |

## 10. Open Questions (resolve at build start)

1. First-login provisioning: auto-create a pending `users` record vs. require pre-seeding by `github_handle`.
2. Audit store: dedicated `audit` collection vs. rely on PocketBase's built-in logs initially.
3. Whether `reviewer`/`stakeholder` differ in Phase 3 (both read-only) or only diverge once commenting exists.
4. Public tier granularity: which project fields are public-summary vs. member-only detail.
