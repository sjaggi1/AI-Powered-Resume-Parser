@echo off
REM AI Resume Parser - Windows Startup Script

echo ========================================
echo AI Resume Parser - Startup Script
echo ========================================

REM Check Python installation
echo.
echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo.
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Create .env if it doesn't exist
if not exist ".env" (
    echo.
    echo Creating .env file...
    copy .env .env
)

REM Create necessary directories
echo.
echo Creating necessary directories...
if not exist "logs" mkdir logs
if not exist "uploads" mkdir uploads

REM Start PostgreSQL
echo.
echo Starting PostgreSQL database...
docker-compose up -d

REM Wait for database
echo Waiting for database to start...
timeout /t 5 /nobreak

REM Start the application
echo.
echo ========================================
echo Starting AI Resume Parser...
echo ========================================
echo API URL: http://localhost:8000
echo Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop
echo.

python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

pause