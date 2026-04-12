"""
app.py
======
FastAPI server exposing the BugTriageEnvironment as HTTP endpoints.
Required by OpenEnv validator which sends POST requests to /reset, /step, /state.
inference.py still runs as a background task on startup.
"""

import os
import json
import threading
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

from environment import BugTriageEnvironment, BugTriageAction

app = FastAPI(title="Bug Triage Environment", version="1.0.0")
env = BugTriageEnvironment()


# ── Request models ─────────────────────────────────────────────────────

class ResetRequest(BaseModel):
    task_index: Optional[int] = 0

class StepRequest(BaseModel):
    label:    Optional[str] = None
    severity: Optional[str] = None
    module:   Optional[str] = None


# ── Endpoints ──────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "name"       : "Bug Triage Environment",
        "version"    : "1.0.0",
        "description": "OpenEnv-compliant bug triage benchmark",
        "endpoints"  : ["/reset", "/step", "/state", "/tasks", "/health"],
        "num_tasks"  : env.num_tasks(),
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/reset")
def reset(request: ResetRequest = None):
    task_index = request.task_index if request else 0
    obs = env.reset(task_index)
    return obs.model_dump()

@app.post("/step")
def step(request: StepRequest):
    action = BugTriageAction(
        label    = request.label,
        severity = request.severity,
        module   = request.module,
    )
    obs, reward, done, info = env.step(action)
    return {
        "observation": obs.model_dump(),
        "reward"     : reward.model_dump(),
        "done"       : done,
        "info"       : info,
    }

@app.get("/state")
def state():
    return env.state().model_dump()

@app.get("/tasks")
def tasks():
    return {"tasks": env.list_tasks()}


# ── Run inference.py in background on startup ──────────────────────────

def run_inference():
    import subprocess
    subprocess.run(["python", "inference.py"], capture_output=False)

@app.on_event("startup")
def startup_event():
    thread = threading.Thread(target=run_inference, daemon=True)
    thread.start()