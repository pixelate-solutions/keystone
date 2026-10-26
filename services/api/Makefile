.PHONY: run worker migrate test seed

run:
	uv run uvicorn app.main:app --reload

worker:
	uv run python -m app.jobs.worker

migrate:
	uv run alembic upgrade head

test:
	uv run --extra dev pytest

seed:
	uv run python -m app.scripts.seed_demo
