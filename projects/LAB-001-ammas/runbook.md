# LAB-001: AAMAS — Operational Runbook

This runbook covers local setup, operational execution, test suites, and troubleshooting for the AAMAS edge system located in [github.com/agni-eialarasu/ammas](https://github.com/agni-eialarasu/ammas).

---

## 1. Prerequisites & Environment

- **Python**: 3.11+
- **Hardware**: Standard consumer webcam or video files for ingestion (Apple Silicon / Linux / Windows supported).
- **Optional Services**: Twilio account (for SMS alerts), Docker (for WrenAI GenBI container stack).

---

## 2. Installation & Quick Setup

```bash
# Clone the repository
git clone https://github.com/agni-eialarasu/ammas.git
cd ammas

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment settings
cp .env.example .env
```

---

## 3. Operational Commands

### A. Run Automated Verification Tests
```bash
# Execute unit and integration tests (no webcam required)
pytest
```

### B. Live Edge Camera Monitor
```bash
# Terminal 1: Optional mock webhook receiver
python mock_server.py

# Terminal 2: Run live camera detection loop
python src/main.py
```

### C. Offline Recorded Video Ingestion
```bash
# Process a recorded video file into local SQLite outbox & CSV logs
python -m src.ingest samples/sample-2.mp4
```

### D. Run Web Dashboard & 3D Skeleton Replay Viewer
```bash
# Start standalone web server
python -m src.server --port 8000

# Access dashboard in browser: http://localhost:8000
```

---

## 4. Configuration Reference (`.env`)

| Key | Description | Default |
| :--- | :--- | :--- |
| `CAMERA_INDEX` | Webcam device index | `0` |
| `WEBHOOK_URL` | Endpoint to dispatch alert payloads | `http://localhost:5000/alerts` |
| `ENABLE_RAW_CLIP_CAPTURE` | Opt-in raw episode clip storage | `false` |
| `TWILIO_ACCOUNT_SID` | Twilio account SID for SMS | *(optional)* |
| `TWILIO_AUTH_TOKEN` | Twilio auth token | *(optional)* |

---

## 5. Troubleshooting & Diagnostics

- **Webcam Access Denied (macOS)**: Ensure Terminal / IDE has Camera Permissions granted under *System Settings > Privacy & Security > Camera*.
- **MediaPipe Pose Task Missing**: Ensure `pose_landmarker.task` is present in repository root.
- **Port Conflict on 8000**: Start server with custom port via `python -m src.server --port 8080`.
