# Docker Compose Guide for Dashboard Projects

Each project's `docker-compose.yml` must follow these conventions to integrate with the dashboard.

## How it works

`update.py` reads `repos.json` and injects port values as environment variables when running `docker compose up`. Your compose file reads them via `${VAR_NAME}` syntax.

Shared secrets from Doppler are also injected automatically. They're written to a `.env` file in each project directory and passed as shell env vars to `docker compose up`. But **secrets in `.env` are not automatically available inside containers** — you must explicitly pass them through in your compose file (see [Secrets / Doppler](#secrets--doppler) below).

## Port variables

### `FRONTEND_PORT` — required

Every project must have a frontend service that uses `${FRONTEND_PORT}`. This is always injected from `repos.json` `"port"` field.

```yaml
services:
  web:
    build: .
    ports:
      - "${FRONTEND_PORT:-3000}:3000"  # left side = host port injected by dashboard
                                        # right side = whatever port your container listens on
```

The container-side port (right of the colon) must match what your app actually serves on. Common values: `3000` (Node/Vite), `80` (nginx static), `8080`.

### `BACKEND_PORT` — if project has a separate API service

Add `"backend_port"` to the project's entry in `repos.json`, then use `${BACKEND_PORT}` in compose:

```yaml
services:
  api:
    build: .
    ports:
      - "${BACKEND_PORT:-8000}:8000"
```

The frontend service should pass this to the browser so it can reach the API:

```yaml
  web:
    environment:
      - VITE_API_BASE_URL=http://localhost:${BACKEND_PORT:-8000}
```

### `DB_PORT` — if project exposes a database to the host

Add `"db_port"` to the project's entry in `repos.json`, then use `${DB_PORT}` in compose:

```yaml
services:
  db:
    image: postgres:16-alpine
    ports:
      - "${DB_PORT:-5432}:5432"
```

This is only needed if you want direct host access to the DB (e.g. for debugging). Internal service-to-service connections don't need host port exposure — they use Docker's network and the service name as hostname:

```yaml
  api:
    environment:
      - DB_HOST=db      # the db service name, no port mapping needed
      - DB_PORT=5432    # container-internal port, always 5432
```

## Secrets / Doppler

The dashboard fetches shared secrets from Doppler and writes them to each project's `.env` file. However, Docker Compose does **not** automatically pass `.env` variables into containers. You must do one of:

### Option A: `env_file` (recommended for API services)

Pass the entire `.env` into a service:

```yaml
services:
  api:
    build: .
    env_file:
      - .env    # all Doppler secrets + local overrides available inside container
    ports:
      - "${BACKEND_PORT:-8000}:8000"
```

### Option B: explicit `environment` (when you only need specific vars)

Cherry-pick individual secrets:

```yaml
services:
  api:
    build: .
    environment:
      - META_API_KEY=${META_API_KEY:-}
      - SOME_OTHER_SECRET=${SOME_OTHER_SECRET:-}
    ports:
      - "${BACKEND_PORT:-8000}:8000"
```

### Option C: build args (for frontend builds that bake values at build time)

```yaml
services:
  web:
    build:
      context: .
      args:
        VITE_API_BASE_URL: http://localhost:${BACKEND_PORT:-8000}
```

### What NOT to do

```yaml
services:
  api:
    build: .
    ports:
      - "${BACKEND_PORT:-8000}:8000"
    # No env_file or environment — secrets from Doppler are NOT available
    # inside this container even though they're in .env on the host
```

### Local overrides

If a project needs a secret that differs from Doppler (or a project-only secret), add it to `envs/<project-name>.env` in the dashboard repo. Local env files always override Doppler values.

## repos.json entry

```json
{
  "name": "my-project",
  "label": "My Project",
  "description": "...",
  "git_url": "https://github.com/you/my-project",
  "port": 3011,
  "backend_port": 8002,
  "db_port": 5435,
  "color": "#f97316"
}
```

`backend_port` and `db_port` are optional — only include them if your project has those services.

## Summary

| `repos.json` field | Env var injected   | Use in compose                        |
|--------------------|--------------------|---------------------------------------|
| `"port"`           | `FRONTEND_PORT`    | `${FRONTEND_PORT:-3000}:3000`         |
| `"backend_port"`   | `BACKEND_PORT`     | `${BACKEND_PORT:-8000}:8000`          |
| `"db_port"`        | `DB_PORT`          | `${DB_PORT:-5432}:5432`               |

## Rules

- **No host volume mounts** in any service. The code is baked into the image; path mounts won't resolve from the dashboard container.
  ```yaml
  # BAD
  volumes:
    - .:/app
  ```
- **Pick unique ports** across all projects. Check `repos.json` to avoid conflicts.
- **Backend/DB services don't need host ports** unless you specifically want direct access — they communicate internally over Docker's network.
