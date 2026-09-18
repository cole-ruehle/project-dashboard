# Project Dashboard — How It Works

## Overview

This repo is a self-hosted dashboard that manages multiple independent project repos.
It clones each project, builds it via Docker Compose, and serves a status dashboard at port 8080.

## File Structure

```
project-dashboard/
├── repos.json           # Registry of all projects (source of truth)
├── setup.py             # One-time: clone + build all projects
├── update.py            # Incremental: pull + rebuild only changed projects
├── api.py               # FastAPI server; exposes /api/status and /api/update
├── docker-compose.yml   # Runs the dashboard (setup, api, nginx)
├── dashboard/
│   ├── index.html       # Frontend UI
│   ├── nginx.conf       # Serves dashboard + proxies /api/ to api container
│   └── projects.json    # Runtime status file written by setup.py / update.py
├── envs/
│   └── <name>.env       # Optional per-project env files (copied to project .env)
└── projects/
    └── <name>/          # Cloned project repos (gitignored)
```

## How the System Works

1. `docker-compose up` runs `setup` (one-shot), `api`, and `dashboard` (nginx) containers.
2. The `setup` container runs `setup.py`: clones each repo in `repos.json`, fetches shared secrets from Doppler (if `DOPPLER_TOKEN` set), merges with `envs/<name>.env` (local overrides Doppler), runs `docker-compose up -d --build` in each project dir with the configured ports.
3. The `api` container runs `api.py`: exposes `/api/status`, `/api/update`, `/api/self-update` (git pulls the dashboard repo itself, prunes Docker, rebuilds if needed), and `/api/doppler`.
4. The `dashboard` nginx container serves `dashboard/index.html` and proxies `/api/` to the api container.
5. `update.py` is the incremental version of `setup.py` — it fetches each remote, skips repos with no changes (unless previously failed), and only rebuilds what changed.
6. Projects with `build_failed`, `clone_failed`, or `run_failed` status are always retried on the next update.

## Port Conventions

- Frontend ports: 3001, 3003, 3005, 3007, 3009, 3011, 3013, ... (odd, starting at 3001)
- Backend ports:  8001, 8003, ... (odd, starting at 8001, only for projects with an API)
- DB ports:       5433, 5434, ... (only for projects with a database)

## Adding a New Project

1. **Add an entry to `repos.json`:**

```json
{
  "name": "my-project",
  "label": "My Project",
  "description": "Short description shown on the dashboard",
  "git_url": "https://github.com/cole-ruehle/my-project",
  "port": 3015,
  "backend_port": 8005,
  "color": "#hexcolor"
}
```

- `port` — frontend port (required)
- `backend_port` — only if the project has a separate API service
- `db_port` — only if the project has a database service
- Pick the next available ports following the conventions above.

2. **Secrets** — handled automatically via Doppler. All shared secrets (API keys, etc.) are fetched from Doppler and written to each project's `.env`. To override or add project-specific secrets, create `envs/my-project.env` (local always overrides Doppler).

3. **Ensure the project repo has a `docker-compose.yml`** at its root that:
   - Uses `${FRONTEND_PORT:-<default>}` for the frontend port
   - Uses `${BACKEND_PORT:-<default>}` for the backend port (if applicable)
   - Uses `${DB_PORT:-<default>}` for the db port (if applicable)
   - Uses `env_file: - .env` on any service that needs secrets (Doppler vars are in `.env` but Docker does NOT pass them into containers automatically)
   - See `docs/docker-compose-guide.md` for full details

4. **Trigger a rebuild** — either:
   - Click "Update Dashboard" then "Update All" on the dashboard
   - Or run `python3 setup.py` locally

That's it. The dashboard will show the new project card on next status poll.
