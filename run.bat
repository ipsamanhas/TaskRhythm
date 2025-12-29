@echo off
REM TaskRhythm Startup Script for Windows

echo Starting TaskRhythm...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies if needed
if not exist "venv\installed.flag" (
    echo Installing dependencies...
    pip install -r backend\requirements.txt
    type nul > venv\installed.flag
)

REM Start the server
echo.
echo Starting FastAPI server...
echo Access TaskRhythm at: http://localhost:8000
echo.
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

