#!/bin/bash

# Ensure the script stops on first error
set -e

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    python_version=$(python3 -c 'import sys; v=sys.version_info; print(f"{v.major}{v.minor}")')
    if [ "$python_version" -lt 39 ]; then
        echo "Error: Python 3.9 or higher is required (found $(python3 --version))"
        exit 1
    fi
}

# Check for required system dependencies
echo "Checking system dependencies..."

if ! command_exists python3; then
    echo "Error: Python 3 is required but not found"
    exit 1
fi

check_python_version

# Create and activate virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip and install build dependencies
echo "Installing build dependencies..."
pip install --upgrade pip
pip install build wheel setuptools_scm

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/

# Build the package
echo "Building package..."
python -m build

# Verify the build
if [ -d "dist" ] && [ "$(ls -A dist)" ]; then
    echo "Build successful! The following files were created:"
    ls -l dist/
else
    echo "Error: Build failed - no files were created in dist/"
    exit 1
fi

# Optional: Run tests if pytest is available
if command_exists pytest; then
    echo "Running tests..."
    pytest
fi

echo "
Build complete! To install the package:

1. Install from wheel file:
   pip install dist/openhands_event_tracker-*.whl

2. Or install in development mode:
   pip install -e .

To run the application:
1. Start Kafka (if not using Docker):
   docker-compose up -d kafka

2. Run the application:
   event-tracker
"