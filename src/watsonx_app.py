"""
Enhanced FastAPI app with watsonx.ai integration support
Allows switching between OpenAI and watsonx.ai LLMs
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json
from datetime import datetime

from .graph.graph import build_workflow as build_openai_workflow
from .graph.watsonx_graph import build_workflow as build_watsonx_workflow

app = FastAPI(
    title="ESR Orchestrator with watsonx.ai",
    description="Environmental, Safety & Risk management with AI orchestration",
    version="2.0.0"
)

class IncidentRequest(BaseModel):
    """Request model for incident processing"""
    id: str
    description: str
    material_type: str
    location: str
    quantity: Optional[float] = 0.0
    severity: Optional[str] = "medium"
    use_watsonx: Optional[bool] = False  # New parameter to choose LLM

class WorkflowResponse(BaseModel):
    """Response model for workflow execution"""
    status: str
    incident_id: str
    llm_provider: str
    final_report: Dict[str, Any]
    compliance_score: Optional[Dict[str, Any]] = None
    risk_assessment: Optional[Dict[str, Any]] = None
    insurance_data: Optional[Dict[str, Any]] = None
    execution_time: str

# Global workflow instances
openai_workflow = None
watsonx_workflow = None

def get_workflow(use_watsonx: bool = False):
    """Get the appropriate workflow instance"""
    global openai_workflow, watsonx_workflow
    
    if use_watsonx:
        if watsonx_workflow is None:
            watsonx_workflow = build_watsonx_workflow()
        return watsonx_workflow
    else:
        if openai_workflow is None:
            openai_workflow = build_openai_workflow()
        return openai_workflow

@app.post("/run", response_model=WorkflowResponse)
async def run_esr_workflow(request: IncidentRequest):
    """
    Run the ESR workflow with choice of LLM provider
    
    Args:
        request: Incident data with optional watsonx.ai selection
        
    Returns:
        Complete workflow results with AI analysis
    """
    try:
        start_time = datetime.now()
        
        # Get appropriate workflow
        workflow = get_workflow(request.use_watsonx)
        llm_provider = "watsonx.ai" if request.use_watsonx else "openai"
        
        # Initial state
        initial_state = {
            "incident_data": {
                "id": request.id,
                "description": request.description,
                "material_type": request.material_type,
                "location": request.location,
                "quantity": request.quantity,
                "severity": request.severity,
                "timestamp": datetime.now().isoformat()
            },
            "required_tools": [],
            "current_tool": 0
        }
        
        # Execute workflow
        result = await workflow.ainvoke(initial_state)
        
        execution_time = str(datetime.now() - start_time)
        
        # Format response
        response = WorkflowResponse(
            status="completed",
            incident_id=request.id,
            llm_provider=llm_provider,
            final_report=result.get("final_report", {}),
            compliance_score=result.get("compliance_score"),
            risk_assessment=result.get("risk_assessment"),
            insurance_data=result.get("insurance_data"),
            execution_time=execution_time
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Workflow execution failed: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "features": {
            "openai": True,
            "watsonx": True,
            "langgraph": True
        }
    }

@app.get("/providers")
async def list_providers():
    """List available LLM providers and their status"""
    providers = {
        "openai": {
            "available": True,
            "status": "ready",
            "model": "gpt-4"
        },
        "watsonx": {
            "available": False,
            "status": "checking...",
            "model": "ibm/granite-13b-chat-v2"
        }
    }
    
    # Test watsonx.ai availability
    try:
        from .utils.watsonx_config import test_watsonx_integration
        providers["watsonx"]["available"] = test_watsonx_integration()
        providers["watsonx"]["status"] = "ready" if providers["watsonx"]["available"] else "configuration_needed"
    except Exception as e:
        providers["watsonx"]["status"] = f"error: {str(e)}"
    
    return providers

@app.post("/test-watsonx")
async def test_watsonx_endpoint():
    """Test watsonx.ai integration endpoint"""
    try:
        from .utils.watsonx_config import test_watsonx_integration
        success = test_watsonx_integration()
        
        if success:
            return {
                "status": "success",
                "message": "watsonx.ai integration working",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "failed",
                "message": "watsonx.ai integration failed - check configuration",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"watsonx.ai test failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)
