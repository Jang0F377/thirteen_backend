# Thirteen Backend

`thirteen-backend` is an asynchronous **FastAPI** service that powers the server-side logic for the classic Vietnamese card game _Thirteen_ (also known as Tiến Lên).  
It exposes a REST API for session management and a WebSocket API for fast, bidirectional, real-time gameplay events.

The project follows a clean, domain-driven architecture and relies on **PostgreSQL** for persistence and **Redis** for ephemeral game state & pub/sub. Everything is fully containerised with **Docker Compose** so you can be up and running in seconds.

---

## Table of contents

- [Thirteen Backend](#thirteen-backend)
  - [Table of contents](#table-of-contents)
  - [Features](#features)
  - [Tech stack](#tech-stack)
  - [Project structure](#project-structure)
  - [Quick start with Docker](#quick-start-with-docker)
  - [Environment variables](#environment-variables)
  - [Local development (without Docker)](#local-development-without-docker)
  - [Database migrations](#database-migrations)
  - [Running tests](#running-tests)
  - [Logging](#logging)
  - [Useful helper commands](#useful-helper-commands)
  - [License](#license)

---

## Features

- **FastAPI**-powered REST endpoints (`/health`, `/sessions`, …).
- **WebSocket** endpoint for real-time play (`/ws/{session_id}`).
- **Async SQLAlchemy** & **Alembic** migrations.
- **Redis** JSON storage for game state plus pub/sub fan-out.
- Modular, domain-driven architecture (Domains → Repositories → Adapters → APIs).
- 100 % typed with **mypy** compatible type-hints.
- Exhaustive unit-test suite with **pytest**.

---

## Tech stack

| Layer            | Library / Service              |
| ---------------- | ------------------------------ |
| Web framework    | FastAPI / Starlette            |
| Persistence      | PostgreSQL 17-alpine           |
| ORM / DB driver  | SQLAlchemy 2 (async) / asyncpg |
| Cache & pub/sub  | redis-stack (Redis 7 + ReJSON) |
| Background tasks | Native `async` / `await`       |
| Containerisation | Docker & Docker Compose        |
| Testing          | pytest, httpx, pytest-asyncio  |

---

## Project structure

```
├── app.py                       # FastAPI entry-point (creates application instance)
├── Dockerfile                   # Production image definition
├── docker-compose.yml           # Local dev-stack (backend + postgres + redis)
├── migrations/                  # Alembic migration scripts
│   └── versions/                #   ↳ revision files
├── thirteen_backend/            # **Python package**
│   ├── api/                     #   ↳ FastAPI routers (REST + WebSocket)
│   ├── adapters/                #   ↳ Infrastructure (database engine, etc.)
│   ├── domain/                  #   ↳ Pure business logic (cards, deck, game, …)
│   ├── repositories/            #   ↳ Data access / persistence boundary
│   ├── services/                #   ↳ Application-level services (websocket mgr.)
│   ├── utils/                   #   ↳ Helpers & formatting utilities
│   ├── config/                  #   ↳ Centralised env var loading
│   └── …
├── tests/                       # pytest suite
└── README.md
```

> The package purposefully separates the **domain** (pure, framework-agnostic Python) from IO-bound concerns (databases, web) to keep the core game logic easy to test and evolve.

---

## Quick start with Docker

The easiest way to run everything locally is via Docker Compose. _You only need **Docker Desktop** or the CLI; no local Python, Postgres or Redis installations are required._

```bash
# 1. Clone repository
$ git clone https://github.com/<your-org>/thirteen-backend.git && cd thirteen-backend

# 2. Configure environment
$ cp .env.example .env   # then edit the file and fill in real values

# 3. Build & start the stack
$ docker compose up --build
```

Compose will spin up three containers:

- `thirteen-backend` — FastAPI service (exposes `http://localhost:${APP_PORT}`)
- `thirteen-postgres` — PostgreSQL 17 with a named volume for data
- `thirteen-cache` — redis-stack instance with ReJSON module

The backend runs database migrations automatically on startup. Open the interactive API docs at:

```
http://localhost:${APP_PORT}/docs
```

(Replace `${APP_PORT}` with the value you set in `.env`, e.g. **8000**.)

To shut everything down:

```bash
docker compose down -v   # "-v" also removes named volumes
```

---

## Environment variables

All runtime configuration is performed through environment variables loaded by [python-dotenv](https://pypi.org/project/python-dotenv/). For convenience, Docker Compose reads them from a file called **.env** in the project root.

A template is provided at **.env.example** – copy/rename it to `.env` and supply real values.

| Key                   | Purpose                                                                  |
| --------------------- | ------------------------------------------------------------------------ |
| `ENV`                 | "development" or "production" – toggles FastAPI CLI mode                 |
| `APP_PORT`            | Host port to expose the FastAPI service on                               |
| `JWT_SECRET_KEY`      | Signing key for any future JWT-secured endpoints                         |
| **PostgreSQL**        |                                                                          |
| `BACKEND_DB_HOST`     | Hostname/IP of the Postgres server (inside Compose: `thirteen-postgres`) |
| `BACKEND_DB_PORT`     | Port Postgres listens on (default: **5432**)                             |
| `BACKEND_DB_NAME`     | Database name                                                            |
| `BACKEND_DB_USER`     | PostgreSQL user                                                          |
| `BACKEND_DB_PASSWORD` | User password                                                            |
| `BACKEND_DB_DIALECT`  | SQLAlchemy dialect (e.g. `postgresql`)                                   |
| `BACKEND_DB_DRIVER`   | Optional async driver (e.g. `asyncpg`)                                   |
| **Redis**             |                                                                          |
| `CACHE_URL`           | Full redis URL (e.g. `redis://:password@thirteen-cache:6379/0`)          |
| `CACHE_PASSWORD`      | Password passed to `redis-server --requirepass`                          |

---

## Local development (without Docker)

If you prefer running the service directly on your machine:

1. Install **Python 3.12** and **Poetry ≥ 1.8**.
2. `poetry install` to create a virtual environment and download deps.
3. Create a Postgres & Redis instance (or edit `.env` to point to your own).
4. Apply DB schema: `alembic upgrade head`.
5. Run the dev server:

   ```bash
   ENV=development poetry run fastapi dev app.py --port 8000 --host 0.0.0.0
   ```

Hot-reload is enabled with the `fastapi dev` command.

---

## Database migrations

The project uses **Alembic**. New migrations are generated automatically from SQLAlchemy models:

```bash
poetry run alembic revision --autogenerate -m "<description>"
poetry run alembic upgrade head
```

---

## Running tests

```bash
poetry run pytest -q
```

The `tests/` directory ships with comprehensive unit tests covering domain logic, utility helpers and the WebSocket manager.

---

## Logging

Logging is configured via [logging.conf](logging.conf) and initialised in `thirteen_backend.logger`. The `ENV` variable switches between **DEBUG** (development) and **INFO** (production) levels.

---

## Useful helper commands

```bash
# Start stack in detached mode
$ docker compose up --build -d

# View container logs
$ docker compose logs -f thirteen-backend

# Enter Postgres shell inside container
$ docker exec -it thirteen-postgres psql -U "$BACKEND_DB_USER" "$BACKEND_DB_NAME"
```

---

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
