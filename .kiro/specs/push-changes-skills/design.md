# Push-Changes Skills — Design

| Property | Value |
| :--- | :--- |
| **Spec ID** | `push-changes-skills` |
| **Branch** | `feat/push-changes-skills` |
| **Builds on** | `/commit-changes` skill; `RFC-LAB-000-004` branching model |

---

## 1. Approach

Two thin, composable markdown skills — no scripts, no app code. The design principle is **branch-awareness as a shared gate**: both skills route through one decision table before any `git push`, so the branching model (`RFC-LAB-000-004`) is enforced in the procedure, not left to recall.

```
/commit-and-push-changes  =  /commit-changes  →  /push-changes
/push-changes             =  [branch-aware push gate]  →  git push origin <branch>
```

## 2. The branch-aware push gate (shared logic, documented in /push-changes)

```text
current = git rev-parse --abbrev-ref HEAD

IF current in {main, master}:
    changed = paths in the commits not yet on origin/<current>
    IF changed ⊆ {governance/docs: STATUS.md, journal.md, SPRINT_TRACKER.md,
                  BACKLOG.md, CHANGELOG.md, README.md, docs/**, *.md governance}:
        → fast-path eligible (RFC-004). CONFIRM with operator, then push.
    ELSE (code / data/ / migrations present):
        → REFUSE. Instruct: move to a feat/ branch + PR. Do NOT push.
ELSE (feat/|fix/|chore/|refactor/ branch):
    → push origin <current> (add -u if no upstream). No confirmation needed.

NEVER: --force / --force-with-lease to a protected branch, --all, --mirror,
       bare `git push`, HEAD/@ targets.
IF up-to-date with remote: report "nothing to push" and exit 0.
```

This mirrors `/commit-changes`'s own path logic and the runtime's protected-branch guard — the skill makes the guard *predictable* (explains before it refuses) rather than letting the operator hit a raw policy block.

## 3. Skill file shapes

**`.kiro/skills/push-changes/SKILL.md`** — frontmatter + a Step-by-Step that: (1) `git status` + `git log origin/<branch>..HEAD` to list what would push, (2) run the §2 gate, (3) push by explicit name, (4) report the pushed ref / remote URL. Owns the full gate text (it is the single source).

**`.kiro/skills/commit-and-push-changes/SKILL.md`** — frontmatter + a short procedure that defers to `/commit-changes` for the commit half and to `/push-changes` for the push half, with one worked example per path (feat/ branch; docs-on-main; code-on-main → refuse-at-push). No rule duplication — it cross-references.

## 4. Why not one combined skill or a script?

- **Two skills, not one:** the operator sometimes wants to push *already-committed* work (e.g. the current unpushed `8a55612` docs commit) without re-committing — that's `/push-changes` alone. Bundling would force a no-op commit.
- **Markdown, not a shell script:** the logic is a *decision procedure the agent follows*, consistent with every other `/command` here; a script would duplicate the runtime's own guard and risk drifting from it.

## 5. Risks & mitigations

| Risk | Mitigation |
| :--- | :--- |
| Skill tempts a code push to `main` | §2 gate refuses; runtime guard is the backstop. |
| Gate's "governance/docs" set drifts from `RFC-004` | Skill cites the RFC's exact path list; `/audit-doc` catches drift. |
| Operator surprised by a confirmation prompt on `main` | Skill explains *why* (fast-path vs PR) before prompting. |
| Duplicated rules rot | `/commit-and-push-changes` cross-references, never copies. |
