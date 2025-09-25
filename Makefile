.PHONY: lint fmt test run type-check security-check complexity-check duplication-check profile

lint:
	ruff check . && black --check .

fmt:
	black . && ruff check --fix .

test:
	python -m pytest -q

type-check:
	mypy forgeflow tests

security-check:
	bandit -r forgeflow

complexity-check:
	radon cc forgeflow -a -s

duplication-check:
	flake8 forgeflow --select B --ignore B018,B019

profile:
	python -m cProfile -o forgeflow.prof -m forgeflow.cli --help

run:
	python -m forgeflow.cli
	sh scripts/setup-hooks.sh