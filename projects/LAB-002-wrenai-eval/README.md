# LAB-002: WrenAI Capabilities & Semantic GenBI Evaluation

| Property | Value |
| :--- | :--- |
| **Project ID** | `LAB-002` |
| **Archetype** | 📑 Research / Feasibility Spike |
| **Status** | 🟢 Active |
| **Owner** | Eialarasu ([@agni-eialarasu](https://github.com/agni-eialarasu)) |
| **Target Technology** | [WrenAI](https://www.getwren.ai/) ([GitHub: Canner/WrenAI](https://github.com/Canner/WrenAI)) |
| **Practical Reference / Proof** | [LAB-001: AAMAS](../LAB-001-ammas/README.md) ([github.com/agni-eialarasu/ammas](https://github.com/agni-eialarasu/ammas)) |
| **Outcome / Recommendation** | Adopted for GenBI Conversational Analytics in edge/local dashboards |
| **Executive Status** | [STATUS.md](STATUS.md) |
| **Last Updated** | 2026-09-23 |

---

## 1. Research Objectives & Problem Statement

To evaluate **WrenAI** as an open-source, semantic-engine-driven GenBI (Generative Business Intelligence) layer for local data sources (e.g. SQLite, PostgreSQL) with local/hosted LLMs:
- How reliable is WrenAI's **Modeling Definition Language (MDL)** in preventing LLM SQL hallucinations compared to direct text-to-SQL prompting?
- Can WrenAI operate fully on-premise / locally using **Ollama** (e.g., Qwen, Llama 3) without sending proprietary schema/data to cloud APIs?
- What are the compute footprint, Docker dependencies, and response latencies when running alongside edge systems?

---

## 2. Evaluation Matrix & Key Findings

| Area | Evaluation Criteria | Finding / Observation | Verdict |
| :--- | :--- | :--- | :---: |
| **Semantic Modeling (MDL)** | Context grounding & schema definition | Declarative MDL manifest (`manifest.json`) defines relationships, calculations, and dimension constraints reliably. | 🟢 Excellent |
| **Local LLM Integration** | Compatibility with local providers | Works smoothly with Ollama endpoints for embeddings and SQL generation. | 🟢 Supported |
| **Text-to-SQL Accuracy** | Complex aggregations & date filters | Significantly outperforms raw prompt engineering on structured time-series and event outbox tables. | 🟢 High Precision |
| **Topology & Resource Footprint** | Memory & container overhead | Multi-container stack (Wren Engine, AI Service, UI, Qdrant vector store) requires ~4-8 GB RAM. Best hosted on a companion machine or local server rather than ultra-constrained edge devices. | 🟡 Needs Companion Host |

---

## 3. Practical Implementation & Verification

The practical proof-of-concept for this evaluation was implemented in **[LAB-001: AAMAS](../LAB-001-ammas/README.md)**:
- **Use Case**: Caregiver conversational queries over behavioral telemetry outbox (`data/outbox.db`).
- **Semantic Manifest**: Generated MDL modeling behavioral events, duration aggregations, and stimming frequencies.
- **Topology**: Dual-device architecture where the edge device sends lightweight queries to a companion WrenAI host.

---

## 4. Documentation Links

- 📋 [Executive Status (STATUS.md)](STATUS.md) — 30-line executive status, health, and latest findings.
- 🗓️ [Research Journal](journal.md) — Evaluation milestones, architectural discoveries, and benchmark notes.
