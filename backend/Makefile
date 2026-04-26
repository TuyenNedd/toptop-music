.PHONY: setup lint typecheck test check

## First-time setup: install dependencies + pre-commit hooks
setup:
	uv sync
	uv run pre-commit install --config ../.pre-commit-config.yaml
	uv run pre-commit install --config ../.pre-commit-config.yaml --hook-type pre-push

## Run ruff lint + fix
lint:
	uv run ruff check . --fix

## Run mypy type check
typecheck:
	uv run mypy .

## Run pytest
test:
	uv run pytest tests/ -v

## Run all checks (same as CI)
check: lint typecheck test
