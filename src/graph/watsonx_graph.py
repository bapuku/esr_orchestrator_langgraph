"""
Enhanced LangGraph workflow with watsonx.ai integration for ESR Orchestrator
This version allows switching between OpenAI and watsonx.ai LLMs
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, TypedDict, Union
from datetime import datetime

from langgraph.graph import StateGraph, END
from langchain.schema import BaseMessage
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage

from ..utils.config import settings
from ..utils.watsonx_config import create_watsonx_llm, WatsonxConfig, ESR_PROMPTS
from ..tools import (
    knowledge_graph, vector_store, insurer_api, waste_tracking,
    compliance_scoring, risk_detection, report_generation, audit_trail
)
from ..prompts.reporter import render_report
from .state import OrchestratorState

class ESROrchestrator:
    """Enhanced ESR Orchestrator with watsonx.ai support"""
    
    def __init__(self, use_watsonx: bool = False):
        """
        Initialize orchestrator with LLM choice
        
        Args:
            use_watsonx: If True, use watsonx.ai LLM; otherwise use OpenAI
        """
        self.use_watsonx = use_watsonx
        self.llm = self._initialize_llm()
        
    def _initialize_llm(self):
        """Initialize the appropriate LLM based on configuration"""
        if self.use_watsonx:
            try:
                return create_watsonx_llm()
            except Exception as e:
                print(f"Warning: watsonx.ai LLM failed to initialize: {e}")
                print("Falling back to OpenAI...")
                return ChatOpenAI(
                    model="gpt-4",
                    temperature=0.1,
                    openai_api_key=settings.openai_api_key
                )
        else:
            return ChatOpenAI(
                model="gpt-4",
                temperature=0.1,
                openai_api_key=settings.openai_api_key
            )
    
    def invoke_llm(self, prompt: str, context: Optional[Dict] = None) -> str:
        """
        Invoke LLM with appropriate prompt formatting
        
        Args:
            prompt: The prompt template or direct prompt
            context: Context variables for prompt formatting
            
        Returns:
            LLM response text
        """
        if context:
            formatted_prompt = prompt.format(**context)
        else:
            formatted_prompt = prompt
            
        if self.use_watsonx:
            # watsonx.ai LLM expects direct string input
            return self.llm.invoke(formatted_prompt)
        else:
            # OpenAI LLM expects messages
            messages = [HumanMessage(content=formatted_prompt)]
            response = self.llm.invoke(messages)
            return response.content

# Initialize global orchestrator instance
orchestrator = ESROrchestrator(use_watsonx=True)  # Set to True for watsonx.ai

async def plan_workflow(state: OrchestratorState) -> OrchestratorState:
    """Plan the workflow based on incident analysis"""
    incident_data = state["incident_data"]
    
    # Enhanced planning prompt for watsonx.ai
    planning_prompt = """
    You are an ESR (Environmental, Safety & Risk) workflow planner. 
    Analyze this incident and create an action plan.
    
    Incident: {incident}
    
    Determine which tools are needed:
    1. knowledge_graph: For regulatory compliance lookups
    2. vector_store: For similar incident searches
    3. waste_tracking: For waste material analysis
    4. compliance_scoring: For regulatory compliance assessment
    5. risk_detection: For risk level analysis
    6. insurer_api: For insurance claim processing
    7. report_generation: For final reporting
    8. audit_trail: For audit logging
    
    Respond with a JSON list of required tools in execution order.
    Example: ["knowledge_graph", "risk_detection", "compliance_scoring", "report_generation"]
    """
    
    response = orchestrator.invoke_llm(
        planning_prompt,
        {"incident": json.dumps(incident_data)}
    )
    
    try:
        # Extract JSON from response
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0].strip()
        elif "[" in response and "]" in response:
            json_str = response[response.find("["):response.rfind("]")+1]
        else:
            # Default plan if parsing fails
            json_str = '["risk_detection", "compliance_scoring", "report_generation"]'
            
        required_tools = json.loads(json_str)
    except:
        # Fallback plan
        required_tools = ["risk_detection", "compliance_scoring", "report_generation"]
    
    state["required_tools"] = required_tools
    state["current_tool"] = 0
    return state

async def knowledge_graph_query(state: OrchestratorState) -> OrchestratorState:
    """Query knowledge graph for regulations"""
    incident = state["incident_data"]
    
    # Use watsonx.ai for regulatory analysis
    if orchestrator.use_watsonx:
        regulatory_prompt = ESR_PROMPTS["compliance_analysis"].format(
            incident_data=json.dumps(incident),
            regulations="EPA, OSHA, DOT hazardous materials regulations"
        )
        analysis = orchestrator.invoke_llm(regulatory_prompt)
    else:
        # Fallback to knowledge graph tool
        analysis = knowledge_graph.find_regulations(
            incident.get("material_type", ""),
            incident.get("location", "")
        )
    
    state["regulatory_data"] = {"analysis": analysis, "timestamp": datetime.now().isoformat()}
    return state

async def vector_store_search(state: OrchestratorState) -> OrchestratorState:
    """Search for similar incidents"""
    incident = state["incident_data"]
    similar_incidents = vector_store.search_similar_incidents(
        incident.get("description", ""),
        top_k=5
    )
    state["similar_incidents"] = similar_incidents
    return state

async def waste_material_lookup(state: OrchestratorState) -> OrchestratorState:
    """Analyze waste materials"""
    incident = state["incident_data"]
    waste_analysis = waste_tracking.analyze_material(
        incident.get("material_type", ""),
        incident.get("quantity", 0)
    )
    state["waste_analysis"] = waste_analysis
    return state

async def compliance_check(state: OrchestratorState) -> OrchestratorState:
    """Perform compliance scoring with watsonx.ai enhancement"""
    incident = state["incident_data"]
    
    # Enhanced compliance check using watsonx.ai
    if orchestrator.use_watsonx and "regulatory_data" in state:
        compliance_prompt = ESR_PROMPTS["compliance_analysis"].format(
            incident_data=json.dumps(incident),
            regulations=state.get("regulatory_data", {}).get("analysis", "Standard EPA regulations")
        )
        watsonx_analysis = orchestrator.invoke_llm(compliance_prompt)
        
        # Combine with traditional scoring
        traditional_score = compliance_scoring.calculate_score(incident)
        
        compliance_result = {
            "traditional_score": traditional_score,
            "watsonx_analysis": watsonx_analysis,
            "timestamp": datetime.now().isoformat()
        }
    else:
        # Fallback to traditional method
        compliance_result = compliance_scoring.calculate_score(incident)
    
    state["compliance_score"] = compliance_result
    return state

async def risk_analysis(state: OrchestratorState) -> OrchestratorState:
    """Enhanced risk analysis with watsonx.ai"""
    incident = state["incident_data"]
    
    # Use watsonx.ai for risk assessment
    if orchestrator.use_watsonx:
        risk_prompt = ESR_PROMPTS["risk_assessment"].format(
            incident_description=incident.get("description", ""),
            material_type=incident.get("material_type", ""),
            location=incident.get("location", "")
        )
        watsonx_risk = orchestrator.invoke_llm(risk_prompt)
        
        # Combine with traditional risk detection
        traditional_risk = risk_detection.assess_risk(incident)
        
        risk_result = {
            "traditional_assessment": traditional_risk,
            "watsonx_assessment": watsonx_risk,
            "timestamp": datetime.now().isoformat()
        }
    else:
        # Fallback to traditional method
        risk_result = risk_detection.assess_risk(incident)
    
    state["risk_assessment"] = risk_result
    return state

async def insurer_lookup(state: OrchestratorState) -> OrchestratorState:
    """Process insurance claim with watsonx.ai enhancement"""
    incident = state["incident_data"]
    
    # Enhanced insurance processing
    if orchestrator.use_watsonx:
        # Generate insurance claim using watsonx.ai
        claim_prompt = ESR_PROMPTS["insurance_claim"].format(
            incident_data=json.dumps(incident),
            policy_details="Standard environmental liability policy",
            damage_assessment=json.dumps(state.get("risk_assessment", {}))
        )
        watsonx_claim = orchestrator.invoke_llm(claim_prompt)
        
        # Submit to insurer API
        insurer_response = await insurer_api.submit_claim(incident)
        
        insurance_result = {
            "watsonx_claim_analysis": watsonx_claim,
            "api_response": insurer_response,
            "timestamp": datetime.now().isoformat()
        }
    else:
        # Traditional insurance processing
        insurance_result = await insurer_api.submit_claim(incident)
    
    state["insurance_data"] = insurance_result
    return state

async def generate_report(state: OrchestratorState) -> OrchestratorState:
    """Generate comprehensive report"""
    report_data = {
        "incident": state["incident_data"],
        "compliance": state.get("compliance_score", {}),
        "risk": state.get("risk_assessment", {}),
        "insurance": state.get("insurance_data", {}),
        "regulatory": state.get("regulatory_data", {}),
        "waste": state.get("waste_analysis", {}),
        "similar_incidents": state.get("similar_incidents", [])
    }
    
    # Use report generation tool with watsonx.ai enhancement
    report = report_generation.create_comprehensive_report(
        report_data,
        use_ai_enhancement=orchestrator.use_watsonx
    )
    
    state["final_report"] = report
    return state

async def audit_logging(state: OrchestratorState) -> OrchestratorState:
    """Log audit trail"""
    audit_data = {
        "incident_id": state["incident_data"].get("id", "unknown"),
        "tools_used": state.get("required_tools", []),
        "llm_provider": "watsonx.ai" if orchestrator.use_watsonx else "openai",
        "timestamp": datetime.now().isoformat(),
        "status": "completed"
    }
    
    audit_trail.log_workflow_execution(audit_data)
    state["audit_log"] = audit_data
    return state

def should_continue(state: OrchestratorState) -> str:
    """Determine next step in workflow"""
    current_tool = state.get("current_tool", 0)
    required_tools = state.get("required_tools", [])
    
    if current_tool >= len(required_tools):
        return "audit_log"
    
    next_tool = required_tools[current_tool]
    state["current_tool"] = current_tool + 1
    
    tool_mapping = {
        "knowledge_graph": "graph_query",
        "vector_store": "doc_search", 
        "waste_tracking": "waste_lookup",
        "compliance_scoring": "compliance_check",
        "risk_detection": "risk_analysis",
        "insurer_api": "insurer_lookup",
        "report_generation": "report_generate"
    }
    
    return tool_mapping.get(next_tool, "report_generate")

def build_workflow() -> StateGraph:
    """Build the enhanced LangGraph workflow with watsonx.ai support"""
    workflow = StateGraph(OrchestratorState)
    
    # Add nodes
    workflow.add_node("plan", plan_workflow)
    workflow.add_node("graph_query", knowledge_graph_query)
    workflow.add_node("doc_search", vector_store_search)
    workflow.add_node("waste_lookup", waste_material_lookup)
    workflow.add_node("compliance_check", compliance_check)
    workflow.add_node("risk_analysis", risk_analysis)
    workflow.add_node("insurer_lookup", insurer_lookup)
    workflow.add_node("report_generate", generate_report)
    workflow.add_node("audit_log", audit_logging)
    
    # Define edges
    workflow.set_entry_point("plan")
    workflow.add_conditional_edges("plan", should_continue)
    workflow.add_conditional_edges("graph_query", should_continue)
    workflow.add_conditional_edges("doc_search", should_continue)
    workflow.add_conditional_edges("waste_lookup", should_continue)
    workflow.add_conditional_edges("compliance_check", should_continue)
    workflow.add_conditional_edges("risk_analysis", should_continue)
    workflow.add_conditional_edges("insurer_lookup", should_continue)
    workflow.add_conditional_edges("report_generate", should_continue)
    workflow.add_edge("audit_log", END)
    
    return workflow.compile()

# For backward compatibility
workflow = build_workflow()
