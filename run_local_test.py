#!/usr/bin/env python
"""
Simplified Local Test Runner for ADE Platform

This script provides a simplified approach to running the ADE platform locally
for testing purposes, focusing on the agent coordination system and consensus mechanism.
"""

import os
import sys
import subprocess
import logging
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("local_test")

# Define paths
PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
TEST_DATA_DIR = BACKEND_DIR / "tests" / "test_data"

def ensure_directory_exists(directory):
    """Ensure a directory exists, creating it if necessary."""
    directory.mkdir(exist_ok=True, parents=True)
    return directory

def generate_test_data():
    """Generate test data for local testing."""
    logger.info("Generating test data for local testing")
    
    # Ensure test data directory exists
    test_data_dir = ensure_directory_exists(TEST_DATA_DIR)
    
    # Generate test conflicts
    conflicts_data = [
        {
            "attribute": "authentication.method",
            "values": {
                "security": "oauth2",
                "architecture": "jwt"
            },
            "selected_value": "oauth2",
            "selected_agent": "security",
            "confidence": 0.85
        },
        {
            "attribute": "database.encryption.enabled",
            "values": {
                "security": True,
                "performance": False
            },
            "selected_value": True,
            "selected_agent": "security",
            "confidence": 0.92
        },
        {
            "attribute": "ui.framework",
            "values": {
                "design": "react",
                "architecture": "angular"
            },
            "selected_value": "react",
            "selected_agent": "design",
            "confidence": 0.78
        }
    ]
    
    # Generate test consensus decisions
    consensus_decisions_data = [
        {
            "id": "decision_12345678",
            "key": "database_type",
            "description": "Choose database type for the application",
            "options": ["postgresql", "mongodb", "mysql"],
            "selected_option": "postgresql",
            "votes": [
                {
                    "agent": "security",
                    "agent_id": "security-1",
                    "option": "postgresql",
                    "confidence": 0.8,
                    "reasoning": "PostgreSQL has better security features"
                },
                {
                    "agent": "architecture",
                    "agent_id": "architecture-1",
                    "option": "postgresql",
                    "confidence": 0.9,
                    "reasoning": "PostgreSQL is better for complex data models"
                },
                {
                    "agent": "design",
                    "agent_id": "design-1",
                    "option": "mongodb",
                    "confidence": 0.7,
                    "reasoning": "MongoDB is more flexible for UI data"
                }
            ],
            "confidence": 0.85,
            "status": "resolved"
        },
        {
            "id": "decision_87654321",
            "key": "frontend_framework",
            "description": "Choose frontend framework for the application",
            "options": ["react", "vue", "angular"],
            "status": "in_progress",
            "votes": [
                {
                    "agent": "design",
                    "agent_id": "design-1",
                    "option": "react",
                    "confidence": 0.9,
                    "reasoning": "React has better component reusability"
                },
                {
                    "agent": "performance",
                    "agent_id": "performance-1",
                    "option": "vue",
                    "confidence": 0.75,
                    "reasoning": "Vue has better performance for this use case"
                }
            ]
        }
    ]
    
    # Save test data to files
    with open(test_data_dir / "conflicts.json", "w") as f:
        json.dump(conflicts_data, f, indent=2)
    
    with open(test_data_dir / "consensus_decisions.json", "w") as f:
        json.dump(consensus_decisions_data, f, indent=2)
    
    logger.info(f"Test data saved to {test_data_dir}")

def start_backend_server():
    """Start the backend server."""
    logger.info("Starting backend server")
    
    try:
        # Run the backend server
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
            cwd=str(PROJECT_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit to see if the server starts successfully
        try:
            stdout, stderr = process.communicate(timeout=5)
            logger.error(f"Backend server failed to start: {stderr}")
            return None
        except subprocess.TimeoutExpired:
            # This is actually good - it means the server is still running
            logger.info("Backend server started successfully")
            return process
    
    except Exception as e:
        logger.error(f"Failed to start backend server: {e}")
        return None

def start_frontend_dev_server():
    """Start the frontend development server."""
    logger.info("Starting frontend development server")
    
    try:
        # Run npm install first to ensure dependencies are installed
        logger.info("Installing frontend dependencies")
        subprocess.run(
            ["npm", "install"],
            cwd=str(FRONTEND_DIR),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Start the frontend server
        process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=str(FRONTEND_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit to see if the server starts successfully
        try:
            stdout, stderr = process.communicate(timeout=5)
            logger.error(f"Frontend server failed to start: {stderr}")
            return None
        except subprocess.TimeoutExpired:
            # This is actually good - it means the server is still running
            logger.info("Frontend development server started successfully")
            return process
    
    except Exception as e:
        logger.error(f"Failed to start frontend server: {e}")
        return None

def main():
    """Main function to run the local test setup."""
    logger.info("Starting ADE local test setup")
    
    # Generate test data
    generate_test_data()
    
    # Start backend server
    backend_process = start_backend_server()
    
    # Start frontend server
    frontend_process = start_frontend_dev_server()
    
    if backend_process or frontend_process:
        logger.info("ADE local test environment is running")
        logger.info("Press Ctrl+C to stop")
        
        try:
            # Keep the script running
            while True:
                if backend_process and backend_process.poll() is not None:
                    logger.error("Backend server stopped unexpectedly")
                    break
                
                if frontend_process and frontend_process.poll() is not None:
                    logger.error("Frontend server stopped unexpectedly")
                    break
                
                # Sleep to avoid high CPU usage
                import time
                time.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt. Shutting down...")
        
        finally:
            # Terminate processes
            if backend_process and backend_process.poll() is None:
                backend_process.terminate()
                logger.info("Backend server stopped")
            
            if frontend_process and frontend_process.poll() is None:
                frontend_process.terminate()
                logger.info("Frontend server stopped")
    
    else:
        logger.error("Failed to start ADE local test environment")

if __name__ == "__main__":
    main()
