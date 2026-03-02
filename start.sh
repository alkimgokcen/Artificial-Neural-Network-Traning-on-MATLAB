#!/bin/bash

echo "================================================"
echo "    🚀 Starting Gate.io Crypto Trading Bot    "
echo "================================================"

# Step 1: Check and Setup Python Environment
echo -e "\n[1/3] Setting up Python Backend Environment..."
cd backend || exit

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies (quietly to reduce noise)
echo "Installing dependencies..."
pip install -r requirements.txt -q

# Step 2: Start the FastAPI Backend Server
echo -e "\n[2/3] Starting Backend Server on port 8000..."
# Kill any existing process on port 8000 to prevent errors
kill $(lsof -t -i :8000) 2>/dev/null || true

# Run uvicorn in the background and log output
nohup python -m uvicorn main:app --reload > server.log 2>&1 &
BACKEND_PID=$!
echo "Backend started successfully (PID: $BACKEND_PID)"

# Step 3: Start the Frontend UI Server
echo -e "\n[3/3] Starting Frontend UI on port 3000..."
cd ../frontend || exit
# Kill any existing process on port 3000
kill $(lsof -t -i :3000) 2>/dev/null || true

# Run a simple Python HTTP server in the background
nohup python -m http.server 3000 > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend started successfully (PID: $FRONTEND_PID)"

echo "================================================"
echo "✅ All services are up and running!"
echo "👉 Open your browser and go to: http://localhost:3000"
echo "================================================"

# Trap Ctrl+C to stop both servers cleanly
trap "echo -e '\nStopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM

echo "Press Ctrl+C to stop the bot."

# Wait indefinitely to keep the script running
wait
