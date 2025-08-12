#!/usr/bin/env zsh
# Keep LangGraph local API server running, auto-restart on crash
# Resolve repo root and ensure we run from there
REPO_ROOT="$(cd "$(dirname "$0")"/.. && pwd)"
cd "$REPO_ROOT"

# Load .env if present
if [[ -f .env ]]; then
  set -a
  source .env
  set +a
fi

export INSURER_API_BASE="${INSURER_API_BASE:-https://mock.insurer.local}"
export INSURER_API_KEY="${INSURER_API_KEY:-dev-local}"

PORT="${PORT:-8123}"
CONFIG_PATH="$REPO_ROOT/langgraph.json"

# Prefer venv langgraph if available, else fallback to PATH
PARENT_DIR="$(dirname "$REPO_ROOT")"
VENV_LG="$PARENT_DIR/.venv/bin/langgraph"
LG_BIN="${LG_BIN:-$VENV_LG}"
[[ -x "$LG_BIN" ]] || LG_BIN="langgraph"

CMD="$LG_BIN up -c $CONFIG_PATH --port $PORT"

while true; do
  echo "[launcher] starting $CMD (cwd=$REPO_ROOT)"
  eval "$CMD"
  code=$?
  echo "[launcher] langgraph exited with code $code; restarting in 2s..."
  sleep 2
done
