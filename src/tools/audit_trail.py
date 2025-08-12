import json, time
from pathlib import Path

LOG = Path("audit_log.jsonl")

def log_action(entry: dict | str) -> dict:
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    if isinstance(entry, str):
        payload = {"ts": ts, "event": entry}
    else:
        payload = {"ts": ts, **entry}
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return {"status": "ok"}
