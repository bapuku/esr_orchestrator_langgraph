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
PORT="${PORT:-8000}"

# Prefer repo-local venv if available
VENV_UVI="$REPO_ROOT/.venv/bin/uvicorn"
VENV_PY="$REPO_ROOT/.venv/bin/python"
if [[ -x "$VENV_UVI" ]]; then
  RUN_CMD=("$VENV_UVI" "$APP" --host "$HOST" --port "$PORT")
elif [[ -x "$VENV_PY" ]]; then
  RUN_CMD=("$VENV_PY" -m uvicorn "$APP" --host "$HOST" --port "$PORT")
else
  RUN_CMD=(uvicorn "$APP" --host "$HOST" --port "$PORT")
fi

while true; do
  echo "[launcher] starting: ${RUN_CMD[@]} (cwd=$REPO_ROOT)"
  "${RUN_CMD[@]}"
  code=$?
  echo "[launcher] uvicorn exited with code $code; restarting in 2s..."
  sleep 2
done
