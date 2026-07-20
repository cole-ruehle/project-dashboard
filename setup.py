#!/usr/bin/env python3
"""
Project Dashboard Setup
Clones/pulls each repo in repos.json, checks for a docker-compose file,
runs `docker compose up -d --build`, then starts the dashboard.

Usage: python3 setup.py
"""

import json
import os
import shutil
import subprocess
import sys

REPOS_FILE     = os.path.join(os.path.dirname(__file__), "repos.json")
PROJECTS_DIR   = os.path.join(os.path.dirname(__file__), "projects")
DASHBOARD_JSON = os.path.join(os.path.dirname(__file__), "dashboard", "projects.json")

COMPOSE_NAMES  = ["docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"]


def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def find_compose(project_dir):
    for name in COMPOSE_NAMES:
        if os.path.isfile(os.path.join(project_dir, name)):
            return name
    return None


def main():
    with open(REPOS_FILE) as f:
        repos = json.load(f)

    os.makedirs(PROJECTS_DIR, exist_ok=True)

    # Copy repos.json into dashboard so nginx can serve it
    shutil.copy(REPOS_FILE, os.path.join(os.path.dirname(__file__), "dashboard", "repos.json"))

    statuses = []

    for repo in repos:
        name    = repo["name"]
        git_url = repo["git_url"]
        port    = repo["port"]
        project_dir = os.path.join(PROJECTS_DIR, name)

        print(f"\n[{name}]")

        # Clone or pull
        if os.path.isdir(os.path.join(project_dir, ".git")):
            print("  Pulling latest...")
            result = run(["git", "pull"], cwd=project_dir)
        else:
            print(f"  Cloning {git_url}...")
            result = run(["git", "clone", git_url, project_dir])

        if result.returncode != 0:
            print(f"  ERROR: {result.stderr.strip()}")
            statuses.append({**repo, "status": "clone_failed", "error": result.stderr.strip()})
            continue

        # Check for compose file
        compose_file = find_compose(project_dir)
        if not compose_file:
            print("  No docker-compose.yml found — skipping")
            statuses.append({**repo, "status": "no_compose_file"})
            continue

        print(f"  Found {compose_file}")

        # Bring down any existing containers for this project
        run(["docker", "compose", "down"], cwd=project_dir)

        # Build + start
        print(f"  Running docker compose up --build ...")
        result = run(["docker", "compose", "up", "-d", "--build"], cwd=project_dir)
        if result.returncode != 0:
            print(f"  Failed:\n{result.stderr.strip()}")
            statuses.append({**repo, "status": "build_failed", "error": result.stderr.strip()})
        else:
            print(f"  Running at http://localhost:{port}")
            statuses.append({**repo, "status": "running"})

    # Write status file for dashboard
    with open(DASHBOARD_JSON, "w") as f:
        json.dump(statuses, f, indent=2)
    print(f"\nWrote {DASHBOARD_JSON}")

    # Start dashboard container
    print("\nStarting dashboard...")
    result = run(["docker", "compose", "up", "-d", "dashboard"],
                 cwd=os.path.dirname(__file__))
    if result.returncode == 0:
        print("Dashboard running at http://localhost:8080")
    else:
        print(f"Dashboard failed to start:\n{result.stderr.strip()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
