from fastapi import FastAPI
from pydantic import BaseModel
from src.graph.graph import build_workflow

app = FastAPI(title="ESR Orchestrator (LangGraph)")
wf = build_workflow()

class RunRequest(BaseModel):
    task: str

@app.post("/run")
async def run(req: RunRequest):
    # LangGraph supports async steps; we call ainvoke to run the compiled graph
    out = await wf.ainvoke({"task": req.task})
    return {"state": out, "report": out.get("report",{})}

@app.get("/health")
def health():
    return {"ok": True}
