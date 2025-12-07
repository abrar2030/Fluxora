#!/bin/bash

# clean.sh: Script to clean up build and temporary files in the Fluxora project.

set -euo pipefail

echo "----------------------------------------"
echo "Starting Fluxora project cleanup..."
echo "----------------------------------------"

# --- 1. Clean Python artifacts ---
echo "Cleaning Python artifacts (.pyc files and __pycache__ directories)..."
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -delete

# --- 2. Clean temporary/build directories (from Makefile) ---
echo "Cleaning temporary and build directories..."
# The original Makefile command: rm -rf .pytest_cache/ .mlruns/ htmlcov/
rm -rf .pytest_cache/ .mlruns/ htmlcov/

# --- 3. Clean environment files (Added for completeness) ---
echo "Cleaning environment files (node_modules, venv)..."
rm -rf node_modules/ .venv/

echo "----------------------------------------"
echo "Fluxora project cleanup complete."
echo "----------------------------------------"
