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


DOPPLER_STATUS_FILE = os.path.join(os.path.dirname(__file__), "dashboard", "doppler_status.json")


def fetch_doppler_secrets():
    """Fetch shared secrets from Doppler. Returns (secrets_dict, status_string)."""
    token = os.environ.get("DOPPLER_TOKEN", "")
    if not token:
        status = {"ok": False, "message": "DOPPLER_TOKEN not set"}
        _write_doppler_status(status)
        print("  Doppler: no token configured")
        return {}, status
    try:
        result = subprocess.run(
            ["doppler", "secrets", "download", "--no-file", "--format", "json"],
            capture_output=True, text=True,
            env={**os.environ, "DOPPLER_TOKEN": token},
        )
        if result.returncode == 0:
            secrets = json.loads(result.stdout)
            status = {"ok": True, "message": f"Loaded {len(secrets)} secrets"}
            _write_doppler_status(status)
            print(f"  Doppler: loaded {len(secrets)} secrets")
            return secrets, status
        else:
            status = {"ok": False, "message": f"CLI error: {result.stderr.strip()[:200]}"}
            _write_doppler_status(status)
            print(f"  Doppler: fetch failed — {result.stderr.strip()}")
            return {}, status
    except FileNotFoundError:
        status = {"ok": False, "message": "Doppler CLI not installed"}
        _write_doppler_status(status)
        print("  Doppler: CLI not found")
        return {}, status
    except json.JSONDecodeError:
        status = {"ok": False, "message": "Invalid JSON from Doppler CLI"}
        _write_doppler_status(status)
        print("  Doppler: bad response")
        return {}, status


def _write_doppler_status(status):
    with open(DOPPLER_STATUS_FILE, "w") as f:
        json.dump(status, f)


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

    doppler_secrets, _ = fetch_doppler_secrets()

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

        # Build project .env: Doppler (base) → local env file (override)
        env_dst = os.path.join(project_dir, ".env")
        project_env = dict(doppler_secrets)
        env_src = os.path.join(os.path.dirname(__file__), "envs", f"{name}.env")
        if os.path.isfile(env_src):
            with open(env_src) as ef:
                for line in ef:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        project_env[k.strip()] = v.strip()
            print(f"  Merged envs/{name}.env (overrides Doppler)")
        if project_env:
            with open(env_dst, "w") as ef:
                for k, v in project_env.items():
                    ef.write(f"{k}={v}\n")
            print(f"  Wrote .env ({len(project_env)} vars)")

        # Bring down any existing containers for this project
        print("  Stopping existing containers...")
        stream(["docker-compose", "down"], cwd=project_dir)

        # Build + start — ports injected as shell env (override everything)
        print(f"  Building and starting containers...")
        env = {**os.environ, **doppler_secrets, "FRONTEND_PORT": str(port)}
        if repo.get("db_port"):
            env["DB_PORT"] = str(repo["db_port"])
        if repo.get("backend_port"):
            env["BACKEND_PORT"] = str(repo["backend_port"])
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
