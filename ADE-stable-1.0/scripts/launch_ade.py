import os
import sys
from pathlib import Path
import subprocess
import venv
import json

def setup_environment():
    """Set up the Python virtual environment and install dependencies"""
    # Create virtual environment
    venv_dir = Path("venv")
    if not venv_dir.exists():
        print("Creating virtual environment...")
        venv.create(venv_dir, with_pip=True)
    
    # Get the Python executable from the virtual environment
    if sys.platform == "win32":
        python_exe = venv_dir / "Scripts" / "python.exe"
        pip_exe = venv_dir / "Scripts" / "pip.exe"
    else:
        python_exe = venv_dir / "bin" / "python"
        pip_exe = venv_dir / "bin" / "pip"
    
    # Install dependencies
    print("Installing dependencies...")
    subprocess.run([str(pip_exe), "install", "-r", "requirements.txt"])
    
    return python_exe

def launch_ade():
    """Launch the ADE platform"""
    # Set up environment
    python_exe = setup_environment()
    
    # Set environment variables
    os.environ["ADE_PROJECT_DIR"] = str(Path.cwd())
    os.environ["PYTHONPATH"] = str(Path.cwd())
    
    # Launch the ADE platform
    print("Launching ADE platform...")
    subprocess.run([str(python_exe), "-m", "src.ade_platform"])

def main():
    """Main entry point"""
    try:
        launch_ade()
    except Exception as e:
        print(f"Error launching ADE platform: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 