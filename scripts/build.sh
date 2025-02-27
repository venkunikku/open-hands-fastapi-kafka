#!/bin/bash

# Ensure the script stops on first error
set -e

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install build dependencies
pip install --upgrade pip
pip install build wheel

# Build the package
python -m build

# The wheel file will be in dist/*.whl
echo "Build complete! Check the dist/ directory for the wheel file."