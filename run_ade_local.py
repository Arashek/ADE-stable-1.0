#!/usr/bin/env python
"""
ADE Platform Local Runner

This script runs the ADE platform locally, setting up both the backend and frontend
components for testing. It ensures proper Python path configuration to avoid import issues.
"""

import os
import sys
import subprocess
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ade_local_run.log')
    ]
)
logger = logging.getLogger("ade_local_runner")

def setup_environment():
    """Set up the environment for running ADE locally"""
    # Get the project root directory
    project_root = Path(__file__).parent.absolute()
    logger.info(f"Project root: {project_root}")
    
    # Add the backend directory to the Python path
    backend_dir = project_root / "backend"
    if backend_dir not in sys.path:
        sys.path.append(str(backend_dir))
        logger.info(f"Added {backend_dir} to Python path")
    
    # Create necessary directories for Docker volumes if they don't exist
    volume_dirs = [
        "D:/ADE-stable-1.0-OSLLMS/ollama_models",
        "D:/ADE-stable-1.0-OSLLMS/model_cache",
        "D:/ADE-stable-1.0-OSLLMS/redis_data",
        "D:/ADE-stable-1.0-OSLLMS/mongodb_data",
        "D:/ADE-stable-1.0-OSLLMS/prometheus_data",
        "D:/ADE-stable-1.0-OSLLMS/grafana_data"
    ]
    
    for volume_dir in volume_dirs:
        os.makedirs(volume_dir, exist_ok=True)
        logger.info(f"Ensured directory exists: {volume_dir}")
    
    return project_root

def start_backend(project_root):
    """Start the backend server"""
    logger.info("Starting backend server...")
    backend_dir = project_root / "backend"
    os.chdir(backend_dir)
    
    # Start the backend server using uvicorn
    backend_process = subprocess.Popen(
        ["python", "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        cwd=backend_dir
    )
    
    logger.info("Backend server started")
    return backend_process

def start_frontend(project_root):
    """Start the frontend development server"""
    logger.info("Starting frontend development server...")
    frontend_dir = project_root / "frontend"
    os.chdir(frontend_dir)
    
    # Start the frontend development server
    frontend_process = subprocess.Popen(
        ["npm", "start", "--", "--port", "3001"],
        cwd=frontend_dir
    )
    
    logger.info("Frontend development server started")
    return frontend_process

def main():
    """Main function to run ADE locally"""
    logger.info("Starting ADE platform locally")
    
    # Set up the environment
    project_root = setup_environment()
    
    # Start the backend server
    backend_process = start_backend(project_root)
    
    # Wait for the backend to start
    logger.info("Waiting for backend to start...")
    time.sleep(5)
    
    # Start the frontend development server
    frontend_process = start_frontend(project_root)
    
    # Keep the script running until interrupted
    try:
        logger.info("ADE platform is running locally")
        logger.info("Backend: http://localhost:8000")
        logger.info("Frontend: http://localhost:3001")
        logger.info("Press Ctrl+C to stop")
        
        # Wait for the processes to complete (which they won't unless terminated)
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        logger.info("Stopping ADE platform...")
        
        # Terminate the processes
        backend_process.terminate()
        frontend_process.terminate()
        
        logger.info("ADE platform stopped")

if __name__ == "__main__":
    main()
