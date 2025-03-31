#!/usr/bin/env python
"""
ADE Environment Setup Script

This script sets up a virtual environment for the ADE platform and installs
all required dependencies for both backend and frontend components.
"""

import os
import sys
import subprocess
import argparse
import platform
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('environment_setup.log')
    ]
)
logger = logging.getLogger("environment_setup")

# Define paths
PROJECT_ROOT = Path(__file__).resolve().parent
VENV_DIR = PROJECT_ROOT / "venv"
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"


def check_python_version():
    """Check if the Python version is compatible."""
    required_version = (3, 8)
    current_version = sys.version_info
    
    if current_version < required_version:
        logger.error(f"Python {required_version[0]}.{required_version[1]} or higher is required.")
        logger.error(f"Current version: {current_version[0]}.{current_version[1]}")
        return False
    
    return True


def check_node_npm():
    """Check if Node.js and npm are installed."""
    try:
        node_version = subprocess.check_output(["node", "--version"], text=True).strip()
        npm_version = subprocess.check_output(["npm", "--version"], text=True).strip()
        
        logger.info(f"Node.js version: {node_version}")
        logger.info(f"npm version: {npm_version}")
        
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        logger.error("Node.js and npm are required but not found.")
        logger.error("Please install Node.js and npm before continuing.")
        return False


def create_virtual_environment():
    """Create a Python virtual environment."""
    if VENV_DIR.exists():
        logger.info(f"Virtual environment already exists at {VENV_DIR}")
        return True
    
    try:
        logger.info(f"Creating virtual environment at {VENV_DIR}")
        subprocess.check_call([sys.executable, "-m", "venv", str(VENV_DIR)])
        logger.info("Virtual environment created successfully")
        return True
    except subprocess.SubprocessError as e:
        logger.error(f"Failed to create virtual environment: {e}")
        return False


def get_venv_python_path():
    """Get the path to the Python executable in the virtual environment."""
    if platform.system() == "Windows":
        return VENV_DIR / "Scripts" / "python.exe"
    else:
        return VENV_DIR / "bin" / "python"


def get_venv_pip_path():
    """Get the path to the pip executable in the virtual environment."""
    if platform.system() == "Windows":
        return VENV_DIR / "Scripts" / "pip.exe"
    else:
        return VENV_DIR / "bin" / "pip"


def create_requirements_file():
    """Create a requirements.txt file if it doesn't exist."""
    if REQUIREMENTS_FILE.exists():
        logger.info(f"Requirements file already exists at {REQUIREMENTS_FILE}")
        return
    
    logger.info(f"Creating requirements.txt file at {REQUIREMENTS_FILE}")
    
    requirements = [
        "fastapi==0.95.0",
        "uvicorn==0.21.1",
        "pydantic==1.10.7",
        "python-dotenv==1.0.0",
        "aiohttp==3.8.4",
        "pytest==7.3.1",
        "pytest-asyncio==0.21.0",
        "httpx==0.24.0",
        "jinja2==3.1.2",
        "sqlalchemy==2.0.9",
        "alembic==1.10.3",
        "python-multipart==0.0.6",
        "aiosqlite==0.18.0",
        "numpy==1.24.2",
        "pandas==2.0.0",
        "openai==0.27.4",
        "tiktoken==0.3.3",
        "tenacity==8.2.2",
        "rich==13.3.4",
        "pyyaml==6.0",
    ]
    
    with open(REQUIREMENTS_FILE, "w") as f:
        f.write("\n".join(requirements))
    
    logger.info("Requirements file created successfully")


def install_backend_dependencies():
    """Install backend dependencies in the virtual environment."""
    pip_path = get_venv_pip_path()
    
    try:
        logger.info("Upgrading pip in virtual environment")
        subprocess.check_call([str(pip_path), "install", "--upgrade", "pip"])
        
        logger.info("Installing backend dependencies")
        subprocess.check_call([str(pip_path), "install", "-r", str(REQUIREMENTS_FILE)])
        
        logger.info("Backend dependencies installed successfully")
        return True
    except subprocess.SubprocessError as e:
        logger.error(f"Failed to install backend dependencies: {e}")
        return False


def install_frontend_dependencies():
    """Install frontend dependencies."""
    if not FRONTEND_DIR.exists():
        logger.error(f"Frontend directory not found at {FRONTEND_DIR}")
        return False
    
    try:
        logger.info("Installing frontend dependencies")
        subprocess.check_call(["npm", "install"], cwd=str(FRONTEND_DIR))
        
        logger.info("Frontend dependencies installed successfully")
        return True
    except subprocess.SubprocessError as e:
        logger.error(f"Failed to install frontend dependencies: {e}")
        return False


def create_activation_scripts():
    """Create activation scripts for the virtual environment."""
    # Windows activation script (PowerShell)
    activate_ps1 = PROJECT_ROOT / "activate_ade.ps1"
    with open(activate_ps1, "w") as f:
        f.write(f"""# ADE Activation Script for PowerShell
$env:ADE_ROOT = "{PROJECT_ROOT}"
Write-Host "Activating ADE virtual environment..." -ForegroundColor Green
& "{VENV_DIR / 'Scripts' / 'Activate.ps1'}"
Write-Host "ADE environment activated. You can now run:" -ForegroundColor Green
Write-Host "  - python -m backend.scripts.local_test_setup" -ForegroundColor Cyan
Write-Host "  - cd frontend && npm run dev" -ForegroundColor Cyan
""")
    
    # Unix activation script (bash)
    activate_sh = PROJECT_ROOT / "activate_ade.sh"
    with open(activate_sh, "w") as f:
        f.write(f"""#!/bin/bash
# ADE Activation Script for bash
export ADE_ROOT="{PROJECT_ROOT}"
echo "Activating ADE virtual environment..."
source "{VENV_DIR / 'bin' / 'activate'}"
echo "ADE environment activated. You can now run:"
echo "  - python -m backend.scripts.local_test_setup"
echo "  - cd frontend && npm run dev"
""")
    
    # Make the bash script executable on Unix systems
    if platform.system() != "Windows":
        os.chmod(activate_sh, 0o755)
    
    logger.info(f"Activation scripts created at {activate_ps1} and {activate_sh}")


def create_run_script():
    """Create a run script for the ADE platform."""
    run_script = PROJECT_ROOT / "run_ade.py"
    
    with open(run_script, "w") as f:
        f.write("""#!/usr/bin/env python
\"\"\"
ADE Platform Runner

This script runs the ADE platform in a virtual environment.
\"\"\"

import os
import sys
import subprocess
import platform
import time
import signal
import threading
from pathlib import Path

# Define paths
PROJECT_ROOT = Path(__file__).resolve().parent
VENV_DIR = PROJECT_ROOT / "venv"
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"

# Get the path to the Python executable in the virtual environment
if platform.system() == "Windows":
    PYTHON_PATH = VENV_DIR / "Scripts" / "python.exe"
else:
    PYTHON_PATH = VENV_DIR / "bin" / "python"

# Check if virtual environment exists
if not VENV_DIR.exists():
    print("Virtual environment not found. Please run setup_environment.py first.")
    sys.exit(1)

# Global variables for process management
backend_process = None
frontend_process = None
running = True

def start_backend():
    \"\"\"Start the backend server.\"\"\"
    global backend_process
    
    print("Starting backend server...")
    backend_process = subprocess.Popen(
        [str(PYTHON_PATH), "-m", "backend.main"],
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Monitor backend output
    while running and backend_process.poll() is None:
        line = backend_process.stdout.readline()
        if line:
            print(f"[BACKEND] {line.strip()}")
    
    if running and backend_process.poll() is not None:
        print(f"Backend server stopped with exit code {backend_process.returncode}")

def start_frontend():
    \"\"\"Start the frontend development server.\"\"\"
    global frontend_process
    
    print("Starting frontend development server...")
    if platform.system() == "Windows":
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=str(FRONTEND_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=True
        )
    else:
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=str(FRONTEND_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
    
    # Monitor frontend output
    while running and frontend_process.poll() is None:
        line = frontend_process.stdout.readline()
        if line:
            print(f"[FRONTEND] {line.strip()}")
    
    if running and frontend_process.poll() is not None:
        print(f"Frontend server stopped with exit code {frontend_process.returncode}")

def signal_handler(sig, frame):
    \"\"\"Handle Ctrl+C signal.\"\"\"
    global running
    print("Shutting down ADE platform...")
    running = False
    
    # Terminate processes
    if backend_process and backend_process.poll() is None:
        backend_process.terminate()
    
    if frontend_process and frontend_process.poll() is None:
        frontend_process.terminate()
    
    print("ADE platform shut down successfully")
    sys.exit(0)

def main():
    \"\"\"Main function to run the ADE platform.\"\"\"
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start backend and frontend in separate threads
    backend_thread = threading.Thread(target=start_backend)
    frontend_thread = threading.Thread(target=start_frontend)
    
    backend_thread.start()
    time.sleep(2)  # Wait for backend to start before starting frontend
    frontend_thread.start()
    
    # Wait for threads to complete
    try:
        while backend_thread.is_alive() or frontend_thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main()
""")
    
    # Make the script executable on Unix systems
    if platform.system() != "Windows":
        os.chmod(run_script, 0o755)
    
    logger.info(f"Run script created at {run_script}")


def main():
    """Main function to set up the environment."""
    parser = argparse.ArgumentParser(description="ADE Environment Setup")
    parser.add_argument("--backend-only", action="store_true", help="Only set up backend environment")
    parser.add_argument("--frontend-only", action="store_true", help="Only set up frontend environment")
    args = parser.parse_args()
    
    logger.info("Starting ADE environment setup")
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Set up backend
    if not args.frontend_only:
        # Create virtual environment
        if not create_virtual_environment():
            return 1
        
        # Create requirements file
        create_requirements_file()
        
        # Install backend dependencies
        if not install_backend_dependencies():
            return 1
    
    # Set up frontend
    if not args.backend_only:
        # Check Node.js and npm
        if not check_node_npm():
            return 1
        
        # Install frontend dependencies
        if not install_frontend_dependencies():
            return 1
    
    # Create activation scripts
    create_activation_scripts()
    
    # Create run script
    create_run_script()
    
    logger.info("ADE environment setup completed successfully")
    logger.info(f"To activate the environment on Windows, run: .\\activate_ade.ps1")
    logger.info(f"To activate the environment on Unix, run: source ./activate_ade.sh")
    logger.info(f"To run the ADE platform, run: python run_ade.py")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
