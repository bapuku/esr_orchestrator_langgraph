from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from typing import Dict, Any
from src.graph.state import OrchestratorState
from src.tools.knowledge_graph import KG
from src.tools.vector_store import VS
from src.tools.insurer_api import insurer_call
from src.tools.waste_tracking import get_waste_info
from src.tools.compliance_scoring import check_compliance
from src.tools.risk_detection import analyze as risk_analyze
from src.tools.report_generation import create_report
from src.tools.audit_trail import log_action
from src.utils.config import settings

# Init backends once
KG.init_from_files("data/sample_waste_data.csv", "data/regulations/ISO14001_clauses.txt")
VS.add_dir("data")

def node_plan(state: OrchestratorState) -> OrchestratorState:
    # Minimal planner: create a default plan based on keywords
    t = state.get("task","")
    steps = []
    steps.append("graph_query")
    steps.append("doc_search")
    steps.append("waste_lookup")
    steps.append("compliance_check")
    steps.append("risk_analysis")
    steps.append("insurer_lookup")
    steps.append("report_generate")
    steps.append("audit_log")
    state["plan"] = {"steps": steps, "success_criteria": ["report generated", "scores computed"]}
    return state

def node_graph_query(state: OrchestratorState) -> OrchestratorState:
    # example: try common relation from container to batch/material
    task = state.get("task","")
    container = None
    for tok in task.replace("(", " ").replace(")", " ").split():
        if tok.startswith("C-"):
            container = tok
            break
    if not container:
        # fallback: from text, assume C-456
        container = "C-456"
    res = KG.query(f"{container} -> contains_batch -> ?")
    mats = []
    for r in res.get("results", []):
        res2 = KG.query(f"{r['to']} -> contains_material -> ?")
        for m in res2.get("results", []):
            mats.append(m["to"])
    state["graph_results"] = {"container": container, "materials": mats}
    return state

def node_doc_search(state: OrchestratorState) -> OrchestratorState:
    hits = VS.search("ISO 14001 spills toxic time window")
    state["docs"] = hits
    return state

def node_waste_lookup(state: OrchestratorState) -> OrchestratorState:
    container = state.get("graph_results",{}).get("container","C-456")
    info = get_waste_info(container)
    state["waste_info"] = info
    return state

def node_compliance(state: OrchestratorState) -> OrchestratorState:
    # Minimal synthetic context for scoring
    ctx = {
        "incident_time": "2025-08-11T09:00:00",
        "recorded_time": "2025-08-11T18:00:00",
        "handler_cert": True,
        "labeled": True,
        "contained": False if "Leak" in state.get("task","") else True
    }
    comp = check_compliance(ctx)
    state["compliance"] = comp
    return state

def node_risk(state: OrchestratorState) -> OrchestratorState:
    mats = state.get("graph_results",{}).get("materials", []) or ["Unknown"]
    info = state.get("waste_info",{}).get("results", [{}])[0] if state.get("waste_info",{}).get("results") else {}
    payload = {
        "material": mats[0],
        "temperature_c": 25,
        "leak": "leak" in state.get("task","").lower(),
        "quantity_kg": info.get("quantity_kg", 0)
    }
    risk = risk_analyze(payload)
    state["risk"] = risk
    return state

async def node_insurer(state: OrchestratorState) -> OrchestratorState:
    data = await insurer_call("CLAUSE")
    state["insurer"] = data
    return state

def node_report(state: OrchestratorState) -> OrchestratorState:
    facts = {
        "incident": {
            "summary": state.get("task","N/A"),
            "container": state.get("graph_results",{}).get("container","N/A"),
            "time": "2025-08-11T18:10:00"
        },
        "materials": {
            "material": (state.get("graph_results",{}).get("materials") or ["Unknown"])[0],
            "hazard": "Toxic" if "Lead" in (state.get("graph_results",{}).get("materials") or [""])[0] else "Unknown"
        },
        "compliance": state.get("compliance", {}),
        "risk": state.get("risk", {}),
        "insurer": state.get("insurer", {})
    }
    rpt = create_report(facts)
    state["report"] = rpt
    return state

def node_audit(state: OrchestratorState) -> OrchestratorState:
    entry = {
        "event": "workflow_complete",
        "container": state.get("graph_results",{}).get("container"),
        "compliance": state.get("compliance",{}),
        "risk": state.get("risk",{}),
    }
    log_action(entry)
    state["done"] = True
    return state

def build_workflow():
    g = StateGraph(OrchestratorState)
    g.add_node("plan", node_plan)
    g.add_node("graph_query", node_graph_query)
    g.add_node("doc_search", node_doc_search)
    g.add_node("waste_lookup", node_waste_lookup)
    g.add_node("compliance_check", node_compliance)
    g.add_node("risk_analysis", node_risk)
    g.add_node("insurer_lookup", node_insurer)
    g.add_node("report_generate", node_report)
    g.add_node("audit_log", node_audit)

    g.add_edge(START, "plan")
    g.add_edge("plan", "graph_query")
    g.add_edge("graph_query", "doc_search")
    g.add_edge("doc_search", "waste_lookup")
    g.add_edge("waste_lookup", "compliance_check")
    g.add_edge("compliance_check", "risk_analysis")
    g.add_edge("risk_analysis", "insurer_lookup")
    g.add_edge("insurer_lookup", "report_generate")
    g.add_edge("report_generate", "audit_log")
    g.add_edge("audit_log", END)
    return g.compile()
