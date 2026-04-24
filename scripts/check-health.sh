#!/bin/bash

echo "Running Ruff check..."
ruff check .
ruff_status=$?

echo "Running Black check..."
black --check .
black_status=$?

echo "Running Pytest..."
pytest -q
pytest_status=$?

echo "Running MyPy type check..."
mypy --config-file mypy.ini src/forgeflow
mypy_status=$?

echo "Running Bandit security check..."
if command -v bandit >/dev/null 2>&1; then
    bandit --configfile .bandit -r src/forgeflow
    bandit_status=$?
else
    echo "bandit not installed, skipping"
    bandit_status=0
fi

echo "Running Radon complexity check..."
if command -v radon >/dev/null 2>&1; then
    radon cc src/forgeflow -a -s
    radon_status=$?
else
    echo "radon not installed, skipping"
    radon_status=0
fi

echo "Running Flake8 bug check..."
if command -v flake8 >/dev/null 2>&1; then
    flake8 src/forgeflow --select B --ignore B018,B019
    flake8_status=$?
else
    echo "flake8 not installed, skipping"
    flake8_status=0
fi

# Check if any check failed
if [ $ruff_status -ne 0 ] || [ $black_status -ne 0 ] || [ $pytest_status -ne 0 ] || [ $mypy_status -ne 0 ] || [ $bandit_status -ne 0 ] || [ $radon_status -ne 0 ] || [ $flake8_status -ne 0 ]; then
    echo "Some health checks failed!"
    exit 1
else
    echo "All health checks passed!"
fi