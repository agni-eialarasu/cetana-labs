# RFC-LAB-000-010: Portfolio & Sprint Tracking Model

| Property | Value |
| :--- | :--- |
| **RFC ID** | `RFC-LAB-000-010` |
| **Title** | Portfolio & Sprint Tracking Model — the three-tier funnel (Backlog → Sprint → Changelog) |
| **Author** | Eialarasu (LAB-000 Control Hub) |
| **Status** | 🟡 Proposed |
| **Date** | 2026-09-27 |
| **Backlog** | `SPRINT-09` |
| **Builds On** | `RFC-LAB-000-009` (sprint lifecycle & state machine), `RFC-LAB-000-004` (branching/PR), `RFC-LAB-000-002` (relational data) |
| **Influenced By** | Nexus Pulse (`LAB-003`) `SPRINT_TRACKER.md` / `BACKLOG.md` separation — adapted, not copied |
| **Decision Journal** | Entry 005 |

---

## 1. Context & Problem Statement

Cetana Labs (`LAB-000`) is becoming the **proven blueprint for the AIDLC framework** — a reference other repositories will copy. Its work-tracking must therefore be **industry-standard and portable**, not bespoke.

Today, tracking is functional but **conflated**: `BACKLOG.md` holds *both* the active sprint (committed, in-flight work) *and* the idea bucket (future/unrefined initiatives), and its status vocabulary (`✅ Done`, `🚧 In Progress`, `📋 Planned`) is separate from the lifecycle state machine defined in `RFC-LAB-000-009` §3.1. For a blueprint, three concerns should be **physically distinct** and use **one shared vocabulary**.

## 2. Decision (summary)

Adopt the standard **three-tier funnel**, with each tier a distinct artifact and a single shared status vocabulary aligned to the lifecycle state machine:

```
BACKLOG.md            SPRINT_TRACKER.md              CHANGELOG.md
(ideas / the shelf)   (committed, in-flight work)    (shipped history)
─────────────────     ──────────────────────────     ──────────────────
BK-xxx ideas   ──(Definition of Ready:  ──▶  TSK-xxx items moving   ──(released)──▶  versioned
prioritized,       Spec merged to main)      through the state             release entries
groomed                                       machine                       + git tag
```

1. **Split `SPRINT_TRACKER.md` from `BACKLOG.md`** — the tracker holds *only* the active/committed sprint(s) + the delivered archive; the backlog holds *only* the idea bucket (future initiatives, prioritized, groomed).
2. **Status vocabulary = the `RFC-LAB-000-009` state machine** — one set of states everywhere, no separate tracker dialect.
3. **Definition of Ready (backlog → sprint) = the Spec is merged to `main`** — i.e. the merge-first `/plan-done` transition. An item is sprint-ready exactly when `READY_TO_BUILD`.
4. **An explicit traceability chain** links an idea to its shipped code and back.

This is the standard **Product Backlog → Sprint Backlog → Release** funnel, expressed in files, aligned to the lifecycle we already run.

## 3. The three tiers (artifacts & responsibilities)

| Tier | File | Holds | Does NOT hold |
| :--- | :--- | :--- | :--- |
| **Idea bucket** | `BACKLOG.md` | `BK-` initiatives — prioritized (P1–P3), archetyped, groomed. The "someday/maybe" shelf. | Sprint task states; in-flight work |
| **Sprint tracker** | `SPRINT_TRACKER.md` | The **Current Sprint** (committed `TSK-` items + states) and the **Delivered Sprints Archive**. | Unrefined ideas; long-term roadmap |
| **Shipped history** | `CHANGELOG.md` | Released, versioned entries (Keep a Changelog) + git tag per release. | Planned/in-flight work |

**Why split (vs. keeping one file):** for a portable blueprint, the funnel should be *physically obvious* — a reader (or an agent onboarding cold) sees three files for three concerns. It also matches the Nexus Pulse reference (`docs/sprints/SPRINT_TRACKER.md` + `BACKLOG.md`) we are standardizing toward, and cleanly separates the two audiences: backlog = product/prioritization; tracker = execution.

## 4. Shared status vocabulary (= the lifecycle state machine)

The `SPRINT_TRACKER.md` status column uses the **exact states** of `RFC-LAB-000-009` §3.1 — no parallel dialect:

| Status | Meaning | Lifecycle state |
| :--- | :--- | :--- |
| `📋 Backlog` | An idea, not yet committed (lives in `BACKLOG.md`) | — (pre-funnel) |
| `✅ Ready` | Committed to a sprint; **Spec merged** to `main` | `READY_TO_BUILD` |
| `🔨 In Progress` | Being implemented (`/spec-run` running / interactive build) | (Build) |
| `🔍 In Verification` | Human functional verification loop | `IN_VERIFICATION` |
| `👀 In Review` | At the human PR gate | `IN_REVIEW` |
| `✅ Done` | Merged + recorded | `RECORDED` |

One vocabulary across the tracker, the lifecycle commands, and the guide — the blueprint payoff.

## 5. Definition of Ready (the backlog → sprint gate)

An item may enter `SPRINT_TRACKER.md` (leave the idea bucket) only when it is **Ready**:

- It has an **ID** (`TSK-` in the tracker, tracing to a `BK-` initiative where applicable).
- It has a **rough size / priority**.
- **For delegated/AIDLC work: its Kiro Spec is authored and merged to `main`** (the merge-first `/plan-done` transition → `READY_TO_BUILD`). Lead-paired work uses a lighter ready-bar (a scoped tracker row), per progressive formality (`RFC-LAB-000-009` §5).

This makes the **funnel = the lifecycle**: "sprint-ready" is not a separate judgment — it is the `READY_TO_BUILD` state. It prevents the classic failure of half-baked items entering a sprint.

## 6. Traceability chain (blueprint-grade)

Every unit of work is traceable end-to-end, in both directions:

```
BK-xxx (idea)  →  TSK-xxx (sprint item)  →  .kiro/specs/<id>/ (Spec)  →  PR #NN  →  CHANGELOG entry  →  git tag vX.Y.0
```

- The tracker row cites the `BK-` it serves and the `TSK-`/Spec id.
- The Spec's `REPORT.md` cites the PR; the CHANGELOG entry cites the `TSK-`/PR; the release cites the tag.
- Result: from a shipped line in the CHANGELOG you can walk back to the originating idea, and from a backlog idea forward to its shipped code — the auditable thread a governed AIDLC framework needs.

## 7. Migration (what changes, mechanically)

*This RFC is the decision of record. The mechanical refactor is delivered as a follow-on Kiro Spec (§9), merge-first.*

- **Create `SPRINT_TRACKER.md`**: move the **Current Sprint** block + **Delivered Sprints Archive** out of `BACKLOG.md` into it.
- **Trim `BACKLOG.md`** to the **Prioritized Backlog** (idea bucket) only.
- **Re-map statuses** to the §4 vocabulary in the tracker.
- **Update the lifecycle skills** that read/write these files — `/sprint-start`, `/sprint-done` (and references in `/plan-*`, `/spec-run`, `/review-pr`) — to target `SPRINT_TRACKER.md` for sprint state and `BACKLOG.md` for ideas.
- **Update references**: `AGENTS.md` §1.5/§4, `docs/work-environment.md`, `docs/sprint-lifecycle.md`, `README.md`, and any validator that checks lockstep (`scripts/validate_portfolio.py` / status generators) — verify none hard-code the current single-file layout.
- **Preserve history**: use `git mv` where moving whole sections is possible; keep the delivered archive intact.

## 8. Scope & Non-Goals

- **In scope:** the three-tier file model, the shared status vocabulary, the Definition of Ready, the traceability chain.
- **Non-goals:** changing the lifecycle commands' *behavior* (only their file targets); introducing an external tracker (Jira/Linear) — this stays git-native and portable; the Track-A/B roster (still deferred, `RFC-LAB-000-009` §8).

## 9. Deliverables

- **This RFC** (decision of record).
- (Follow-on Kiro Spec, merge-first — its own PR set): the §7 mechanical refactor — create `SPRINT_TRACKER.md`, trim `BACKLOG.md`, re-map statuses, update the skills + references + validators. Tracked as a backlog item and run via the AIDLC lifecycle (dogfooding the very model this RFC defines).

## 10. Open Questions

1. **Multiple concurrent sprints?** For solo+AI today, one Current Sprint suffices; the tracker format should not preclude a second active sprint later. *(Leaning: single Current Sprint block now, extensible.)*
2. **Where does the delivered archive live** — in `SPRINT_TRACKER.md`, or its own `docs/sprints/` history? *(Leaning: in `SPRINT_TRACKER.md` for now; split later if it grows.)*
3. **Validator enforcement** — should `scripts/validate_portfolio.py` gain a pillar checking the traceability chain / status-vocab conformance? *(Leaning: yes, in the refactor Spec — makes the blueprint self-enforcing.)*

## 11. Risks & Mitigations

| Risk | Mitigation |
| :--- | :--- |
| Refactor churn / broken references | Deliver as a Spec with a full task list; validators must stay green; verify no tool hard-codes the single-file layout (§7). |
| Two status vocabularies drift | §4 mandates the tracker reuse the state-machine states verbatim; a validator pillar can enforce it (OQ-3). |
| Over-engineering for a solo repo | Three files, one vocabulary, one gate — no external tooling; stays git-native and lightweight (§8 non-goals). |
| Blueprint diverges from what LAB-000 actually does | Dogfood: run the refactor itself through the AIDLC lifecycle, so the blueprint is proven on its own repo. |
