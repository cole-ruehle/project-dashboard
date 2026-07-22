#!/usr/bin/env python3
"""
Project Dashboard Updater
Checks each repo for new commits. Only rebuilds projects that have changed.
The main dashboard nginx stays up the entire time.

Usage: python3 update.py
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


def load_statuses():
    if os.path.isfile(DASHBOARD_JSON):
        with open(DASHBOARD_JSON) as f:
            return {s["name"]: s for s in json.load(f)}
    return {}


def write_statuses(statuses_map):
    with open(DASHBOARD_JSON, "w") as f:
        json.dump(list(statuses_map.values()), f, indent=2)


def has_remote_changes(project_dir, auth_url):
    """Returns True if remote has commits not yet in local HEAD."""
    run(["git", "remote", "set-url", "origin", auth_url], cwd=project_dir)
    if run(["git", "fetch", "origin"], cwd=project_dir).returncode != 0:
        return False
    local  = run(["git", "rev-parse", "HEAD"],        cwd=project_dir).stdout.strip()
    remote = run(["git", "rev-parse", "FETCH_HEAD"],  cwd=project_dir).stdout.strip()
    return local != remote


def main():
    with open(REPOS_FILE) as f:
        repos = json.load(f)

    os.makedirs(PROJECTS_DIR, exist_ok=True)

    token    = os.environ.get("GITHUB_TOKEN", "")
    statuses = load_statuses()

    for repo in repos:
        name        = repo["name"]
        git_url     = repo["git_url"]
        port        = repo["port"]
        project_dir = os.path.join(PROJECTS_DIR, name)

        print(f"\n[{name}]")

        auth_url = git_url
        if token and git_url.startswith("https://github.com/"):
            auth_url = git_url.replace("https://", f"https://{token}@")

        # Clone if missing
        if not os.path.exists(os.path.join(project_dir, ".git")):
            print(f"  Not cloned — cloning {git_url}...")
            result = run(["git", "clone", auth_url, project_dir])
            if result.returncode != 0:
                print(f"  ERROR: {result.stderr.strip()}")
                statuses[name] = {**repo, "status": "clone_failed"}
                write_statuses(statuses)
                continue
            needs_build = True
        else:
            print("  Checking for remote changes...")
            needs_build = has_remote_changes(project_dir, auth_url)
            if needs_build:
                print("  Changes detected — rebuilding")
            else:
                print("  Up to date — skipping")
                continue

        compose_file = find_compose(project_dir)
        if not compose_file:
            print("  No docker-compose.yml — skipping")
            statuses[name] = {**repo, "status": "no_compose_file"}
            write_statuses(statuses)
            continue

        # Mark as updating so dashboard shows it live
        statuses[name] = {**repo, "status": "updating"}
        write_statuses(statuses)

        # Pull
        print("  Pulling latest...")
        result = run(["git", "pull"], cwd=project_dir)
        if result.returncode != 0:
            print(f"  ERROR: {result.stderr.strip()}")
            statuses[name] = {**repo, "status": "clone_failed"}
            write_statuses(statuses)
            continue

        # Copy env
        env_src = os.path.join(os.path.dirname(__file__), "envs", f"{name}.env")
        if os.path.isfile(env_src):
            shutil.copy(env_src, os.path.join(project_dir, ".env"))
            print(f"  Copied envs/{name}.env → .env")

        # Bring down existing containers for this project only
        print("  Stopping existing containers...")
        stream(["docker", "compose", "down"], cwd=project_dir)

        # Build + start
        print("  Building and starting...")
        env = {**os.environ, "FRONTEND_PORT": str(port)}
        if repo.get("db_port"):
            env["DB_PORT"] = str(repo["db_port"])
        returncode = stream(["docker", "compose", "up", "-d", "--build"], cwd=project_dir, env=env)

        if returncode != 0:
            print("  Failed — see output above")
            statuses[name] = {**repo, "status": "build_failed"}
        else:
            print(f"  Running at http://localhost:{port}")
            statuses[name] = {**repo, "status": "running"}
        write_statuses(statuses)

    print("\nUpdate complete.")


if __name__ == "__main__":
    main()
