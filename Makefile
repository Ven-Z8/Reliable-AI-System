.PHONY: setup format lint typecheck test test-adversarial eval-smoke validate clean

setup:
	uv sync --extra dev

format:
	uv run ruff format .
	uv run ruff check --fix .

lint:
	uv run ruff format --check .
	uv run ruff check .

typecheck:
	uv run mypy src

test:
	uv run pytest -m "not adversarial and not evaluation"

test-adversarial:
	uv run pytest -m adversarial

eval-smoke:
	@echo "No model-dependent evaluation is implemented in the starter."
	@echo "Milestone 2 must replace this placeholder with an executable smoke evaluation."

validate:
	python scripts/validate_starter.py

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov dist build
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
