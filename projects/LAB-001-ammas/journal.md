# LAB-001: AAMAS — Project Journal & Timeline

## 📌 Phase Summary

| Phase | Focus Area | Status | Target / Completion Date |
| :--- | :--- | :--- | :--- |
| **Phase 1: Core CV Pipeline & Heuristics** | In-memory MediaPipe pose detection, FFT stimming classifier, and webhook alerts | ✅ Completed | 2026-08-30 |
| **Phase 2: Offline Ingestion & Canvas Replay** | Headless video ingest CLI, SQLite outbox, and HTML5 3D skeleton replay | ✅ Completed | 2026-09-03 |
| **Phase 3: GenBI Conversational Analytics (v2.0)** | WrenAI MDL modeling, Ollama integration, and "Ask AI" dashboard drawer | ✅ Completed | 2026-09-04 |
| **Phase 4: Multi-Model Evaluation & Refinement** | Real-world benchmark validation and continuous edge optimization | 🟢 Active | 2026-09-30 |

---

## 🗓️ Milestone Log

### [2026-09-06] Milestone: Central Lab Hub Registration
- **Context**: Integrated AAMAS into `cetana-labs` as the foundational master reference (`LAB-001`).
- **Key Decisions**:
  - Decoupled code repo maintained at [github.com/agni-eialarasu/ammas](https://github.com/agni-eialarasu/ammas).
  - High-level runbooks, telemetry architecture, and phase histories tracked centrally here.
- **Next Steps**: Benchmark real-time multi-person edge latency and validate ML classifier precision.

---

### [2026-09-04] Milestone: WrenAI GenBI Analytics Layer Integrated
- **Context**: Released v2.0 conversational analytics embedded in the local web dashboard.
- **Key Decisions**:
  - Implemented semantic MDL manifest (`wrenai/mdl/manifest.json`) targeting SQLite `outbox.db`.
  - Added dual-device topology deployment scripts for companion AI hosts running Ollama.

---

### [2026-09-03] Milestone: Offline Video Ingest & HTML5 3D Skeleton Replay
- **Context**: Added headless processing capability for pre-recorded clinical/observational videos.
- **Key Decisions**:
  - Anonymized 11-joint 3D skeleton trajectories stored in `data/outbox.db`.
  - Built zero-dependency Python web server (`src/server.py`) rendering canvas animations.

---

### [2026-08-30] Milestone: Inception & Core Real-Time CV Pipeline
- **Context**: Initial prototype of edge behavioral monitoring.
- **Key Decisions**:
  - Strict privacy-first rule: zero video frames persisted to disk by default.
  - Multi-threaded non-blocking camera loop using MediaPipe Pose Landmarker.
  - Dual classification: FFT-based frequency analysis and heuristic posture rules.
