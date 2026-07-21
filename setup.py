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

REPOS_FILE     = os.path.join(os.path.dirname(__file__), "repos.json")
PROJECTS_DIR   = os.path.join(os.path.dirname(__file__), "projects")
DASHBOARD_JSON = os.path.join(os.path.dirname(__file__), "dashboard", "projects.json")

COMPOSE_NAMES  = ["docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"]


def run(cmd, cwd=None, env=None):
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)


def stream(cmd, cwd=None, env=None):
    """Run a command and stream output live, returns exit code."""
    proc = subprocess.Popen(cmd, cwd=cwd, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, bufsize=1)
    for line in proc.stdout:
        print(f"    {line}", end="", flush=True)
    proc.wait()
    return proc.returncode


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

        # Build authenticated URL if token is available
        token = os.environ.get("GITHUB_TOKEN", "")
        if token and git_url.startswith("https://github.com/"):
            auth_url = git_url.replace("https://", f"https://{token}@")
        else:
            auth_url = git_url

        # Clone or pull
        if os.path.exists(os.path.join(project_dir, ".git")):
            print("  Pulling latest...")
            result = run(["git", "remote", "set-url", "origin", auth_url], cwd=project_dir)
            result = run(["git", "pull"], cwd=project_dir)
        else:
            print(f"  Cloning {git_url}...")
            result = run(["git", "clone", auth_url, project_dir])

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

        # Copy project-specific .env if provided
        env_src = os.path.join(os.path.dirname(__file__), "envs", f"{name}.env")
        env_dst = os.path.join(project_dir, ".env")
        if os.path.isfile(env_src):
            shutil.copy(env_src, env_dst)
            print(f"  Copied envs/{name}.env → .env")

        # Bring down any existing containers for this project
        print("  Stopping existing containers...")
        stream(["docker-compose", "down"], cwd=project_dir)

        # Build + start
        print(f"  Building and starting containers...")
        env = {**os.environ, "FRONTEND_PORT": str(port)}
        if repo.get("db_port"):
            env["DB_PORT"] = str(repo["db_port"])
        returncode = stream(["docker-compose", "up", "-d", "--build"], cwd=project_dir, env=env)
        if returncode != 0:
            print(f"  Failed — see output above")
            statuses.append({**repo, "status": "build_failed"})
        else:
            print(f"  Running at http://localhost:{port}")
            statuses.append({**repo, "status": "running"})

    # Write status file for dashboard
    with open(DASHBOARD_JSON, "w") as f:
        json.dump(statuses, f, indent=2)
    print(f"\nWrote {DASHBOARD_JSON}")

    print("\nSetup complete. Dashboard will be available at http://localhost:8080")


if __name__ == "__main__":
    main()
