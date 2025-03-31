#!/bin/bash

# Development build script for ADE Platform

# Exit on error
set -e

echo "Building ADE Platform Development Version..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run tests
echo "Running tests..."
python -m pytest tests/

# Build documentation
echo "Building documentation..."
cd docs
make html
cd ..

echo "Development build completed successfully!" 