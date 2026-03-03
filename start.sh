#!/bin/bash

echo "================================================"
echo "    🚀 Starting Gate.io Crypto Trading Bot    "
echo "================================================"

# Determine which python command to use
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "Error: Python is not installed or not in PATH."
    exit 1
fi

# Step 1: Check and Setup Python Environment
echo -e "\n[1/3] Setting up Python Backend Environment..."
cd backend || exit

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
fi

# Activate virtual environment (handle Windows vs Mac/Linux)
if [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "Error: Could not find virtual environment activation script."
    exit 1
fi

# Install dependencies with trusted host flags to bypass SSL issues
echo "Upgrading pip..."
pip install --upgrade pip \
    --trusted-host pypi.org \
    --trusted-host pypi.python.org \
    --trusted-host files.pythonhosted.org -q

echo "Installing dependencies..."
pip install -r requirements.txt \
    --prefer-binary \
    --trusted-host pypi.org \
    --trusted-host pypi.python.org \
    --trusted-host files.pythonhosted.org -q

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
