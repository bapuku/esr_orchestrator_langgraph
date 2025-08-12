from pathlib import Path

def render_report(facts: dict) -> str:
    # deterministic, template-based for demo (no token usage)
    lines = []
    lines.append("# Incident Report")
    inc = facts.get("incident", {})
    lines.append(f"- **Summary**: {inc.get('summary','N/A')}")
    lines.append(f"- **Container**: {inc.get('container','N/A')}")
    lines.append(f"- **Time**: {inc.get('time','N/A')}")
    mats = facts.get("materials", {})
    lines.append(f"- **Material**: {mats.get('material','N/A')} | Hazard: {mats.get('hazard','Unknown')}")
    comp = facts.get("compliance", {})
    lines.append(f"- **Compliance Score**: {comp.get('score','?')}")
    for d in comp.get("details", []):
        lines.append(f"  - {d['rule']}: {'OK' if d['ok'] else 'MISSING'}")
    risk = facts.get("risk", {})
    lines.append(f"- **Risk**: {risk.get('risk','?')} | Notes: {', '.join(risk.get('notes',[]))}")
    ins = facts.get("insurer", {})
    clause = ins.get("clause", "N/A")
    lines.append(f"- **Insurer Clause**: {clause}")
    lines.append("\n## Recommended Actions")
    if risk.get("risk") == "High":
        lines.append("- Immediately isolate area; escalate to emergency response per ISO 14001 Clause 8.2")
    else:
        lines.append("- Monitor and document remediation steps")
    lines.append("- File required insurer forms within the specified time window")
    return "\n".join(lines)
