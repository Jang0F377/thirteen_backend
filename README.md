# Thirteen Backend

`thirteen-backend` is an asynchronous **FastAPI** service that powers the server-side logic for the classic Vietnamese card game _Thirteen_ (also known as Tiến Lên).  
It exposes a REST API for session management and a WebSocket API for fast, bidirectional, real-time gameplay events.

The project follows a clean, domain-driven architecture and relies on **PostgreSQL** for persistence and **Redis** for ephemeral game state & pub/sub. Everything is fully containerised with **Docker Compose** so you can be up and running in seconds.

---

## Rules of the Game

This game is a shedding-type card game, where the players try to be the first to get rid of all their cards. This game originates from Vietnam and has many different variants. I aim to support these different variant types of game modes, but the first one I will support is the one I was taught.

### Core Rules

This deals with a standard 52 card deck dealt 13 cards between 4 or 17 between 3.  
**Cards rank**(from low to high): **3 4 5 6 7 8 9 10 J Q K A 2**  
**Suits rank**(from low to high): **Diamonds Clubs Hearts Spades**  
2 of Spades being the highest single card, 3 of Diamonds being the lowest.
Players in turn discard single cards or card combinations to a central face-up discard pile.  
The object is to avoid being the last player holding any cards.

### Outplay

#### Leading

For the first hand, the player holding the 3 of Diamonds will begin. They will be 'leading' (I will also refer to as 'in control').  
They may begin by playing any valid card combination as long as the 3 of Diamonds is included.  
In subsequent hands, the winner of the previous hand begins and may play any card or combination.

#### Valid Card Plays

Valid card combinations that may be led are:

- A **single** card - 3&#9830;
- A **pair** of same rank - 4&#9830;/4&#9824;
- A **triplets** of same rank - 3&#9830;/3&#9827;/3&#9829;
- A **sequence** of 3 or more cards, regardless of suit - 9&#9827;/10&#9830;/J&#9829;/Q&#9824;
- A **bomb**(more on these below):
  - **Double sequence** of 3 or more pairs - 4&#9827;/4&#9830;/5&#9829;/5&#9824;/6&#9827;/6&#9830;
  - **Quartet** of same rank - A&#9827;/A&#9830;/A&#9829;/A&#9824;

> Sequences may not "go around the corner". So while K&#9830;/A&#9829;/2&#9824; is a valid sequence, K&#9830;/A&#9829;/2&#9824;/3&#9824; is NOT.

#### Following

Each player in turn may either play or pass.  
Passing and playing continues until theres is a card/combination that no one can beat. When the winning card/combination has been determined, that discard pile is set aside and a new pile is started for the new lead.

- To play, the player must contribute a card or combination to the pile that matches the type (single, pair, sequence, etc) of the previous played but _beats_ it in rank. The highest-ranking card of each combination determines which beats which. Thus if a sequence of 9&#9827;/10&#9830;/J&#9829; it can be beaten by 9&#9830;/10&#9827;/J&#9824; because the highest card of the second sequence (Jack of Spades) outranks the highest card of the first sequence (Jack of Hearts). Naturally it would also be beaten by any **10 J Q** or higher sequence.
- A player passes when they have no card/combination to beat the previous played in rank. Once a player passes, they may not play again to this pile and must wait until a new lead is started.

#### Bombs

The exceptions to the strict rule of _matching type_ and _beating rank_ are called **bombs**. The original rules state that **bombs** may be played "only against presently winning **2**s." But I was taught that these were free to be played against any presently winning card/combination as follows:

- **Double sequence of 3+ pairs**
  - Can beat any single card
  - Ex: 4&#9827;/4&#9830;/5&#9829;/5&#9824;/6&#9827;/6&#9830;
- **Quartet**
  - Ultimate bomb
  - Can beat anything - including double sequence
  - Can only be beat by a quartet of a higher rank.
  - Ex: 4&#9827;/4&#9830;/4&#9829;/4&#9824;

<br/>

A bomb is not unbeatable, but once played it becomes the type that must be beat rather than that of the card or combination originally led.

> This was the way I was taught, I like the fact that you must strategize as to when you want to use your bombs. You can waste them on spite or to take control of a pile to further your plans. But they do not have to be played only on **2**s.

### Ending the Game

As players play their last cards, they drop out of play. If the leader to a new pile has no cards remaining, the lead passes to the next active player to the left. The game ends when only one player is left with any cards. That player is the loser.

### Variants

To be supported at a later time...  
2-4 may play, being dealt 13 cards each; alternatively 3 players may be dealt 17 cards each.  
5-8 may play using a double deck of 104 cards. Either dealt out 13 each, or as many cards to each player as may be done equally.

---

## Table of contents

- [Thirteen Backend](#thirteen-backend)
  - [Rules of the Game](#rules-of-the-game)
    - [Core Rules](#core-rules)
    - [Outplay](#outplay)
      - [Leading](#leading)
      - [Valid Card Plays](#valid-card-plays)
      - [Following](#following)
      - [Bombs](#bombs)
    - [Ending the Game](#ending-the-game)
    - [Variants](#variants)
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
