# Django Docker Starter

This is a basic, scalable Django starter template running in Docker.

## Stack

- Python 3.12 (stable recent release)
- Django 5.1
- Gunicorn
- PostgreSQL 16
- Docker + Docker Compose

## Quick Start

1. Copy environment file:

```bash
cp .env.example .env
```

2. Build and run:

```bash
docker compose up --build
```

3. Open:

- App: http://localhost:8000/
- Health check: http://localhost:8000/health/
- Admin: http://localhost:8000/admin/

The app container runs migrations on startup and connects to PostgreSQL through Docker Compose service discovery.

## Database Configuration

Database settings are environment driven in `.env`:

- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`

## Project Layout

```
.
├── apps/
│   └── main/
├── config/
├── docker-compose.yml
├── Dockerfile
├── manage.py
└── requirements.txt
```

## Why this is easy to scale

- App modularization under `apps/` makes feature apps easy to add.
- Environment-driven settings simplify moving between local/dev/prod.
- Gunicorn is production-ready and can scale with worker counts via `GUNICORN_WORKERS`.
- `health/` endpoint is ready for load balancer and orchestration checks.

## Next Steps

- Add Django REST Framework for API endpoints.
- Add CI checks (formatting, linting, tests).
