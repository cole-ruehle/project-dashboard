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

WORKSPACE           = "/workspace"
DASHBOARD_JSON      = os.path.join(WORKSPACE, "dashboard", "projects.json")
DOPPLER_STATUS_FILE = os.path.join(WORKSPACE, "dashboard", "doppler_status.json")

_lock    = threading.Lock()
_running = False
_self_updating = False
_self_update_status = {"status": "idle"}


def _run_update():
    global _running
    env = {**os.environ}
    subprocess.run(["python3", os.path.join(WORKSPACE, "update.py")],
                   cwd=WORKSPACE, env=env)
    with _lock:
        _running = False


def _run_self_update():
    global _self_updating, _self_update_status
    try:
        _self_update_status = {"status": "pulling"}

        # Ensure git trusts the workspace directory (owned by host user, container runs as root)
        subprocess.run(["git", "config", "--global", "--add", "safe.directory", WORKSPACE],
                       capture_output=True, text=True)

        # Git pull
        result = subprocess.run(["git", "pull"], cwd=WORKSPACE, capture_output=True, text=True)
        if result.returncode != 0:
            _self_update_status = {"status": "failed", "message": f"git pull failed: {result.stderr.strip()}"}
            return

        pull_output = result.stdout.strip()
        already_up_to_date = "Already up to date" in pull_output

        # Docker prune: build cache + dangling images (not named volumes — projects use those)
        _self_update_status = {"status": "pruning"}
        subprocess.run(["docker", "builder", "prune", "-a", "-f"], capture_output=True, text=True)
        subprocess.run(["docker", "image", "prune", "-a", "-f"], capture_output=True, text=True)
        subprocess.run(["docker", "container", "prune", "-f"], capture_output=True, text=True)

        # Check if Dockerfiles changed in the pull
        needs_rebuild = False
        if not already_up_to_date:
            diff = subprocess.run(["git", "diff", "HEAD~1", "--name-only"],
                                  cwd=WORKSPACE, capture_output=True, text=True)
            changed = diff.stdout.strip().split("\n") if diff.stdout.strip() else []
            needs_rebuild = any(f.startswith("Dockerfile") or f == "docker-compose.yml" for f in changed)

        if needs_rebuild:
            _self_update_status = {"status": "rebuilding"}
            subprocess.run(["docker-compose", "up", "-d", "--build"],
                           cwd=WORKSPACE, capture_output=True, text=True)
            _self_update_status = {"status": "done", "message": "Pulled + rebuilt containers"}
        elif already_up_to_date:
            _self_update_status = {"status": "done", "message": "Already up to date (pruned Docker cache)"}
        else:
            _self_update_status = {"status": "done", "message": "Pulled latest code (no rebuild needed)"}
    except Exception as e:
        _self_update_status = {"status": "failed", "message": str(e)}
    finally:
        with _lock:
            _self_updating = False


@app.get("/api/status")
def get_status():
    if os.path.isfile(DASHBOARD_JSON):
        with open(DASHBOARD_JSON) as f:
            return json.load(f)
    return []


@app.get("/api/doppler")
def doppler_status():
    if os.path.isfile(DOPPLER_STATUS_FILE):
        with open(DOPPLER_STATUS_FILE) as f:
            return json.load(f)
    return {"ok": False, "message": "No status yet — run setup or update first"}


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


@app.post("/api/self-update")
def trigger_self_update():
    global _self_updating
    with _lock:
        if _self_updating or _running:
            return {"ok": False, "message": "An update is already in progress"}
        _self_updating = True
    threading.Thread(target=_run_self_update, daemon=True).start()
    return {"ok": True, "message": "Self-update started"}


@app.get("/api/self-update/status")
def self_update_status():
    return {**_self_update_status, "running": _self_updating}
