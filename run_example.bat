@echo off
REM Photo Organizer - Example Run Script for Windows
REM This script demonstrates how to run the photo organizer

echo ========================================
echo Photo Organizer - Example Usage
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ and try again
    pause
    exit /b 1
)

echo Python is installed. Checking dependencies...
echo.

REM Check if Pillow is installed
python -c "import PIL" >nul 2>&1
if errorlevel 1 (
    echo Installing required dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
) else (
    echo Dependencies are already installed.
)

echo.
echo ========================================
echo Running Test Demo
echo ========================================
echo.

REM Run the test script
python test_organizer.py

echo.
echo ========================================
echo Example Commands
echo ========================================
echo.
echo To organize your own photos, use:
echo.
echo python photo_organizer.py --source "C:\Path\To\Your\Photos" --destination "C:\Path\To\Organized\Photos"
echo.
echo Replace the paths with your actual source and destination directories.
echo.

pause