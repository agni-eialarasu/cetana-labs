# Cetana Labs — Product Backlog (Idea Bucket)

The **idea bucket** for **Cetana Labs Control Hub (`LAB-000`)** — prioritized, groomed future initiatives (`BK-` items) that have not yet been committed to a sprint. This is the first tier of the three-tier tracking funnel defined in [`RFC-LAB-000-010`](docs/rfc/RFC-LAB-000-010-tracking-model.md):

```
BACKLOG.md            SPRINT_TRACKER.md              CHANGELOG.md
(ideas / the shelf)   (committed, in-flight work)    (shipped history)
```

> 🎯 **Active sprint & delivered archive:** [`SPRINT_TRACKER.md`](SPRINT_TRACKER.md) · 📜 **Shipped releases:** [`CHANGELOG.md`](CHANGELOG.md)
>
> **Definition of Ready (backlog → sprint):** a `BK-` idea leaves this shelf and enters `SPRINT_TRACKER.md` as `✅ Ready` only when its Kiro Spec is authored and merged to `main` (`READY_TO_BUILD`), per [`RFC-LAB-000-010`](docs/rfc/RFC-LAB-000-010-tracking-model.md) §5.

---

## 💡 Prioritized Backlog (Future Sprints)

| Backlog ID | Proposed Initiative / Capability | Priority | Archetype | Target Sprint | Notes |
| :---: | :--- | :---: | :---: | :---: | :--- |
| `BK-005` | PDF Executive Digest Export | P3 | Tooling | Backlog | One-click export for board/investor reporting |
| `BK-006` | Project Health Trend Telemetry | P3 | Analytics | Backlog | Historical velocity and health transition graphs on dashboard |
| `BK-007` | On-Demand Git Status Audit Trail & Role-Gated History | P2 | Governance | SPRINT-07 (scoped) | Role-gated history & audit trail. Auth/RBAC scoped in [`RFC-LAB-000-006`](docs/rfc/RFC-LAB-000-006-auth-rbac.md) (`TSK-037`) — GitHub OAuth, per-project roles via `memberships`, per-collection API rules, access-only audit (non-surveillance). Delivered as BK-008 Phase 3 atop the web app. |
| `BK-008` | Control Hub Web App Evolution (PocketBase, db + server) | P2 | Platform | SPRINT-06 (scoping) | Evolve the static control plane into a full PocketBase web application (database + backend server). Scoped in [`RFC-LAB-000-003`](docs/rfc/RFC-LAB-000-003-pocketbase-web-app.md) (`TSK-031`). Prerequisite for `BK-007` RBAC. Cloud dev env shifts Kiro Web → Codespaces per `RFC-LAB-000-001` §5; services declared in `.devcontainer/`. Consumes the `BK-009` relational data layer as its seed schema. |
| `BK-009` | Relational JSON Data Layer (`RFC-LAB-000-002`) | P1 | Data | ✅ Delivered (SPRINT-05, `TSK-030`) | User & project masters + many-to-many memberships join under `data/`; generated README registry; referential-integrity validator pillar. PocketBase-ready schema; foundation for `BK-008` + `BK-007` RBAC. |
| `BK-011` | Control Hub Web App MVP (`RFC-LAB-000-008`) | P1 | Platform | Scoped (`TSK-042`) | MVP: logged-in user sees live portfolio from PocketBase; **owner edits own project's status**; deployed. **Minimum RBAC** = 3 tiers (public / authenticated / owner via `owner_id`), deferring the full 5-role `memberships` model + audit. Phases M1 (wire UI→PB) → M5 (deploy). Foundation verified: provisioning + seed live on PocketBase v0.40. |
| `BK-012` | App-Level Settings | P2 | Platform | Backlog | Configurable app settings, initialized minimal and grown over time (PocketBase-backed settings collection + typed accessors). **Foundation for `BK-013` branding** (name/description/logo are settings). Needs a small RFC (schema/pattern decision) before scoping. |
| `BK-013` | Branding & White-Labeling | P2 | Platform | Backlog | App name (default: repo name), description (default: repo description), and logo set (icon / small / medium) — ready for per-client white-labeling on deploy. **Consumes `BK-012` settings**; pre-req for client deployments (relates to `RFC-LAB-000-011`). RFC (design decision) → Spec. |
| `BK-014` | Admin Project CRUD (UI) | P2 | Platform | Backlog | Manage projects (create/read/update/delete) from the UI under an **administrator persona**. **Superset of MVP M4** (owner-edits-own-status) — requires auth (M2) + an admin role, which `RFC-LAB-000-008` deferred (5-role model). Sequence after MVP auth+RBAC; likely a post-MVP epic. |
| `BK-015` | AI Assistant — Ask-the-Portfolio | P1 | AI/Platform | Backlog | **Flagship**: CTO / Project Owner ask casual natural-language questions about a project/portfolio, grounded in repo + repo-docs + `data/`. Retrieval over repo/docs + LLM. Needs its own RFC + a feasibility spike (index strategy, model, cost, data boundaries, where it runs) before scoping. Highest value, highest effort. |
