.PHONY: lint fmt test run

lint:
	ruff check . && black --check .

fmt:
	black . && ruff check --fix .

test:
	python -m pytest -q

run:
	python -m forgeflow.cli
	sh scripts/setup-hooks.sh