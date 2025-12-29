#!/bin/bash

# TaskRhythm Startup Script

echo "Starting TaskRhythm..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/installed.flag" ]; then
    echo "Installing dependencies..."
    pip install -r backend/requirements.txt
    touch venv/installed.flag
fi

# Start the server
echo ""
echo "Starting FastAPI server..."
echo "Access TaskRhythm at: http://localhost:8000"
echo ""
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

