# LAB-002: WrenAI Capabilities — Research Journal & Timeline

## 📌 Phase Summary

| Phase | Focus Area | Status | Target / Completion Date |
| :--- | :--- | :--- | :--- |
| **Phase 1: Architecture Survey & Discovery** | Evaluate WrenAI MDL vs direct Text-to-SQL prompting | ✅ Completed | 2026-09-01 |
| **Phase 2: Local Docker & Ollama Spike** | Stand up local stack with open-source LLMs | ✅ Completed | 2026-09-03 |
| **Phase 3: Practical Integration (AAMAS Proof)** | Validate with real SQLite telemetry database in LAB-001 | ✅ Completed | 2026-09-04 |
| **Phase 4: Synthesis & Dual-Device Topology** | Document deployment patterns for companion AI hosts | 🟢 Active | 2026-09-30 |

---

## 🗓️ Milestone Log

### [2026-09-06] Milestone: Centralized Research Documentation
- **Context**: Structured WrenAI evaluation as dedicated research project `LAB-002` in Cetana Labs.
- **Key Findings**:
  - Semantic MDL manifests significantly reduce SQL schema hallucinations by establishing explicit constraints and calculations before the LLM generates SQL.
  - Resource footprint requires companion AI host separation when running alongside lightweight edge capture hardware.

---

### [2026-09-04] Milestone: Practical Verification in LAB-001 (AAMAS)
- **Context**: Embedded WrenAI conversational backend into the AAMAS dashboard.
- **Key Decisions**:
  - Connected WrenAI semantic engine to local `data/outbox.db` SQLite database.
  - Verified natural language querying for episode counts, timestamps, and durations.

---

### [2026-09-01] Milestone: Initial Tech Spike & Local Ollama Testing
- **Context**: Tested WrenAI Docker Compose stack paired with local Ollama instance.
- **Key Decisions**:
  - Confirmed feasibility of 100% on-premise execution without cloud LLM dependencies.
  - Benchmarked SQL generation accuracy on time-series queries.
