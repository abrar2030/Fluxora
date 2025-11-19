#!/bin/bash

# Fluxora Project Setup Script (Comprehensive)

# Exit immediately if a command exits with a non-zero status.
set -e

# Prerequisites (ensure these are installed and configured):
# - Kubernetes cluster (e.g., minikube, k3s, or a cloud provider's Kubernetes service)
# - Python 3.10+ (the script will use python3.11 available in the environment)
# - Docker 20.10+
# - Apache Spark 3.3+
# - make
# - dvc (Data Version Control)

echo "Starting Fluxora project setup..."

PROJECT_DIR="/home/ubuntu/projects_extracted/Fluxora"

if [ ! -d "${PROJECT_DIR}" ]; then
  echo "Error: Project directory ${PROJECT_DIR} not found."
  echo "Please ensure the project is extracted correctly."
  exit 1
fi

cd "${PROJECT_DIR}"
echo "Changed directory to $(pwd)"

# 1. Initialize environment and pull DVC data (as per README.md)
# The README specifies 'make bootstrap && dvc pull'

echo "Checking for Makefile..."
if [ ! -f "Makefile" ]; then
    echo "Error: Makefile not found in ${PROJECT_DIR}. Cannot run 'make bootstrap'."
    exit 1
fi

echo "Running 'make bootstrap' to set up the initial environment..."
make bootstrap

echo "Checking for DVC configuration (dvc.yaml or .dvc folder)..."
if [ ! -f "dvc.yaml" ] && [ ! -d ".dvc" ]; then
    echo "Warning: DVC configuration not found. Skipping 'dvc pull'. Ensure DVC is not required or manually configured."
else
    echo "Pulling data with DVC..."
    dvc pull
fi

# 2. Install Python dependencies
# Project has requirements.txt. requirements_dev.txt and pyproject.toml were found to be empty.
echo "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    echo "Found requirements.txt. Setting up Python virtual environment and installing dependencies..."
    # It's good practice to use a virtual environment
    if ! python3.11 -m venv venv_fluxora; then # Using a specific venv name
        echo "Failed to create virtual environment. Please check your Python installation."
        exit 1
    fi
    source venv_fluxora/bin/activate
    echo "Python virtual environment 'venv_fluxora' created and activated."

    echo "Installing production dependencies from requirements.txt..."
    pip3 install -r requirements.txt
    echo "Production dependencies installed."

    if [ -f "requirements_dev.txt" ]; then
        echo "Found requirements_dev.txt. Attempting to install development dependencies..."
        # This will do nothing if the file is empty, which it was in analysis.
        pip3 install -r requirements_dev.txt
        echo "Development dependencies (if any) installed."
    fi
    echo "To activate the virtual environment later, run: source ${PROJECT_DIR}/venv_fluxora/bin/activate"
    deactivate
    echo "Python virtual environment deactivated."
else
    echo "Warning: requirements.txt not found. Python dependencies may need manual installation."
fi

# 3. Reminders for other prerequisites (as per README.md)
echo ""
echo "Important Prerequisites to ensure are manually set up:"
echo "  - Kubernetes cluster (minikube supported)"
echo "  - Docker 20.10+ (ensure Docker daemon is running for any container-related tasks)"
echo "  - Apache Spark 3.3+"

echo ""
echo "Fluxora project setup script finished."
echo "Please review any warnings and ensure all prerequisites are met."
echo "Refer to the project's README.md for further instructions on running data pipelines, model training, and deployment (e.g., 'make data_pipeline', 'make train', 'make deploy_prod')."
