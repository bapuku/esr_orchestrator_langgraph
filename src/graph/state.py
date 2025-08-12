from typing import Any, Dict, List, Optional, TypedDict

class OrchestratorState(TypedDict, total=False):
    task: str
    plan: Dict[str, Any]
    context: Dict[str, Any]
    graph_results: Dict[str, Any]
    docs: Dict[str, Any]
    waste_info: Dict[str, Any]
    compliance: Dict[str, Any]
    risk: Dict[str, Any]
    insurer: Dict[str, Any]
    report: Dict[str, Any]
    audit: List[Dict[str, Any]]
    done: bool
