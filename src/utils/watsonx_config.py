"""
watsonx.ai Configuration for ESR Orchestrator
Update your LangGraph workflow to use watsonx.ai foundation models
"""

import os
from typing import Optional
from langchain_ibm import WatsonxLLM
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class WatsonxConfig(BaseModel):
    """watsonx.ai configuration settings"""
    api_key: Optional[str] = os.getenv("WATSONX_API_KEY")
    project_id: Optional[str] = os.getenv("WATSONX_PROJECT_ID")
    url: str = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
    model_id: str = "ibm/granite-13b-chat-v2"  # Or your preferred model
    
    # Model parameters
    max_new_tokens: int = 1000
    temperature: float = 0.1
    top_p: float = 1.0
    repetition_penalty: float = 1.0

def create_watsonx_llm(config: Optional[WatsonxConfig] = None) -> WatsonxLLM:
    """
    Create a watsonx.ai LLM instance for LangGraph
    
    Args:
        config: Optional WatsonxConfig, uses default if None
        
    Returns:
        WatsonxLLM instance configured for ESR analysis
    """
    if config is None:
        config = WatsonxConfig()
    
    if not config.api_key or not config.project_id:
        raise ValueError(
            "WATSONX_API_KEY and WATSONX_PROJECT_ID must be set in environment variables"
        )
    
    return WatsonxLLM(
        model_id=config.model_id,
        url=config.url,
        apikey=config.api_key,
        project_id=config.project_id,
        params={
            "decoding_method": "greedy",
            "max_new_tokens": config.max_new_tokens,
            "temperature": config.temperature,
            "top_p": config.top_p,
            "repetition_penalty": config.repetition_penalty,
        }
    )

# ESR-specific prompt templates for watsonx.ai
ESR_PROMPTS = {
    "compliance_analysis": """
You are an environmental compliance expert. Analyze the following incident data and provide:
1. Compliance score (0-1)
2. Regulatory violations identified
3. Required corrective actions

Incident Data: {incident_data}
Regulations: {regulations}

Response format:
- Compliance Score: [0.0-1.0]
- Violations: [list violations]
- Actions: [required actions]
""",
    
    "risk_assessment": """
You are a risk assessment specialist for environmental incidents. Evaluate:
1. Environmental impact severity
2. Health and safety risks
3. Risk level (Low/Medium/High/Critical)

Incident: {incident_description}
Material: {material_type}
Location: {location}

Provide structured risk assessment with specific recommendations.
""",
    
    "insurance_claim": """
You are an insurance claim specialist for environmental incidents. Generate:
1. Claim summary
2. Required documentation
3. Estimated coverage assessment

Incident: {incident_data}
Policy: {policy_details}
Damages: {damage_assessment}

Format as professional insurance claim documentation.
"""
}

# Example usage function
def test_watsonx_integration():
    """Test watsonx.ai integration with sample ESR data"""
    try:
        # Create watsonx LLM
        llm = create_watsonx_llm()
        
        # Test prompt
        test_prompt = ESR_PROMPTS["risk_assessment"].format(
            incident_description="Lead-acid battery leak in container C-456",
            material_type="Lead-acid batteries (toxic)",
            location="Site-A industrial facility"
        )
        
        # Generate response
        response = llm.invoke(test_prompt)
        print(f"✅ watsonx.ai Integration Success!")
        print(f"📝 Response: {response[:200]}...")
        return True
        
    except Exception as e:
        print(f"❌ watsonx.ai Integration Failed: {e}")
        return False

if __name__ == "__main__":
    test_watsonx_integration()
