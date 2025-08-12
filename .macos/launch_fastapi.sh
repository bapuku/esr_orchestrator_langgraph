#!/usr/bin/env zsh
# Keep FastAPI running via uvicorn, auto-restart on crash
export PYTHONPATH="$(cd "$(dirname "$0")"/.. && pwd)"
export INSURER_API_BASE="${INSURER_API_BASE:-https://mock.insurer.local}"
export INSURER_API_KEY="${INSURER_API_KEY:-dev-local}"
# OPENAI_API_KEY is expected in the environment already

APP="src.app:app"
HOST="0.0.0.0"
PORT="8000"

while true; do
  echo "[launcher] starting uvicorn $APP on $HOST:$PORT"
  uvicorn "$APP" --host "$HOST" --port "$PORT"
  code=$?
  echo "[launcher] uvicorn exited with code $code; restarting in 2s..."
  sleep 2
done
