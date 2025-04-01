#!/usr/bin/env python
"""
ADE Platform Local Development Starter

This script helps set up and run the ADE platform locally by:
1. Fixing common issues in the codebase
2. Starting the backend server
3. Starting the frontend development server
"""

import os
import sys
import subprocess
import time
import logging
from pathlib import Path
import shutil
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("local_dev_starter")

class LocalDevStarter:
    """Helper class to start local development of ADE platform"""
    
    def __init__(self):
        """Initialize the local development starter"""
        self.project_root = Path(__file__).parent.parent
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.backend_process = None
        self.frontend_process = None
    
    def print_header(self, title):
        """Print a formatted header"""
        logger.info("\n" + "=" * 80)
        logger.info(f" {title} ".center(80, "="))
        logger.info("=" * 80)
    
    def run_command(self, command, cwd=None, capture_output=True):
        """Run a shell command and return the result"""
        logger.info(f"Running: {command}")
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or self.project_root,
                capture_output=capture_output,
                text=True
            )
            if capture_output:
                if result.stdout:
                    logger.debug(f"STDOUT: {result.stdout}")
                if result.stderr:
                    logger.debug(f"STDERR: {result.stderr}")
            return result
        except Exception as e:
            logger.error(f"Error running command: {str(e)}")
            return None
    
    def fix_init_files(self):
        """Ensure __init__.py files exist in all directories"""
        self.print_header("FIXING __init__.py FILES")
        
        # Walk through all directories in backend
        for root, dirs, files in os.walk(self.backend_dir):
            # Skip __pycache__ directories
            if "__pycache__" in root:
                continue
                
            # Create __init__.py if it doesn't exist
            init_file = os.path.join(root, "__init__.py")
            if not os.path.exists(init_file):
                logger.info(f"Creating missing __init__.py in {root}")
                with open(init_file, "w") as f:
                    f.write("# Auto-generated __init__.py\n")
    
    def fix_frontend_dependencies(self):
        """Fix frontend dependencies"""
        self.print_header("FIXING FRONTEND DEPENDENCIES")
        
        # List of required dependencies
        dependencies = [
            "react-syntax-highlighter",
            "react-markdown",
            "@types/react-syntax-highlighter",
            "axios"
        ]
        
        # Install missing dependencies
        for dep in dependencies:
            logger.info(f"Installing {dep}...")
            self.run_command(f"npm install {dep} --save", cwd=self.frontend_dir)
    
    def start_backend(self):
        """Start the backend server"""
        self.print_header("STARTING BACKEND SERVER")
        
        # Kill any existing Python processes on port 8000
        self.run_command("powershell -Command \"Get-Process -Id (Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue).OwningProcess -ErrorAction SilentlyContinue | Stop-Process -Force\"")
        
        # Start the backend server
        logger.info("Starting backend server...")
        try:
            backend_command = "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"
            self.backend_process = subprocess.Popen(
                backend_command,
                shell=True,
                cwd=self.project_root
            )
            
            # Wait for the server to start
            logger.info("Waiting for backend server to start...")
            time.sleep(5)
            
            # Check if server is running
            health_check = self.run_command("python scripts\\simple_healthcheck.py")
            if health_check and "✓ Server is running" in health_check.stdout:
                logger.info("Backend server started successfully")
            else:
                logger.warning("Backend server might not have started properly")
                
                # Try with minimal backend
                logger.info("Trying minimal backend...")
                if self.backend_process:
                    self.backend_process.terminate()
                    time.sleep(2)
                
                self.backend_process = subprocess.Popen(
                    "python scripts\\run_minimal_backend.py",
                    shell=True,
                    cwd=self.project_root
                )
                
                # Wait for the minimal server to start
                time.sleep(5)
                
                # Check if minimal server is running
                health_check = self.run_command("python scripts\\simple_healthcheck.py")
                if health_check and "✓ Server is running" in health_check.stdout:
                    logger.info("Minimal backend server started successfully")
                else:
                    logger.error("Failed to start backend server")
        except Exception as e:
            logger.error(f"Error starting backend server: {str(e)}")
    
    def start_frontend(self):
        """Start the frontend development server"""
        self.print_header("STARTING FRONTEND SERVER")
        
        # Kill any existing processes on port 3000
        self.run_command("powershell -Command \"Get-Process -Id (Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue).OwningProcess -ErrorAction SilentlyContinue | Stop-Process -Force\"")
        
        # Start the frontend server
        logger.info("Starting frontend server...")
        try:
            frontend_command = "npm start"
            self.frontend_process = subprocess.Popen(
                frontend_command,
                shell=True,
                cwd=self.frontend_dir
            )
            
            # Wait for the server to start
            logger.info("Waiting for frontend server to start...")
            time.sleep(10)
            
            # Check if server is running
            frontend_check = self.run_command("powershell -Command \"Test-NetConnection -ComputerName localhost -Port 3000\"")
            if frontend_check and "TcpTestSucceeded : True" in frontend_check.stdout:
                logger.info("Frontend server started successfully")
                logger.info("You can access the frontend at: http://localhost:3000")
            else:
                logger.warning("Frontend server might not have started properly")
        except Exception as e:
            logger.error(f"Error starting frontend server: {str(e)}")
    
    def run(self):
        """Run the local development starter"""
        self.print_header("ADE PLATFORM LOCAL DEVELOPMENT STARTER")
        
        # Step 1: Fix critical issues
        self.fix_init_files()
        self.fix_frontend_dependencies()
        
        # Step 2: Start backend server
        self.start_backend()
        
        # Step 3: Start frontend server
        self.start_frontend()
        
        # Summary
        self.print_header("STARTUP COMPLETE")
        logger.info("The ADE platform should now be running locally.")
        logger.info("Frontend: http://localhost:3000")
        logger.info("Backend: http://localhost:8000")
        logger.info("\nPress Ctrl+C to stop the servers.")
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping servers...")
            if self.backend_process:
                self.backend_process.terminate()
            if self.frontend_process:
                self.frontend_process.terminate()
            logger.info("Servers stopped.")

def main():
    """Main function"""
    starter = LocalDevStarter()
    starter.run()

if __name__ == "__main__":
    main()
