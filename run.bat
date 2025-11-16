@echo off
REM SRE Tier-0 Monitoring Dashboard - Run Script (Windows)

echo ===================================
echo SRE Tier-0 Monitoring Dashboard
echo ===================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies if needed
if not exist "venv\dependencies_installed" (
    echo Installing dependencies...
    pip install -r requirements.txt
    type nul > venv\dependencies_installed
)

REM Create necessary directories
if not exist "data\logs" mkdir data\logs
if not exist "data\devices" mkdir data\devices
if not exist "images" mkdir images
if not exist "templates" mkdir templates

REM Check for .env file
if not exist ".env" (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo WARNING: Please edit .env file to add your Cohere API key (optional)
)

echo.
echo Starting application...
echo Dashboard will be available at: http://localhost:8000
echo Login credentials: admin / secret
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run the application
python backend\main.py

pause
