# LAB-003: Nexus Pulse — Operational Runbook

**Runbook Reference:** NP-RUN-S1  
This runbook provides developer setup, test execution, golden fixture verification, and diagnostic steps for Nexus Pulse located in [github.com/eAgni-Technologies/nexus-pulse](https://github.com/eAgni-Technologies/nexus-pulse).

---

## 1. Prerequisites & Environment
- **Python**: 3.11+
- **Database**: SQLite (default for development & tests) / PostgreSQL
- **Key Extras**: `dev` extra (includes `pytest` and `httpx2` required by Starlette TestClient)

---

## 2. Fast Start & Environment Setup

```bash
# Clone repository
git clone https://github.com/eAgni-Technologies/nexus-pulse.git
cd nexus-pulse

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies including dev extras
python -m pip install -e ".[dev]"
```

---

## 3. Running Automated Test Suites

```bash
# Run full test suite (expected baseline: 126 passed)
pytest -q -rA

# Run specific domain test modules
pytest tests/modules/finance/
pytest tests/modules/commercial/
pytest tests/modules/signals/
```

---

## 4. Golden Fixture Verification (`NP-GOLDEN-001`)

Scrum-1 tests are verified against self-contained canonical fixture data located under `tests/fixtures/np_golden_001/data/`:
- **Actual Delivery Cost**: USD 76,328
- **Actual Revenue**: USD 133,800
- **Gross Margin**: USD 57,472 (Margin %: ~42.95%)
- **Forecast Variance**: Hours +50, Cost +3,540, Revenue 0, Margin -3,540

To point tests against an external copy if needed:
```bash
export NEXUSPULSE_GOLDEN_DIR="/path/to/golden_fixture_dir"
pytest
```

---

## 5. Troubleshooting & Diagnostics

- **Starlette / AnyIO Warning**: API tests may emit a `DeprecationWarning` for `anyio.abc.BlockingPortal`. This is an upstream dependency warning and non-blocking.
- **Missing TestClient Dependencies**: Ensure installation is completed via `pip install -e ".[dev]"` so `httpx2` is present.
- **Schema & Migrations**: Managed via Alembic (`alembic upgrade head`).
