#!/usr/bin/env zsh
# Keep FastAPI running via uvicorn, auto-restart on crash
# Resolve repo root and ensure we run from there
REPO_ROOT="$(cd "$(dirname "$0")"/.. && pwd)"
cd "$REPO_ROOT"

# Expose repo on PYTHONPATH for imports like `src.*`
export PYTHONPATH="$REPO_ROOT"

# Load .env if present (so OPENAI_API_KEY and others are available)
if [[ -f .env ]]; then
  set -a
  source .env
  set +a
fi

# Defaults for local mock insurer if not provided
export INSURER_API_BASE="${INSURER_API_BASE:-https://mock.insurer.local}"
export INSURER_API_KEY="${INSURER_API_KEY:-dev-local}"

APP="src.app:app"
HOST="0.0.0.0"
PORT="8000"

# Prefer venv uvicorn if available, else fallback to PATH
PARENT_DIR="$(dirname "$REPO_ROOT")"
VENV_UVI="$PARENT_DIR/.venv/bin/uvicorn"
UVI_BIN="${UVI_BIN:-$VENV_UVI}"
[[ -x "$UVI_BIN" ]] || UVI_BIN="uvicorn"

while true; do
  echo "[launcher] starting $UVI_BIN $APP on $HOST:$PORT (cwd=$REPO_ROOT)"
  "$UVI_BIN" "$APP" --host "$HOST" --port "$PORT"
  code=$?
  echo "[launcher] uvicorn exited with code $code; restarting in 2s..."
  sleep 2
done
