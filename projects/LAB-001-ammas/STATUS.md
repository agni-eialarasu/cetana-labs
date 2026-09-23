# Project Status & Executive Summary

| Property | Value |
| :--- | :--- |
| **Project ID** | LAB-001 |
| **Project Name** | AAMAS (Autism Activity Monitoring & Alerting System) |
| **Current Health** | 🟢 On Track |
| **Owner / Lead** | Eialarasu |
| **Last Updated** | 2026-09-23 |

---

### 1. Elevator Pitch (Business Purpose)
A lightweight, privacy-first edge computer vision system for real-time behavioral monitoring (stimming and physical avoidance) that instantly alerts caregivers via Webhooks/SMS and offers interactive 3D skeleton replays with conversational GenBI analytics.

### 2. Latest Deliveries & Business Wins
- **Edge Vision & Privacy Core**: In-memory frame processing (~30 FPS MediaPipe) purging video frames each loop—storing only numeric 3D skeleton trajectories.
- **Offline Ingestion & Replay**: Batch video ingest CLI coupled with a zero-dependency web server and HTML5 Canvas 3D skeleton replay player.
- **Conversational GenBI Layer**: Integrated WrenAI semantic modeling with local Ollama LLMs for conversational queries over behavior events.

### 3. Current Focus & Next Milestone
- Edge latency benchmarking under long-running sessions and multi-person accuracy optimization.

### 4. Blockers & Risks
- **Blockers**: None.
- **Key Risks**: Edge hardware thermal and compute limits during extended continuous camera feeds.

### 5. Verified Quality Metrics
- 69/69 unit and integration tests passing across 14 modules.
- Strict linter and style compliance.
