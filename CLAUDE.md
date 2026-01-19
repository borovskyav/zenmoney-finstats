# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Development Commands

Uses `uv` as the Python package manager. All commands via Makefile:

```bash
make install   # Create/sync venv (uv sync)
make fmt       # Format code (ruff format + ruff check --fix)
make lint      # Lint only (ruff check)
make type      # Type check (ty check)
make test      # Run tests (pytest)
make check     # Full quality: fmt + lint + type

make migrate   # Run DB migrations (finstats --migrate)
make generate  # Auto-generate migration (alembic revision --autogenerate)
make downgrade # Rollback one migration
```

Run single test: `uv run pytest tests/test_file.py::test_name -v`

## Architecture

**Stack:** aiohttp (async HTTP) + SQLAlchemy 2.0 (async ORM) + PostgreSQL + punq (DI)

**Key Directories:**

- `src/finstats/http/` — HTTP controllers, one per resource (accounts, tags, transactions, etc.)
- `src/finstats/store/` — Repository pattern for DB access
- `src/finstats/client/` — ZenMoney API client
- `src/finstats/container/` — DI container setup
- `src/finstats/daemons/` — Background sync daemons

**Patterns:**

- Controllers inherit `BaseController`, access repos via `self.get_*_repository()`
- All repos are async, use `ConnectionScope` for session management
- Domain models in `contracts.py` (frozen dataclasses with slots)
- HTTP schemas use `marshmallow-recipe` with `@mr.options(naming_case=mr.CAMEL_CASE)`
- OpenAPI auto-generated via `aiohttp-apigami` decorators

**CLI Entry Points:**

```bash
uv run finstats --serve          # Run HTTP server
uv run finstats --migrate        # Run migrations
uv run finstats --sync           # Sync from ZenMoney
uv run finstats --daemon sync_diff  # Background sync
```

## Code Conventions

- Python 3.14+, strict typing (`ty` with `error-on-warning = true`)
- Line length: 150 (ruff)
- All money as `decimal.Decimal`, never float
- Dataclasses: `frozen=True, slots=True`
- Async-first for all I/O
- HTTP errors: `web.HTTPBadRequest`, `web.HTTPUnauthorized`, `web.HTTPConflict`

## Transaction Types

Derived from income/outcome amounts and account types:

- `Income`: outcome == 0, income > 0
- `Expense`: income == 0, outcome > 0
- `Transfer`: income > 0, outcome > 0
- `DebtRepaid`/`LentOut`: Transfer where one account is debt type

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ZENTOKEN` | Yes (for sync) | — | ZenMoney API token |
| `POSTGRES_USER` | Yes | `test` | PostgreSQL username |
| `POSTGRES_PASSWORD` | Yes | `test` | PostgreSQL password |
| `POSTGRES_HOST` | No | `localhost` | PostgreSQL host |
| `POSTGRES_PORT` | No | `5431` | PostgreSQL port |
| `POSTGRES_DB` | No | `finstats` | PostgreSQL database name |
| `APP_PORT` | No | `8080` | HTTP server port |

## Local Development

**Docker Compose files:**

- `docker-compose.local.yml` — full local stack (db + app + sync daemon)
- `.docker/docker-compose.db.yaml` — database only (for running app outside Docker)

**Start database only:**
```bash
docker compose -f .docker/docker-compose.db.yaml up -d
```

**IDE HTTP client:**
- `.etc/requests.http` — sample API requests (uses `{{host}}` and `{{token}}` placeholders)
- Create `.etc/http-client.private.env.json` for actual values (gitignored)

## Secrets Management

**Deployment flow (Fly.io):**
```bash
# secrets.env is sourced, then envsubst renders docker-compose.fly.yml
make deploy
```

## Style Guide

### Dataclasses
- Always use `frozen=True, slots=True, kw_only=True`
- HTTP schemas: `@mr.options(naming_case=mr.CAMEL_CASE)`

### Typing
- Use `X | None` instead of `Optional[X]`
- Use `list[X]` instead of `List[X]`
- Generic parameters: `def foo[T](items: list[T]) -> T:`

### Logging
- Create logger at module level: `log = logging.getLogger(__name__)`
- Use %-formatting (lazy evaluation): `log.info("Found %d items", count)`
- Never use f-strings in log calls

### Naming
- Variables: snake_case
- Classes: PascalCase
- Never shadow builtins (list, dict, type, id, etc.)

### Imports
- Sorted by ruff (isort-compatible)
- Order: stdlib → third-party → local

## Key Modules

| Module | Purpose |
|--------|---------|
| `contracts.py` | Domain models (Account, Transaction, ZmTag, etc.) |
| `syncer.py` | ZenMoney sync orchestration |
| `http/base.py` | BaseController with DI access methods |
| `http/middleware.py` | Auth, error handling, request ID |
| `store/base.py` | SQLAlchemy ORM table definitions |
| `store/connection.py` | ConnectionScope with ContextVar for transactions |
| `store/misc.py` | Dataclass ↔ SQLAlchemy row conversion |
| `client/client.py` | ZenMoney HTTP client |
| `client/convert.py` | ZenMoney API ↔ domain model conversion |
| `container/container.py` | punq DI container wrapper |

## API Endpoints

```
GET    /health                          # Health check (no auth)
GET    /api/v1/transactions             # List with filtering
POST   /api/v1/transactions/expenses    # Create expense
POST   /api/v1/transactions/incomes     # Create income
GET    /api/v1/accounts                 # List accounts
GET    /api/v1/tags                     # List tags/categories
GET    /api/v1/merchants                # List merchants
GET    /api/v1/instruments              # List currencies
GET    /docs/openapi.json               # OpenAPI schema
```

## Authentication & Middleware

**Middleware pipeline** (applied to `/api/*`):
1. `error_middleware` — catches exceptions, returns JSON errors
2. `request_id_middleware` — adds `X-Request-ID` header
3. `auth_mw` — validates `Authorization` header against `ZENTOKEN`

**Auth notes:**
- `/health` and `/docs/*` are public (no auth required)
- Token passed directly in `Authorization` header (not `Bearer <token>`)
- All `/api/v1/*` endpoints require valid token

**Adding new endpoints:**
```python
# In http/app.py create_web_server()
web_server.router.add_view("/v1/new_resource", NewResourceController)
```

## Database & Repository Pattern

**Connection management:**
- `ConnectionScope` wraps SQLAlchemy async session with ContextVar
- Use `async with connection_scope.begin():` for transactions
- Repositories receive `ConnectionScope` via DI

**Creating a new repository:**
```python
class NewRepository:
    def __init__(self, connection_scope: ConnectionScope) -> None:
        self._connection_scope = connection_scope

    async def get_by_id(self, id: uuid.UUID) -> Model | None:
        async with self._connection_scope.begin() as session:
            result = await session.execute(select(Table).where(Table.id == id))
            row = result.scalar_one_or_none()
            return to_dataclass(row) if row else None
```

**ORM tables:** defined in `store/base.py` using SQLAlchemy 2.0 declarative style

## Common Pitfalls

- Never use `float` for money — always `decimal.Decimal`
- Always `raise` exceptions, don't just construct them
- Avoid N+1 queries — batch database operations when possible
- Don't call `datetime.date.today()` directly in business logic (hard to test)
- `from None` hides original traceback — use sparingly, log original error first
- Don't forget `async with connection_scope.begin()` — session won't auto-commit

## ZenMoney Client

**Client usage** (context manager required):
```python
async with ZenMoneyClient(token=os.environ["ZENTOKEN"]) as client:
    diff = await client.get_diff(server_timestamp=0)
```

**Key client methods:**
- `get_diff(server_timestamp)` — fetch changes since timestamp
- `push_transaction(transaction)` — create/update transaction

**Data conversion:** `client/convert.py` maps ZenMoney API responses to domain models

## Dependencies

**Lock file:** `uv.lock` pins exact versions for reproducible builds

**Key dependencies:**
| Package | Purpose |
|---------|---------|
| `aiohttp` | Async HTTP server |
| `aiohttp-apigami` | OpenAPI generation from decorators |
| `sqlalchemy` | Async ORM (2.0 style) |
| `asyncpg` | PostgreSQL async driver |
| `alembic` | Database migrations |
| `marshmallow-recipe` | Schema serialization |
| `punq` | Dependency injection container |

## Pre-commit Checklist

```bash
make check  # Runs: fmt + lint + type
make test   # Run tests
```

## Project Structure

```
├── src/finstats/
│   ├── cli.py              # Entry point, argument parsing
│   ├── contracts.py        # Domain models (dataclasses)
│   ├── syncer.py           # ZenMoney sync orchestration
│   ├── client/             # ZenMoney API client
│   │   ├── client.py       # HTTP client
│   │   ├── convert.py      # API ↔ domain conversion
│   │   └── models.py       # API response models
│   ├── container/          # DI setup
│   ├── daemons/            # Background workers
│   ├── http/               # HTTP layer
│   │   ├── app.py          # Application factory
│   │   ├── base.py         # BaseController
│   │   ├── middleware.py   # Auth, errors, request ID
│   │   └── *.py            # Resource controllers
│   └── store/              # Database layer
│       ├── base.py         # ORM table definitions
│       ├── config.py       # DB connection config
│       ├── connection.py   # ConnectionScope
│       └── *.py            # Repositories
├── alembic/                # Migrations
├── tests/
├── .docker/                # Docker configs
├── .etc/                   # IDE configs, sample requests
└── docker-compose.*.yml    # Compose files
```