.PHONY: lint fmt test run type-check security-check complexity-check duplication-check profile

lint:
	ruff check . && black --check .

fmt:
	black . && ruff check --fix .

test:
	python -m pytest -q

type-check:
	mypy src/forgeflow tests

security-check:
	bandit -r src/forgeflow

complexity-check:
	radon cc src/forgeflow -a -s

duplication-check:
	flake8 src/forgeflow --select B --ignore B018,B019

profile:
	python -m cProfile -o forgeflow.prof -m src.forgeflow.cli --help

run:
	python -m src.forgeflow.cli
	sh scripts/setup-hooks.sh