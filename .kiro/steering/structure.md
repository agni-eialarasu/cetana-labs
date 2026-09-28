# Structure — Cetana Labs

## Layout
```text
cetana-labs/
├── README.md              # Master registry (table GENERATED from data/ — do not hand-edit the marked block)
├── STATUS.md              # Root executive status (mirror of LAB-000; ≤35 lines)
├── BACKLOG.md             # Sprint plan + prioritized backlog + delivered archive
├── CHANGELOG.md           # Keep a Changelog; semver; tag vX.Y.0 at each /sprint-done
├── AGENTS.md              # Universal agent guidelines (rules, commit conventions, branch model)
├── data/                  # Relational JSON masters + schemas (RFC-LAB-000-002) — source of truth for structural data
├── scripts/               # Zero-dependency Python governance engine + generators/validators
├── docs/
│   ├── README.md          # Docs hub + breadcrumb nav standard
│   ├── guides/            # developer-guide, user-guide, sprint-lifecycle, project-owner-guide
│   ├── reference/         # project-protocol, DESIGN, design-system-lab000
│   ├── governance/        # DECISION-JOURNAL, ai-collaboration-model
│   └── rfc/               # RFC-LAB-000-001 … -011 (decision records)
├── app/
│   ├── pocketbase/        # Backend: Containerfile, pb_hooks/, pb_schema.json, pb_provision/import
│   └── web/               # SvelteKit "Sleek UI" (deployed on Vercel; PocketBase on Railway — RFC-LAB-000-011)
├── projects/LAB-XXX-<slug>/  # Per-project README.md + STATUS.md + journal.md
├── templates/             # Archetype scaffolds
└── .kiro/
    ├── skills/            # Project /commands (this skillset)
    └── steering/          # product.md, tech.md, structure.md + conventions
```

## Conventions (see AGENTS.md for detail)
- **Flat, sequential IDs:** control hub = `LAB-000`; others `LAB-XXX-<slug>` (zero-padded, lowercase hyphenated slug).
- **Portability:** never write machine-specific absolute paths in docs; use relative/GitHub links.
- **Lockstep:** on any change, keep `README.md` registry (regenerate), `BACKLOG.md`, `CHANGELOG.md`, journals, and `data/` in sync.
- **Branching (`RFC-LAB-000-004`, hybrid):** app code / `data/` / migrations → **PR + green CI + squash-merge** into `main`; governance/docs → may fast-path. Never force-push `main`.
- **Commit prefixes:** `feat(lab-XXX)` / `log(lab-XXX)` / `status(lab-XXX)` / `chore(lab-XXX)` / `feat(governance)` / `docs:` (see AGENTS.md §2).
- **Two-Phase Governance:** run `/project-validate` (or `/validate-local`) before status emission / PR / release.

## Generated artifacts (never hand-edit)
- `README.md` registry block (between `<!-- BEGIN:registry -->` markers) → `scripts/generate_registry.py`
- `app/pocketbase/pb_schema.json` → `scripts/generate_pb_schema.py`
- `data/status.json` → `scripts/generate_status_json.py`
