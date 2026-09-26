---
name: project-add
description: >-
  Scaffolds and registers a new initiative under Cetana Labs using remote-first inspection or manual parameters (e.g. "/project-add https://github.com/org/repo", "/project-add 'Title' mini-app Eialarasu").
---

# Skill: Onboard New Initiative (`/project-add`)

## Objective
Scaffold a new project directory (`projects/LAB-XXX-<slug>/`), inspect remote GitHub repositories for automatic metadata extraction, initialize `STATUS.md`, and register the project in the master `README.md`.

---

## 1. Trigger Patterns
Activate this skill whenever the user invokes:
- `/project-add <github_repo_url>`
- `/project-add "<Project Title>" [archetype] [owner]`
- `/project-add` (interactive questionnaire)

---

## 2. Step-by-Step Procedure

### Step 1: Resolve Project ID
- Inspect existing folders inside `projects/` starting with `LAB-` (and root `README.md`).
- Determine the highest numerical ID (e.g. `LAB-004`).
- Increment by 1 with 3-digit zero-padding: `LAB-XXX` (e.g. `LAB-005`).

### Step 2: Remote-First Inspection (If URL Provided)
If a GitHub repository URL is passed (e.g. `https://github.com/org/repo`):
1. Use `read_url_content` or `run_command` with `gh repo view <org/repo>` / `curl` to fetch the repository's `STATUS.md` or `README.md`.
2. Check if remote `STATUS.md` already exists:
   - **If remote `STATUS.md` exists**: Adopt its verified wins, metrics, and health badge (`🟢 On Track`).
   - **If remote `STATUS.md` is NOT yet created**: Initialize health as **`⏳ Onboarding Pending`**. This triggers constructive visibility alerts on morning management broadcasts until the lead runs `/status-init`.
3. Extract:
   - **Title / Name**: Repository name or H1 header.
   - **Elevator Pitch**: 2-sentence purpose from README intro.
   - **Archetype**:
     - `mini-app` if it contains code / package manifests (`pyproject.toml`, `package.json`, `Cargo.toml`).
     - `research` if it is documentation / notes / benchmarks.
     - `data-collection` if it is scraping / dataset focused.
   - **Tech Stack**: Languages and frameworks detected.
   - **Owner**: Specified `--owner` or repository maintainer.

### Step 3: Scaffold Project Directory
Create directory: `projects/LAB-XXX-<slug>/`:
1. **`README.md`**: Project charter, architecture diagrams, tech stack, and remote GitHub link.
2. **`STATUS.md`**: Initialized per `docs/project-protocol.md`:
   - `Current Health: ⏳ Onboarding Pending` (or `🟢 On Track` if verified remotely).
   - Initial Elevator Pitch, setup status, and clear pointer to `/status-init`.
3. **`journal.md`**: First milestone entry `[YYYY-MM-DD] Milestone: Project Inception`.

### Step 4: Register in Master `README.md`
Insert a new row in the **Master Project Registry** table:
```markdown
| **`LAB-XXX`** | **[Project Name](projects/LAB-XXX-<slug>/README.md)** | Archetype | `⏳ Onboarding Pending` | Owner | [GitHub Repo](URL) | [STATUS.md](projects/LAB-XXX-<slug>/STATUS.md) |
```

### Step 5: Commit Directly to `main`
Execute trunk-based commit:
```bash
git add . && git commit -m "feat(lab-XXX): init <slug> project"
git push origin main
```

### Step 6: Generate Preview
Run:
```bash
python3 scripts/generate_status.py LAB-XXX
```
Present the resulting WhatsApp broadcast to the user along with the shareable `/status-init` developer prompt pack.
