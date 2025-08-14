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

VENV_LG="$REPO_ROOT/.venv/bin/langgraph"
VENV_PY="$REPO_ROOT/.venv/bin/python"
if [[ -x "$VENV_LG" ]]; then
  CMD=("$VENV_LG" up -c "$CONFIG_PATH" --port "$PORT")
elif [[ -x "$VENV_PY" ]]; then
  CMD=("$VENV_PY" -m langgraph_cli up -c "$CONFIG_PATH" --port "$PORT")
else
  CMD=(langgraph up -c "$CONFIG_PATH" --port "$PORT")
fi

while true; do
  echo "[launcher] starting: ${CMD[@]} (cwd=$REPO_ROOT)"
  "${CMD[@]}"
  code=$?
  echo "[launcher] langgraph exited with code $code; restarting in 2s..."
  sleep 2
done
