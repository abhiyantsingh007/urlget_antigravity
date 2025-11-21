@echo off
echo ACME API Data Capture
echo ====================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher and add it to your PATH
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking required packages...
pip show selenium >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required packages...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Error installing requirements
        pause
        exit /b 1
    )
)

pip show webdriver-manager >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing webdriver-manager...
    pip install webdriver-manager
    if %errorlevel% neq 0 (
        echo Error installing webdriver-manager
        pause
        exit /b 1
    )
)

REM Run the capture script
echo Starting data capture...
python simple_api_capture.py

echo.
echo Capture completed. Press any key to exit.
pause >nul