# LAB-002: WrenAI Capabilities — Evaluation Runbook

This runbook documents the steps to set up, configure, and evaluate WrenAI with local SQLite data sources and Ollama LLMs.

---

## 1. Prerequisites & Environment

- **Docker & Docker Compose**: 24.0+
- **Ollama**: Running locally with a chat model (e.g. `llama3.2`, `qwen2.5`) and an embedding model (e.g. `nomic-embed-text` or `bge-m3`).
- **RAM / Resources**: Minimum 6 GB recommended for WrenAI containers + local LLM.

---

## 2. Launching WrenAI Stack

```bash
# 1. Clone WrenAI or navigate to your evaluation directory
git clone https://github.com/Canner/WrenAI.git
cd WrenAI

# 2. Configure environment settings
cp .env.example .env

# Configure LLM provider in .env (or via WrenAI UI):
# LLM_PROVIDER=ollama
# OLLAMA_BASE_URL=http://host.docker.internal:11434

# 3. Launch Docker Compose services
docker compose up -d
```

---

## 3. Configuring Data Source & Semantic MDL

1. **Access WrenAI UI**: Navigate to `http://localhost:3000` (or configured port).
2. **Connect Data Source**: Select SQLite / PostgreSQL / DuckDB and attach your database file or connection URI.
3. **Define Semantic Models**:
   - Define primary tables, primary keys, and relationships.
   - Configure calculated measures (e.g. `total_stimming_duration = SUM(duration)`).
   - Configure dimension hierarchies and descriptions for column grounding.
4. **Export Manifest**: Save generated `manifest.json` for reproducible deployments.

---

## 4. Query Evaluation & Testing

Test natural language queries against the semantic engine:

```text
Query 1: "How many stimming episodes occurred yesterday between 2 PM and 5 PM?"
Expected SQL: SELECT COUNT(*) FROM episodes WHERE episode_type = 'STIMMING' AND timestamp BETWEEN ...

Query 2: "What was the average episode duration by type over the last 7 days?"
Expected SQL: SELECT episode_type, AVG(duration) FROM episodes WHERE timestamp >= ... GROUP BY episode_type
```

---

## 5. Troubleshooting & Diagnostics

- **Ollama Connection Refused in Docker**: Use `http://host.docker.internal:11434` instead of `localhost` on macOS/Windows, or check `OLLAMA_ORIGINS="*"` on Linux.
- **SQL Hallucination / Missing Joins**: Add explicit relationship semantics in the MDL manifest instead of relying on implicit schema inference.
- **High Latency**: Pre-warm Ollama model in memory (`ollama run <model>`) or use smaller quantized parameter models (e.g. 7B/8B).
