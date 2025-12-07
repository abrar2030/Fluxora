#!/bin/bash

# run_tests.sh: Script to run all tests for the Fluxora project.

set -euo pipefail

echo "----------------------------------------"
echo "Starting Fluxora test suite..."
echo "----------------------------------------"

# --- 1. Check for pytest ---
if ! command -v pytest &> /dev/null; then
    echo "Warning: pytest is not installed globally. Attempting to use venv if available."
    # Assuming the setup.sh script has been run and a .venv exists
    VENV_BIN=".venv/bin/pytest"
    if [ -f "$VENV_BIN" ]; then
        PYTEST_BIN="$VENV_BIN"
    else
        echo "Error: pytest not found. Please run setup.sh first or install pytest."
        exit 1
    fi
else
    PYTEST_BIN="pytest"
fi

# --- 2. Run tests with coverage ---
echo "Running tests with coverage report..."
# The original Makefile command: pytest tests/ --cov=src --cov-report=html
"$PYTEST_BIN" tests/ --cov=src --cov-report=html || {
    echo "Error: Tests failed. Please review the output."
    exit 1
}

echo "----------------------------------------"
echo "Fluxora test suite completed successfully."
echo "Coverage report generated in htmlcov/index.html"
echo "----------------------------------------"
