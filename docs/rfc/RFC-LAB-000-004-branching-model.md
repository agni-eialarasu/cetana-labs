# RFC-LAB-000-004: Branching & Contribution Model

| Property | Value |
| :--- | :--- |
| **RFC ID** | `RFC-LAB-000-004` |
| **Title** | Branch-Based Development, PR Review & Contribution Model |
| **Author** | Eialarasu (LAB-000 Control Hub) |
| **Status** | ✅ Accepted |
| **Date** | 2026-09-24 |
| **Supersedes** | `AGENTS.md` §1.6 (trunk-based direct commits) — for application code |
| **Triggered By** | `BK-008` web-app evolution (`RFC-LAB-000-003`) introducing runnable code, a database, and migrations |

---

## 1. Context & Problem Statement

Until now Cetana Labs was a static, file-based control plane, so **trunk-based direct commits to `main`** (`AGENTS.md` §1.6) were the correct, lean choice: the "build" was just regenerating Markdown/HTML, and a bad commit was trivially reverted.

`BK-008` changes this. The repository now grows **runnable application code** (a PocketBase server, a data importer, schema **migrations**) and multiple concurrent workstreams (backend, importer, UI). In this regime a bad change can break a running service or corrupt data — not merely a document. This is the industry-standard trigger to adopt **branch-based development with pull-request review and CI gates**.

## 2. Decision

Adopt **GitHub Flow** (protected `main` + short-lived feature branches → PR → squash-merge), applied via a **hybrid, path-scoped policy**:

- **Application code changes require a PR** with green CI before merge.
- **Governance / documentation changes may still fast-path** directly to `main` (preserving the zero-friction status cadence).

No long-lived `develop` branch — it adds merge overhead without payoff at this team size. Full GitFlow is explicitly rejected as over-ceremony.

## 3. Branch Model

```text
main  (always deployable • protected • linear history)
  ├── feat/bk008-p1-pocketbase-standup     # new app capability
  ├── feat/bk008-importer
  ├── fix/importer-null-repo-url            # bug fix
  ├── chore/branching-model                 # tooling / meta
  └── docs/...                              # (docs may also fast-path to main)
```

- **`main`** is always deployable and **protected**: no direct pushes of application code; changes arrive via PR with passing checks.
- **Feature branches are short-lived** (hours–days), branched from `main`, one focused unit of work each, deleted after merge.
- **Squash-merge** into `main` keeps history clean and linear (consistent with the prior trunk-based history).

## 4. Branch Naming Convention

`<type>/<scope>-<slug>` — lowercase, hyphenated. `type` mirrors the semantic commit prefixes:

| Type | Use |
| :--- | :--- |
| `feat/` | New capability (e.g. `feat/bk008-importer`) |
| `fix/` | Bug fix |
| `chore/` | Tooling, deps, meta |
| `docs/` | Documentation / RFC |
| `refactor/` | Non-behavioral restructuring |

Where relevant, include the backlog/task ref in the scope (e.g. `feat/bk008-p1-...`).

## 5. Pull Request Policy

1. **Required green CI**: every PR must pass the CI workflow (`validate_portfolio.py` + the `/project-validate` 5-pillar gate + registry `--check`) before merge.
2. **Squash-merge only**; the squash commit message uses a semantic prefix (§ `AGENTS.md` 2) and references the backlog/task ID.
3. **PR title = the intended squash commit** (semantic prefix + summary).
4. **Small, focused PRs**; delete the branch on merge.
5. **In this sandbox environment**, PRs are created via `gh api repos/{owner}/{repo}/pulls` (REST) — not `gh pr create`.

## 6. Hybrid Path-Scoping Rule (What Requires a PR)

| Change touches… | Path (indicative) | Flow |
| :--- | :--- | :--- |
| **Application code** | `app/`, `server/`, `migrations/`, `scripts/pb_*`, importer/UI code | **PR + green CI (required)** |
| **Relational data** | `data/*.json`, `data/*.schema.json` | **PR + green CI (required)** |
| **Governance / docs** | `STATUS.md`, `journal.md`, `BACKLOG.md`, `CHANGELOG.md`, `README.md`, `docs/**` | **May fast-path to `main`** (PR optional) |

Automated skills that mutate governance files (`/project-update`, `/sprint-done`, `/ping-leads`, `log-milestone`) retain their direct-to-`main` fast path.

> **Tightening clause**: once the PocketBase app becomes the source of truth (`RFC-LAB-000-003` Phase 4), `data/` and app config move fully under the PR gate, and the hybrid exception narrows to pure narrative docs.

## 7. CI as Required Status Checks

The existing validators run as a **`pull_request`-triggered** workflow (`.github/workflows/ci-validate.yml`) and are registered as **required status checks** on `main` via branch protection. This is a strict upgrade of the current push-time validation — the same checks now gate merges, not just record post-hoc.

## 8. Versioning & Releases

- Continue semantic versioning; each `/sprint-done` cuts a `vX.Y.0` release.
- **Tag releases on `main`**: `git tag vX.Y.0 && git push --tags` at closeout (formalizes existing practice; enables clean rollback points).

## 9. Rollback Strategy

- **Revert via PR**: to undo a merged change, open a revert PR (`git revert <sha>`) — never force-push `main`.
- Because migrations are now in play, prefer forward-fix migrations over destructive rollbacks where data is involved.

## 10. Migration / Adoption

1. Ratify this RFC and update `AGENTS.md` §1.6 to the hybrid model. ✅
2. Add the `pull_request` CI workflow + PR template.
3. **Dogfood**: land this RFC itself as the first PR.
4. Enable branch protection on `main` (require PR + the CI status check).
5. All `BK-008` phase work proceeds on `feat/*` branches via PRs.

## 11. Risks & Mitigations

| Risk | Mitigation |
| :--- | :--- |
| PR ceremony slows routine status updates | Hybrid rule keeps governance/docs on the fast path. |
| Sole admin can bypass protection | Accepted; protection is a guardrail, not a hard wall, at this team size. |
| History fragmentation | Squash-merge preserves linear, readable `main` history. |
| CI flakiness blocks merges | Validators are deterministic and zero-dependency; low flake risk. |
