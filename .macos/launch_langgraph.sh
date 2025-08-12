#!/usr/bin/env zsh
# Keep LangGraph local API server running, auto-restart on crash
cd "$(dirname "$0")"/..
export INSURER_API_BASE="${INSURER_API_BASE:-https://mock.insurer.local}"
export INSURER_API_KEY="${INSURER_API_KEY:-dev-local}"
# OPENAI_API_KEY is expected in the environment already

CMD="langgraph up -c langgraph.json --port ${PORT:-8123}"

while true; do
  echo "[launcher] starting $CMD"
  eval "$CMD"
  code=$?
  echo "[launcher] langgraph exited with code $code; restarting in 2s..."
  sleep 2
done
