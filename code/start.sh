#!/bin/bash
# Fluxora Backend Startup Script

set -e

echo "========================================="
echo "Fluxora Backend Startup"
echo "========================================="

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Install dependencies if needed
if [ "$1" == "--install" ]; then
    echo "Installing dependencies..."
    pip install -q --no-input -r requirements.txt
    echo "✓ Dependencies installed"
fi

# Initialize database
echo "Initializing database..."
python -c "from backend.database import init_db; init_db(); print('✓ Database initialized')"

# Start the server
echo "Starting Fluxora API server..."
echo "Server will be available at: http://0.0.0.0:8000"
echo "API documentation: http://0.0.0.0:8000/docs"
echo "========================================="

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
