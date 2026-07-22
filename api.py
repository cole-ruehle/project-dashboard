#!/usr/bin/env python3
"""
Dashboard update API.
Exposes endpoints nginx proxies under /api/ so the dashboard
can trigger updates and poll status without any CORS issues.
"""

import json
import os
import subprocess
import threading

from fastapi import FastAPI

app = FastAPI()

WORKSPACE      = "/workspace"
DASHBOARD_JSON = os.path.join(WORKSPACE, "dashboard", "projects.json")

_lock    = threading.Lock()
_running = False


def _run_update():
    global _running
    env = {**os.environ}
    subprocess.run(["python3", os.path.join(WORKSPACE, "update.py")],
                   cwd=WORKSPACE, env=env)
    with _lock:
        _running = False


@app.get("/api/status")
def get_status():
    if os.path.isfile(DASHBOARD_JSON):
        with open(DASHBOARD_JSON) as f:
            return json.load(f)
    return []


@app.get("/api/update/running")
def is_running():
    return {"running": _running}


@app.post("/api/update")
def trigger_update():
    global _running
    with _lock:
        if _running:
            return {"ok": False, "message": "Update already in progress"}
        _running = True
    threading.Thread(target=_run_update, daemon=True).start()
    return {"ok": True, "message": "Update started"}
