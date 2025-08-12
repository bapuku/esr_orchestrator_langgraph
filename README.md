# ESR Orchestrator (LangGraph)

Agentic orchestration for e-waste & hazardous materials: waste tracking, ISO 14001/GDPR compliance checks, risk analysis, and insurance claims documentation. Built with **LangGraph** + **LangChain**.

## Features
- LangGraph workflow with stateful planning & tool execution
- Knowledge Graph (NetworkX) + Vector store (FAISS)
- Tools: GraphQuery, DocSearch, WasteTracker, ComplianceChecker, RiskAnalyzer, InsurerAPI, ReportGenerator, AuditLogger
- FastAPI routes to run workflows
- Dockerized deployment

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# add your OPENAI_API_KEY or other LLM keys
uvicorn src.app:app --reload
```

OpenAPI docs: http://localhost:8000/docs

### Run a sample job

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"task":"Leak in container 456 (Lead-acid batteries). Assess compliance and prepare claim report."}'
```

### Build & Run with Docker

```bash
docker build -t esr-orchestrator .
docker run -p 8000:8000 --env-file .env esr-orchestrator
```

## Structure

```
.
├─ data/
│  ├─ sample_waste_data.csv
│  ├─ regulations/ISO14001_clauses.txt
│  └─ policies/internal_policy.txt
├─ src/
│  ├─ app.py
│  ├─ graph/
│  │  ├─ state.py
│  │  └─ graph.py
│  ├─ tools/
│  │  ├─ knowledge_graph.py
│  │  ├─ vector_store.py
│  │  ├─ insurer_api.py
│  │  ├─ waste_tracking.py
│  │  ├─ compliance_scoring.py
│  │  ├─ risk_detection.py
│  │  ├─ report_generation.py
│  │  └─ audit_trail.py
│  ├─ utils/config.py
│  └─ prompts/
│     ├─ planner.md
│     └─ reporter.md
├─ .env.example
├─ Dockerfile
├─ requirements.txt
└─ README.md
```
