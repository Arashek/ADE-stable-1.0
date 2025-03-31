#!/bin/bash

# Production build script for ADE Platform

# Exit on error
set -e

echo "Building ADE Platform Production Version..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install production dependencies
echo "Installing production dependencies..."
pip install -r requirements.txt

# Run production tests
echo "Running production tests..."
python -m pytest tests/

# Build production documentation
echo "Building production documentation..."
cd docs
make html
cd ..

# Create production package
echo "Creating production package..."
python setup.py sdist bdist_wheel

# Build Docker image
echo "Building Docker image..."
docker build -t ade-platform:latest -f Dockerfile.prod .

echo "Production build completed successfully!" 