# hello-testcontainers-py

A sample of integration tests with [Testcontainers](https://testcontainers.com/) for Python, using FastAPI, SQLAlchemy (async), and PostgreSQL.

Testcontainers starts real middleware (here, PostgreSQL) in Docker during tests and removes it automatically afterwards. This README covers setup and usage only.

## Prerequisites

- Python 3.15 (pinned in `.python-version`; 3.14 also passes the tests)
- [uv](https://docs.astral.sh/uv/)
- **Docker running.** Check with `docker info`.

## Setup

```bash
uv sync --locked --all-extras --dev

# Run ./check.sh (ruff, format, pyright) automatically before each commit
uv run pre-commit install
```

`pre-commit install` writes a hook to `.git/hooks/`, so run it once in each clone.

## Running tests

```bash
./check.sh          # ruff check / ruff format --diff / pyright
uv run pytest -v
```

The first test run pulls the PostgreSQL image, which takes longer. Later runs reuse the cached image.

## Running the app

The app reads the database URL from the `DATABASE_URL` environment variable:

```
postgresql+asyncpg://user:password@host:port/dbname
```

To try it locally, start PostgreSQL and run the app:

```bash
docker run -d --name pg -e POSTGRES_PASSWORD=pw -e POSTGRES_DB=app -p 5432:5432 postgres:18-alpine

export DATABASE_URL="postgresql+asyncpg://postgres:pw@localhost:5432/app"
uv run fastapi dev
```

The app creates its tables on startup (`create_all`, which is a no-op if they already exist). For production, use a migration tool such as Alembic instead.

Then call the endpoint. Percent-encode non-ASCII characters with `--data-urlencode`; a raw non-ASCII URL is rejected by the server as an invalid HTTP request.

```bash
curl -G -X POST --data-urlencode "name=アリス" "http://127.0.0.1:8000/users"
# {"id":1,"name":"アリス"}
```

## Repository layout

```
src/hello_testcontainers_py/
  main.py      FastAPI app and endpoints
  db.py        Engine creation, session factory, get_db (dependency)
  models.py    SQLAlchemy models
tests/
  conftest.py            registers the fixture module
  fixtures/database.py   starts the container; session and test client fixtures
  test_app.py            tests
```

## CI

`.github/workflows/ci.yml` runs on pushes to `main` and on pull requests targeting `main`:

1. `./check.sh` (lint, format, type check)
2. `uv run pytest -v` on `ubuntu-latest`, which provides Docker

## Troubleshooting

- **`Cannot connect to the Docker daemon`**: Docker is not running. Start Docker Desktop or an equivalent.
- **`no such table: users` or `relation "users" does not exist`**: the tables have not been created. Start the app once (`uv run fastapi dev`) so that it creates them on startup.
- **`DATABASE_URL environment variable is not set`**: export `DATABASE_URL` before starting the app.
- **`testcontainers.postgres is deprecated`**: import from `testcontainers.community.postgres` instead (as of testcontainers 4.15.0).

## Project creation (reference)

This repository was created with:

```bash
uv init --app .

uv add "fastapi[standard]" "sqlalchemy[asyncio]" asyncpg

uv add --dev pytest pytest-asyncio "testcontainers[postgres]"
uv add --dev ruff pyright

mkdir tests
```

The pytest settings are in `[tool.pytest.ini_options]` in `pyproject.toml` (`asyncio_mode = "auto"`).
