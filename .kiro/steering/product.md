# Product — Cetana Labs Control Hub

Cetana Labs (`LAB-000`) is the central **engineering command plane, master project registry, and operational lab notebook** for a portfolio of engineering initiatives — mini-apps, research spikes, data pipelines, and benchmark verifications.

## What it is
- A **master control plane, not a monorepo.** It stores project charters, executive `STATUS.md` files, sprint backlog, changelog, milestone journals, and (as of `BK-009`) a relational data layer. Mini-app source code lives in **external** repositories.
- It eliminates manual status friction: a daily automated broadcast and an on-demand `/project-status` generate WhatsApp-ready executive updates from lightweight `STATUS.md` files.

## Who it's for
- **Leadership / management** — instant, high-fidelity executive portfolio status without interrupting engineering flow.
- **Project leads** — a low-overhead protocol (`STATUS.md` under 35 lines) to report health, wins, focus, and blockers.

## Current trajectory
- Evolving from a static file-based control plane into a **full web application** (`BK-008`): PocketBase backend + SvelteKit "Sleek UI", with auth & RBAC (`BK-007`) scoped. See `docs/rfc/` for the decision record (RFC-LAB-000-001 … -006).

## Guiding principles
- Zero-overhead executive visibility; constructive (non-surveillance) accountability.
- Governance is explicit, auditable, and version-controlled.
- Correctness over speed: validate before claiming done.
