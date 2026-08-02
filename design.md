# Project Dashboard — System Architecture

```mermaid
graph TD
    Browser["Browser / Mobile\nhttp://host:8080"]

    subgraph compose["Docker Compose (project-dashboard)"]
        Nginx["dashboard container\nnginx :8080\nserves index.html + /repos.json\nproxies /api/ to api"]
        API["api container\nFastAPI :5000\nGET /api/status\nPOST /api/update\nGET /api/update/running"]
        Setup["setup container\none-shot: setup.py"]
    end

    Browser -->|"HTTP :8080"| Nginx
    Nginx -->|"proxy /api/"| API
    API -->|"reads"| ProjJSON["dashboard/projects.json\n(runtime status)"]
    API -->|"spawns"| UpdatePy["update.py\n(incremental rebuild)"]
    Setup -->|"writes"| ProjJSON
    Setup -->|"git clone + docker-compose up -d"| Projects

    subgraph Projects["projects/ (cloned repos)"]
        direction LR
        P1["flight-finder\nweb :3001 · api :8001 · db :5433"]
        P2["prediction-market\nweb :3003 · db :5434"]
        P3["dj-website\nweb :3005"]
        P4["personal-website\nweb :3007"]
        P5["weather-aopp\nweb :3009"]
        P6["airline-simulator\nweb :3011"]
        P7["cooking-reference\nweb :3013 · api :8003"]
    end

    Browser -->|"direct :300x"| Projects
```

## Port Map

| Service | Port |
|---|---|
| Dashboard (nginx) | 8080 |
| API (FastAPI) | 5000 |
| Flight Finder frontend | 3001 |
| Flight Finder backend | 8001 |
| Flight Finder db | 5433 |
| Prediction Market frontend | 3003 |
| Prediction Market db | 5434 |
| DJ Website | 3005 |
| Personal Website | 3007 |
| Weather App | 3009 |
| Airline Simulator | 3011 |
| Cooking Reference frontend | 3013 |
| Cooking Reference backend | 8003 |

## Data Flow

1. `docker-compose up` starts **setup** (one-shot), **api**, and **dashboard** containers.
2. **setup.py** clones each repo in `repos.json`, copies `envs/<name>.env` if present, runs `docker-compose up -d --build` in each project dir with configured ports, writes status to `dashboard/projects.json`.
3. **api.py** exposes `/api/status` (reads `projects.json`) and `/api/update` (runs `update.py` in background).
4. **nginx** serves `dashboard/index.html` + `repos.json` and proxies `/api/` to the api container.
5. **update.py** fetches each remote, skips unchanged repos, rebuilds only what changed.
