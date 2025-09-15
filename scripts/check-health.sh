#!/bin/bash
set -e

ruff check .
black --check .
pytest -q

echo "All health checks passed!"