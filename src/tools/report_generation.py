from src.prompts.reporter import render_report

def create_report(facts: dict) -> dict:
    """
    facts contains: incident, materials, compliance, risk, insurer
    """
    text = render_report(facts)
    return {"report": text}
