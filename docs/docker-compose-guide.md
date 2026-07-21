# Docker Compose Guide for Dashboard Projects

Each project's `docker-compose.yml` must follow these conventions to work with the dashboard setup.

## Required: Frontend port

The frontend service must use `${FRONTEND_PORT}` for its host port mapping. The dashboard injects this from `repos.json`.

```yaml
web:
  ports:
    - "${FRONTEND_PORT:-3000}:3000"  # host:container — container always listens on 3000
```

## Optional: Database port

If your project exposes a database to the host (for direct access/debugging), use `${DB_PORT}`.

```yaml
db:
  ports:
    - "${DB_PORT:-5432}:5432"
```

Each project gets a unique `db_port` in `repos.json` to avoid conflicts.

## Do not use host volume mounts in services

Avoid `volumes: - .:/app` in any service. The code is already baked into the image and this path won't resolve when run via the dashboard setup container.

```yaml
# BAD
api:
  volumes:
    - .:/app

# GOOD — just remove it, the Dockerfile handles copying code
api:
  build: .
```

## Backend services stay internal

Backend services (APIs, databases, workers) do not need host port exposure unless you want direct access. They communicate internally via Docker's network using the service name as hostname.

```yaml
api:
  environment:
    - DB_HOST=db  # refers to the db service by name, no port mapping needed
```

## Summary

| Variable | Set in repos.json | Used in compose |
|---|---|---|
| `FRONTEND_PORT` | `"port"` | `${FRONTEND_PORT:-3000}:3000` |
| `DB_PORT` | `"db_port"` | `${DB_PORT:-5432}:5432` |
