# `is_admin` Auth Tier — Design

| Property | Value |
| :--- | :--- |
| **Spec ID** | `is-admin-auth` (`BK-030` / `TSK-069`) |
| **Implements** | `RFC-LAB-000-008` Amendment A1 (D67) |
| **Executor** | Kiro IDE (security-sensitive — escalated from the Antigravity default, `RFC-LAB-000-014`) |

## 1. Approach

One boolean field + a reusable rule predicate OR'd into the existing write rules. No new collection, no join, no UI. The entire change lives in the two **rule-source scripts** and the **regenerated reference schema**.

Why a boolean, not a role: A1 chose the minimum surface (Option C). The 5-role `memberships` model stays deferred. `is_admin` is an **auth-collection field**, so PocketBase includes it in the auth token and `@request.auth.is_admin` is valid in collection API rules.

## 2. The two rule sources (both must change, kept in sync)

| File | Role | Edit |
| :--- | :--- | :--- |
| `scripts/pb_provision.py` | **Authoritative** — creates collections via REST API | Add `is_admin` bool to `users_spec.fields`; add `RULE_ADMIN` constant; update the `projects`/`settings`/`users` rules per R2. |
| `scripts/generate_pb_schema.py` | **Reference** — emits CI-checked `pb_schema.json` | Mirror the same field + rules so `--check` matches a provisioned instance. |
| `app/pocketbase/pb_schema.json` | **Generated artifact** | Regenerate (`python3 scripts/generate_pb_schema.py`); never hand-edit. |

## 3. The field

```python
# pb_provision.py — users_spec.fields (append)
f_bool("is_admin"),         # application admin flag (A1); default false, not required
# generate_pb_schema.py — users.fields (append), mirror shape:
{"name": "is_admin", "type": "bool", "required": False, "hidden": False, "presentable": False},
```

## 4. The predicate + rule changes (exact)

```python
RULE_ADMIN = '@request.auth.id != "" && @request.auth.is_admin = true'
OWNER_RULE = '@request.auth.id != "" && @request.auth.github_handle != "" && owner.github_handle = @request.auth.github_handle'
```

| Collection | Field | New value |
| :--- | :--- | :--- |
| `projects` | `createRule` | `RULE_ADMIN` |
| `projects` | `updateRule` | `f'({OWNER_RULE}) || ({RULE_ADMIN})'` — owner path preserved verbatim |
| `projects` | `deleteRule` | `RULE_ADMIN` |
| `settings` | `createRule`/`updateRule`/`deleteRule` | `RULE_ADMIN` (list/view stay `RULE_PUBLIC`) |
| `users` | `updateRule` | `RULE_ADMIN` (create stays `RULE_PUBLIC` for OAuth; delete stays `None`) |

> **PocketBase gotcha:** `@request.auth.is_admin` only resolves if `is_admin` exists on the auth collection at provision time. Order matters — the field must be created with/before the rules that reference it. `upsert_collection` sets fields then rules in one spec, so this is satisfied within a single collection upsert; verify on a fresh `just setup`.

## 5. Bootstrap (chicken-and-egg)

No code can grant the first admin (nobody is admin yet). The first admin is set **once** by a PocketBase **superuser** via the admin UI (`/_/` → `users` → the user → toggle `is_admin`). After that, admins grant others through the R2.6 `users.updateRule`. For local dev, the seed MAY flip `is_admin=true` on a designated `data/users.json` row (documented in REPORT); production stays the manual admin-UI step.

## 6. Verification strategy (fail-closed)

A small rule-test harness (extend `test-settings.js` or add `scripts/test-rbac-admin.*`) authenticates three identities (admin / owner-non-admin / plain-authed) + anonymous, and asserts the R6 matrix. Fail-closed: a write that *should* be denied but succeeds fails the test. Results recorded in `REPORT.md` and surfaced at `/review-pr` as the EARS DoD evidence.

## 7. Risk / rollback

- **Risk:** a mis-OR'd `updateRule` could silently widen or break owner writes. **Mitigation:** R6.2 explicitly re-verifies the owner path (allowed on own, denied on others) alongside the admin path.
- **Rollback:** revert the PR — the rules return to `None`/owner-only; the `is_admin` field is additive and harmless if left (no rule references it after revert). No data migration.
- **No blast radius on reads:** list/view rules are untouched; public portfolio + branding reads are unchanged.

## 8. Decisions

- **D-ADM-1 — boolean, not role.** Honors A1/Option C; 5-role model stays deferred.
- **D-ADM-2 — OR into the live `github_handle` owner rule**, not A1's simplified `owner = @request.auth.id` (grounding correction; the live rule is authoritative).
- **D-ADM-3 — no UI in this Spec.** Settings editor (`BK-031`) + CRUD (`BK-014`) consume these rules separately.
- **D-ADM-4 — manual superuser bootstrap** for the first admin (no self-grant path by design).
