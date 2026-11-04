import os
import secrets
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Header, HTTPException
from .runtime import runtime
from .schemas import Intake, Report
from .engine import InvestigationFailure

@asynccontextmanager
async def lifespan(app):
    with runtime() as engine:
        app.state.engine=engine
        app.state.lock=threading.Lock()
        yield

app=FastAPI(title="Fictional Payment Investigations",version="0.2.0",lifespan=lifespan)

def analyst(authorization: str | None = Header(default=None)):
    token=os.getenv("ANALYST_API_TOKEN")
    if not token or not authorization or not secrets.compare_digest(authorization,"Bearer "+token):
        raise HTTPException(401,"Analyst authentication required")

@app.get("/health")
def health():
    return {"status":"ok","synthetic":True}

@app.post("/investigations",response_model=Report,dependencies=[Depends(analyst)])
def investigate(request: Intake):
    try:
        with app.state.lock:
            return app.state.engine.run(request)
    except InvestigationFailure as exc:
        raise HTTPException(503,{"message":"Investigation paused; inspect configuration then resume", "investigation_id":exc.investigation_id}) from None

@app.get("/investigations/{investigation_id}",response_model=Report,dependencies=[Depends(analyst)])
def report(investigation_id: str):
    with app.state.lock:
        result=app.state.engine.reports.get(investigation_id)
    if result is None: raise HTTPException(404,"Investigation not found")
    return result

@app.post("/investigations/{investigation_id}/resume",response_model=Report,dependencies=[Depends(analyst)])
def resume(investigation_id: str):
    try:
        with app.state.lock:
            return app.state.engine.resume(investigation_id)
    except KeyError:
        raise HTTPException(404,"Checkpoint not found") from None
