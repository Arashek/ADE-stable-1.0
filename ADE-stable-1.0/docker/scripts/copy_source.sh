#!/bin/bash

# Create the target directory if it doesn't exist
mkdir -p /app/src

# Copy the source code
cp -r /source/* /app/src/

# Start the FastAPI application
exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload 