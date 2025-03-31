"""
ADE Backend Server Runner
This script sets up the correct Python path and runs the backend server.
"""

import os
import sys
import subprocess

# Add the backend directory to the Python path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

# Run the backend server using uvicorn
def run_backend():
    print("Starting ADE Backend Server...")
    print(f"Backend directory: {backend_dir}")
    
    # Run uvicorn with the correct Python path
    cmd = [
        "python", "-m", "uvicorn", 
        "main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000", 
        "--reload"
    ]
    
    # Change to the backend directory
    os.chdir(backend_dir)
    
    # Run the command
    subprocess.run(cmd)

if __name__ == "__main__":
    run_backend()
