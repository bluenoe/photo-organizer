#!/bin/bash

# Photo Organizer - Example Run Script for Unix/Linux/macOS
# This script demonstrates how to run the photo organizer

echo "========================================"
echo "Photo Organizer - Example Usage"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python is not installed or not in PATH"
        echo "Please install Python 3.9+ and try again"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "Python is installed. Checking dependencies..."
echo

# Check if Pillow is installed
$PYTHON_CMD -c "import PIL" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required dependencies..."
    pip3 install -r requirements.txt || pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
else
    echo "Dependencies are already installed."
fi

echo
echo "========================================"
echo "Running Test Demo"
echo "========================================"
echo

# Run the test script
$PYTHON_CMD test_organizer.py

echo
echo "========================================"
echo "Example Commands"
echo "========================================"
echo
echo "To organize your own photos, use:"
echo
echo "$PYTHON_CMD photo_organizer.py --source \"/path/to/your/photos\" --destination \"/path/to/organized/photos\""
echo
echo "Replace the paths with your actual source and destination directories."
echo

# Make the script executable
chmod +x "$0" 2>/dev/null

echo "Press Enter to continue..."
read