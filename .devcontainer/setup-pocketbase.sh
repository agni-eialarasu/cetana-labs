#!/usr/bin/env bash
# Cetana Labs — PocketBase dev setup (BK-008 P1 / RFC-LAB-000-003)
# Best-effort: fetches the PocketBase binary into app/pocketbase/ for local/Codespaces
# development. Safe to fail (e.g. no network in the Kiro Web sandbox) — the P1
# scaffolding (schema + importer) does not require the binary to be present.
set -u

PB_VERSION="${PB_VERSION:-0.22.21}"
TARGET_DIR="app/pocketbase"
BIN="${TARGET_DIR}/pocketbase"

python3 --version || true
gh --version || true

if [ -x "$BIN" ]; then
  echo "PocketBase already present at $BIN"
  exit 0
fi

ARCH="$(uname -m)"
case "$ARCH" in
  x86_64|amd64) PB_ARCH="amd64" ;;
  aarch64|arm64) PB_ARCH="arm64" ;;
  *) echo "Unsupported arch '$ARCH' — install PocketBase manually."; exit 0 ;;
esac

URL="https://github.com/pocketbase/pocketbase/releases/download/v${PB_VERSION}/pocketbase_${PB_VERSION}_linux_${PB_ARCH}.zip"
echo "Fetching PocketBase v${PB_VERSION} (${PB_ARCH})..."
mkdir -p "$TARGET_DIR"
if curl -fsSL "$URL" -o /tmp/pb.zip 2>/dev/null && unzip -o /tmp/pb.zip -d "$TARGET_DIR" >/dev/null 2>&1; then
  chmod +x "$BIN" 2>/dev/null || true
  echo "PocketBase installed at $BIN"
  echo "Next: ./$BIN serve --http=0.0.0.0:8090  (then import app/pocketbase/pb_schema.json + run scripts/pb_import.py)"
else
  echo "Could not fetch PocketBase (offline or restricted network). Install manually when online:"
  echo "  $URL"
fi
exit 0
