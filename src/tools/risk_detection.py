def analyze(payload: dict) -> dict:
    """
    Simple heuristic risk analyzer
    payload: {material, temperature_c, leak:bool, quantity_kg:int}
    """
    risk = "Low"
    notes = []
    if payload.get("leak"):
        risk = "Medium"
        notes.append("Leak detected")
    if payload.get("temperature_c", 20) > 45:
        risk = "High"
        notes.append("High temperature")
    if payload.get("material","").lower().find("lead") >= 0 and payload.get("leak"):
        risk = "High"
        notes.append("Toxic material leak")
    return {"risk": risk, "notes": notes}
