# Testcontainers Pytest Example

## Quick Start

```bash
# uv sync

uv run pytest -v

uv run fastapi dev
```

## Init Project

```bash
uv init --app .

uv add "fastapi[standard]" "sqlalchemy[asyncio]" asyncpg

uv add --dev pytest pytest-asyncio "testcontainers[postgres]"
uv add --dev ruff pyright

touch src/hello_testcontainers_py/main.py

# after update main.py and [tool.fastapi]
uv run fastapi dev

mkdir tests
```

* update `pyproject.toml`

```ini
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "session"
```
