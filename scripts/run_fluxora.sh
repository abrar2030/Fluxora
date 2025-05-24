#!/bin/bash

# Start the backend API server
cd /home/ubuntu/Fluxora
python -m src.api.app &
API_PID=$!

# Wait for API to start
echo "Starting API server..."
sleep 3

# Start the frontend development server
cd /home/ubuntu/Fluxora/frontend
npm run dev &
FRONTEND_PID=$!

echo "Starting frontend development server..."
echo "API server running with PID: $API_PID"
echo "Frontend server running with PID: $FRONTEND_PID"
echo "Access the application at http://localhost:3000"

# Wait for user to press Ctrl+C
echo "Press Ctrl+C to stop the servers"
wait
