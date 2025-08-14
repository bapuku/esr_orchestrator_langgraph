# ESR Orchestrator - watsonx.ai Integration Guide

## 🚀 Repository Status
✅ **GitHub Repository**: https://github.com/bapuku/esr_orchestrator_langgraph  
✅ **All tests passing**: 4/4 scenarios validated  
✅ **Ready for watsonx.ai deployment**

## 🔧 watsonx.ai Integration Options

### Option 1: watsonx.ai as LLM Provider (Recommended)

Replace OpenAI with watsonx.ai models in your existing LangGraph workflow.

#### Step 1: Update Requirements
```bash
# Add to requirements.txt
ibm-watsonx-ai>=1.0.0
ibm-watson-machine-learning>=1.0.0
```

#### Step 2: Configure watsonx.ai Connection
```python
# src/utils/watsonx_config.py
from ibm_watsonx_ai import APIClient
from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
import os

# watsonx.ai configuration
WATSONX_CONFIG = {
    "url": "https://us-south.ml.cloud.ibm.com",  # Your watsonx.ai instance
    "apikey": os.getenv("WATSONX_API_KEY"),
    "project_id": os.getenv("WATSONX_PROJECT_ID")
}

def get_watsonx_client():
    """Initialize watsonx.ai client"""
    credentials = {
        "url": WATSONX_CONFIG["url"],
        "apikey": WATSONX_CONFIG["apikey"]
    }
    client = APIClient(credentials)
    client.set.default_project(WATSONX_CONFIG["project_id"])
    return client

def get_watsonx_model(model_id="ibm/granite-13b-chat-v2"):
    """Get watsonx.ai foundation model"""
    client = get_watsonx_client()
    
    parameters = {
        GenParams.DECODING_METHOD: "greedy",
        GenParams.MAX_NEW_TOKENS: 1000,
        GenParams.TEMPERATURE: 0.1,
        GenParams.TOP_P: 1.0
    }
    
    model = Model(
        model_id=model_id,
        params=parameters,
        credentials=credentials,
        project_id=WATSONX_CONFIG["project_id"]
    )
    return model
```

#### Step 3: Update Graph Configuration
```python
# src/graph/watsonx_graph.py
from langchain_ibm import WatsonxLLM
from src.utils.watsonx_config import get_watsonx_model

def create_watsonx_llm():
    """Create watsonx.ai LLM for LangGraph"""
    return WatsonxLLM(
        model_id="ibm/granite-13b-chat-v2",
        url="https://us-south.ml.cloud.ibm.com",
        apikey=os.getenv("WATSONX_API_KEY"),
        project_id=os.getenv("WATSONX_PROJECT_ID"),
        params={
            "decoding_method": "greedy",
            "max_new_tokens": 1000,
            "temperature": 0.1,
        }
    )

# Replace OpenAI LLM in your graph nodes
llm = create_watsonx_llm()
```

### Option 2: Deploy to watsonx.ai Watson Studio

#### Step 1: Create Watson Studio Project
1. Go to https://dataplatform.cloud.ibm.com
2. Create New Project → "Create an empty project"
3. Name: "ESR-Orchestrator-LangGraph"

#### Step 2: Upload Project Files
```bash
# Create deployment package
zip -r esr_orchestrator.zip \
    src/ \
    data/ \
    requirements.txt \
    README.md \
    test_scenarios.py \
    DATA_CONNECTIONS.md
```

#### Step 3: Watson Studio Notebook Integration
```python
# watson_studio_notebook.py
"""
ESR Orchestrator - Watson Studio Integration
Run this in a Watson Studio notebook
"""

# Install requirements in Watson Studio
!pip install langgraph langchain-core fastapi uvicorn pandas networkx faiss-cpu

# Import your ESR orchestrator
import sys
sys.path.append('/project_data/data_asset/')

from src.graph.graph import build_workflow
from src.tools.waste_tracking import get_waste_info

# Initialize the workflow
workflow = build_workflow()

# Test with Watson Studio
def run_esr_analysis(task_description):
    """Run ESR analysis in Watson Studio"""
    result = workflow.invoke({"task": task_description})
    return result

# Example usage
test_result = run_esr_analysis(
    "Leak in container C-456 (Lead-acid batteries). Assess compliance and prepare claim report."
)
print(test_result)
```

### Option 3: watsonx.ai Orchestration Service

#### Step 1: Create Orchestration Flow
```yaml
# watsonx_orchestration.yaml
name: "ESR-Incident-Response"
description: "Environmental, Safety & Risk incident orchestration using watsonx.ai"

flows:
  - name: "esr_analysis"
    steps:
      - name: "data_collection"
        type: "function"
        function: "collect_waste_data"
        
      - name: "compliance_check"
        type: "watsonx_model"
        model: "ibm/granite-13b-chat-v2"
        prompt: "Analyze compliance for: {incident_data}"
        
      - name: "risk_assessment"
        type: "watsonx_model"
        model: "ibm/granite-13b-instruct-v2"
        prompt: "Assess environmental risk for: {compliance_result}"
        
      - name: "report_generation"
        type: "function"
        function: "generate_incident_report"
```

### Option 4: Watson Machine Learning Deployment

#### Step 1: Model Deployment Script
```python
# deploy_to_wml.py
from ibm_watson_machine_learning import APIClient
import joblib
import json

# Package your ESR workflow as a deployable model
class ESROrchestrator:
    def __init__(self):
        self.workflow = build_workflow()
    
    def predict(self, input_data):
        task = input_data.get('task', '')
        result = self.workflow.invoke({"task": task})
        return {
            'report': result.get('report', {}),
            'compliance_score': result.get('compliance_score', 0),
            'risk_level': result.get('risk_level', 'unknown')
        }

# Save model
model = ESROrchestrator()
joblib.dump(model, 'esr_orchestrator_model.pkl')

# Deploy to Watson ML
wml_credentials = {
    "url": "https://us-south.ml.cloud.ibm.com",
    "apikey": "YOUR_WATSONX_API_KEY"
}

client = APIClient(wml_credentials)
client.set.default_space('YOUR_DEPLOYMENT_SPACE_ID')

# Create model
model_meta = {
    client.repository.ModelMetaNames.NAME: "ESR-Orchestrator",
    client.repository.ModelMetaNames.TYPE: "scikit-learn_1.3",
    client.repository.ModelMetaNames.SOFTWARE_SPEC_UID: "default_py3.10"
}

model_details = client.repository.store_model(
    model='esr_orchestrator_model.pkl',
    meta_props=model_meta
)

# Deploy model
deployment_meta = {
    client.deployments.ConfigurationMetaNames.NAME: "ESR-Orchestrator-Deployment",
    client.deployments.ConfigurationMetaNames.ONLINE: {}
}

deployment = client.deployments.create(
    artifact_uid=model_details['metadata']['id'],
    meta_props=deployment_meta
)
```

## 🔑 Environment Variables for watsonx.ai

Update your `.env` file:
```bash
# watsonx.ai Configuration
WATSONX_API_KEY=your-watsonx-api-key
WATSONX_PROJECT_ID=your-project-id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_SPACE_ID=your-deployment-space-id

# Keep existing for fallback
OPENAI_API_KEY=your-openai-key

# ESR specific
INSURER_API_BASE=https://api.insurer.example.com
INSURER_API_KEY=your-insurer-api-key
```

## 🧪 Testing with watsonx.ai

```python
# test_watsonx_integration.py
import os
from src.utils.watsonx_config import get_watsonx_model

def test_watsonx_connection():
    """Test watsonx.ai connection"""
    try:
        model = get_watsonx_model()
        
        test_prompt = """
        Analyze this environmental incident:
        Container C-456 with Lead-acid batteries has leaked at Site-A.
        Provide compliance assessment and risk level.
        """
        
        response = model.generate_text(prompt=test_prompt)
        print(f"✅ watsonx.ai Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ watsonx.ai Error: {e}")
        return False

if __name__ == "__main__":
    test_watsonx_connection()
```

## 📋 Next Steps

1. **Choose Integration Approach**:
   - Option 1: Replace LLM provider (easiest)
   - Option 2: Watson Studio deployment
   - Option 3: Orchestration service
   - Option 4: Watson ML deployment

2. **Get watsonx.ai Credentials**:
   - API Key from IBM Cloud
   - Project ID from Watson Studio
   - Deployment Space ID (if using WML)

3. **Update Configuration**:
   - Add watsonx.ai credentials to `.env`
   - Update model configuration
   - Test integration

4. **Deploy and Test**:
   - Run integration tests
   - Validate ESR scenarios
   - Monitor performance

## 🔗 Resources

- **GitHub Repository**: https://github.com/bapuku/esr_orchestrator_langgraph
- **watsonx.ai Documentation**: https://dataplatform.cloud.ibm.com/docs/content/wsj/getting-started/welcome-main.html
- **IBM Watson ML Python SDK**: https://ibm.github.io/watson-machine-learning-sdk/
- **LangChain IBM Integration**: https://python.langchain.com/docs/integrations/llms/ibm_watsonx

Your ESR orchestrator is now ready for watsonx.ai integration! 🚀🌍
