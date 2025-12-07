#!/bin/bash

# setup.sh: Script to set up the Fluxora project environment.

set -euo pipefail

echo "----------------------------------------"
echo "Starting Fluxora project setup..."
echo "----------------------------------------"

# --- 1. Check for Python and pip ---
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed. Please install Python 3.x."
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed. Please install pip3."
    exit 1
fi

# --- 2. Create and activate a virtual environment (Recommended) ---
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

echo "Activating virtual environment (for current shell only)..."
# Note: We don't actually activate it in this script's shell, but we use the full path to the interpreter/pip
PYTHON_BIN="$VENV_DIR/bin/python"
PIP_BIN="$VENV_DIR/bin/pip"

# Fallback if venv creation failed or for systems where venv is not the standard
if [ ! -f "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
    PIP_BIN="pip3"
    echo "Warning: Could not find venv binaries. Falling back to global python3/pip3."
fi

# --- 3. Install Python dependencies ---
echo "Installing Python dependencies from requirements.txt..."
"$PIP_BIN" install -r requirements.txt || {
    echo "Error: Failed to install Python dependencies."
    exit 1
}

# --- 4. Configure Prefect API URL (from Makefile) ---
echo "Setting Prefect API URL..."
# Assuming prefect is installed via requirements.txt
"$PYTHON_BIN" -m prefect config set PREFECT_API_URL="http://localhost:4200/api" || {
    echo "Warning: Failed to set Prefect API URL. Prefect may not be installed or configured correctly."
}

echo "----------------------------------------"
echo "Fluxora project setup complete."
echo "To use the environment, run: source $VENV_DIR/bin/activate"
echo "----------------------------------------"
