.PHONY: help sync install fmt lint type test check clean deploy

PY := uv run python
RUFF := uv run ruff
TY := uv run ty
PYTEST := uv run pytest

help:
	@echo "Targets:"
	@echo "  install   - create/sync venv (uv sync)"
	@echo "  fmt       - ruff format"
	@echo "  lint      - ruff check"
	@echo "  type      - ty check"
	@echo "  test      - pytest"
	@echo "  check     - fmt + lint + type + test"
	@echo "  sync      - run finstats sync (requires ZEN_TOKEN)"
	@echo "  clean     - remove caches"

install:
	uv sync

lint:
	$(RUFF) check .

fmt:
	$(RUFF) format .
	$(RUFF) check . --fix

type:
	$(TY) check .

test:
	$(PYTEST)

check: lint fmt type

# Example runner (edit flags to your CLI)
sync:
	@[ -n "$$ZEN_TOKEN" ] || (echo "ZEN_TOKEN is required" && exit 2)
	uv run finstats sync --timestamp 0 --out data/last_diff.json

clean:
	rm -rf .ruff_cache .pytest_cache
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +

downgrade:
	uv run alembic downgrade -1

migrate:
	uv run finstats --migrate

generate:
	uv run alembic revision --autogenerate -m "init"
	
deploy:
	@set -euo pipefail; \
    set -a; . "./secrets.env"; set +a; \
    \
    envsubst < "docker-compose.fly.yml" > "docker-compose.fly.rendered.yml"; \
    \
    fly deploy