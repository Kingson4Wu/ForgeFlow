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
mypy forgeflow tests
mypy_status=$?

echo "Running Bandit security check..."
bandit -r forgeflow
bandit_status=$?

echo "Running Radon complexity check..."
radon cc forgeflow -a -s
radon_status=$?

echo "Running Flake8 bug check..."
flake8 forgeflow --select B --ignore B018,B019
flake8_status=$?

# Check if any check failed
if [ $ruff_status -ne 0 ] || [ $black_status -ne 0 ] || [ $pytest_status -ne 0 ] || [ $mypy_status -ne 0 ] || [ $bandit_status -ne 0 ] || [ $radon_status -ne 0 ] || [ $flake8_status -ne 0 ]; then
    echo "Some health checks failed!"
    exit 1
else
    echo "All health checks passed!"
fi