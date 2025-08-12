from typing import Dict, Any
import datetime as dt

ISO_RULES = [
    {"name": "Spill recording within 24h", "weight": 0.4},
    {"name": "Training cert for hazardous handlers", "weight": 0.3},
    {"name": "Proper containment and labeling", "weight": 0.3},
]

def check_compliance(context: Dict[str, Any]) -> dict:
    """
    context: should include keys like incident_time, recorded_time, handler_cert, labeled, contained
    """
    score = 0.0
    details = []
    for rule in ISO_RULES:
        ok = False
        if rule["name"] == "Spill recording within 24h":
            it = context.get("incident_time")
            rt = context.get("recorded_time")
            try:
                it = dt.datetime.fromisoformat(it) if isinstance(it, str) else it
                rt = dt.datetime.fromisoformat(rt) if isinstance(rt, str) else rt
                ok = (rt - it).total_seconds() <= 24 * 3600
            except Exception:
                ok = False
        elif rule["name"] == "Training cert for hazardous handlers":
            ok = bool(context.get("handler_cert"))
        elif rule["name"] == "Proper containment and labeling":
            ok = bool(context.get("labeled")) and bool(context.get("contained"))
        score += rule["weight"] if ok else 0.0
        details.append({"rule": rule["name"], "ok": ok})
    return {"score": round(score, 2), "details": details}
