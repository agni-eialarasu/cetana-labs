---
name: create-lab-project
description: Scaffolds a new lab project folder with standardized templates and registers it in the master README.
---

# Skill: Create Lab Project

## Objective
Scaffold a new lab project directory (`projects/LAB-XXX-<slug>/`) adhering to the chosen archetype, populate initial metadata, create `STATUS.md`, and register the new project in the root `README.md` table.

---

## Step-by-Step Procedure

### 1. Determine Next Project ID
- Inspect existing folders inside `projects/`.
- Find the highest `LAB-XXX` number (e.g. `LAB-003`).
- Increment by 1 with 3-digit zero padding (e.g. `LAB-004`).

### 2. Determine Archetype & Slug
- Identify the project archetype:
  - `mini-app` (Coding with external repo)
  - `research` (Spikes, feasibility, evaluations)
  - `data-collection` (Datasets, scrapers, pipelines)
  - `verification` (Benchmarks, QA harnesses, stress tests)
- Format the folder name: `projects/LAB-XXX-<slug>/` (e.g. `projects/LAB-004-eval-engine/`).

### 3. Copy Template Files
- Copy the three template files from `templates/<archetype>/`:
  - `README.md`
  - `STATUS.md`
  - `journal.md`

### 4. Populate Project Files
- **`README.md`**: Fill in Project ID, Title, Archetype, Health (`🟢 On Track`), Owner, and Remote Repo / External links.
- **`STATUS.md`**: Fill in 2-sentence elevator pitch, latest wins, current focus, and verified metrics per `docs/project-protocol.md`.
- **`journal.md`**: Initialize the Phase Summary table and add the first `[YYYY-MM-DD]` Milestone entry documenting the creation/inception.

### 5. Update Master Registry
- Insert a new row in root `README.md` in the **Master Project Registry** table:
  ```markdown
  | **`LAB-XXX`** | **[Project Title](projects/LAB-XXX-<slug>/README.md)** | Archetype Icon + Name | Health | Owner | Remote Link | [STATUS.md](projects/LAB-XXX-<slug>/STATUS.md) |
  ```
