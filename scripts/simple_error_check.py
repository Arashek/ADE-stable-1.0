#!/usr/bin/env python
"""
Simple Error Check for ADE Platform

Focuses on identifying critical issues in the backend and frontend
to get the system running locally, with emphasis on the Agent Coordination System.
"""

import os
import sys
import subprocess
from pathlib import Path
import json

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def run_command(command, cwd=None):
    """Run a shell command and capture output"""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        return result
    except Exception as e:
        print(f"Error running command: {str(e)}")
        return None

def check_backend_imports():
    """Check for critical backend imports"""
    print_header("CHECKING BACKEND IMPORTS")
    
    project_root = Path(__file__).parent.parent
    backend_dir = project_root / "backend"
    
    # Critical modules for Agent Coordination System
    critical_modules = [
        "agents.agent_coordinator",
        "agents.specialized_agents.design_agent",
        "agents.specialized_agents.development_agent",
        "routes.coordination_api",
        "services.coordination.agent_interface"
    ]
    
    errors = []
    
    for module in critical_modules:
        print(f"Checking import for: {module}")
        
        # Create a simple import script
        import_script = """
import sys
sys.path.insert(0, '{backend_dir}')
try:
    import {module}
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {{type(e).__name__}}: {{str(e)}}")
""".format(backend_dir=str(backend_dir), module=module)
        
        temp_script = project_root / "temp_import_check.py"
        with open(temp_script, "w") as f:
            f.write(import_script)
        
        # Run the script
        result = run_command(f"python {temp_script}")
        
        if result:
            if "SUCCESS" in result.stdout:
                print(f"✓ Module {module} imported successfully")
            else:
                error_msg = result.stdout.strip()
                print(f"✗ {error_msg}")
                errors.append({
                    "module": module,
                    "error": error_msg
                })
        else:
            print(f"✗ Failed to check import for {module}")
        
        # Clean up
        if temp_script.exists():
            os.remove(temp_script)
    
    return errors

def check_frontend_dependencies():
    """Check for critical frontend dependencies"""
    print_header("CHECKING FRONTEND DEPENDENCIES")
    
    project_root = Path(__file__).parent.parent
    frontend_dir = project_root / "frontend"
    
    # Critical dependencies
    critical_dependencies = [
        "react-syntax-highlighter",
        "react-markdown",
        "axios"
    ]
    
    errors = []
    
    for dep in critical_dependencies:
        print(f"Checking dependency: {dep}")
        
        result = run_command(f"npm list {dep}", cwd=frontend_dir)
        
        if result and "empty" in result.stderr:
            print(f"✗ Missing dependency: {dep}")
            errors.append({
                "dependency": dep,
                "error": f"Missing dependency: {dep}"
            })
        else:
            print(f"✓ Dependency {dep} is installed")
    
    return errors

def check_servers():
    """Check if servers are running"""
    print_header("CHECKING SERVERS")
    
    errors = []
    
    # Check backend
    backend_result = run_command("netstat -ano | findstr :8000")
    if backend_result and "LISTENING" in backend_result.stdout:
        print("✓ Backend server is running on port 8000")
    else:
        print("✗ Backend server is not running on port 8000")
        errors.append({
            "server": "backend",
            "error": "Not running on port 8000"
        })
    
    # Check frontend
    frontend_result = run_command("netstat -ano | findstr :3001")
    if frontend_result and "LISTENING" in frontend_result.stdout:
        print("✓ Frontend server is running on port 3001")
    else:
        print("✗ Frontend server is not running on port 3001")
        errors.append({
            "server": "frontend",
            "error": "Not running on port 3001"
        })
    
    return errors

def check_critical_files():
    """Check for critical files"""
    print_header("CHECKING CRITICAL FILES")
    
    project_root = Path(__file__).parent.parent
    
    # Critical files for coordination system
    critical_files = [
        "backend/agents/agent_coordinator.py",
        "backend/agents/base_agent.py",
        "backend/routes/coordination_api.py",
        "backend/services/coordination/agent_interface.py",
        "frontend/src/components/agents/CoordinationSystem.tsx",
        "frontend/src/services/api.ts"
    ]
    
    errors = []
    
    for file_path in critical_files:
        full_path = project_root / file_path
        
        if full_path.exists():
            print(f"✓ Found critical file: {file_path}")
        else:
            print(f"✗ Missing critical file: {file_path}")
            errors.append({
                "file": file_path,
                "error": "File is missing"
            })
    
    return errors

def main():
    """Main function"""
    print_header("ADE SIMPLE ERROR CHECK")
    print("Checking for critical issues to get ADE running locally")
    
    # Run all checks
    backend_errors = check_backend_imports()
    frontend_errors = check_frontend_dependencies()
    server_errors = check_servers()
    file_errors = check_critical_files()
    
    # Summarize errors
    print_header("ERROR SUMMARY")
    
    if not any([backend_errors, frontend_errors, server_errors, file_errors]):
        print("✓ No critical errors found! Your system should be ready to run.")
    else:
        if backend_errors:
            print(f"✗ Found {len(backend_errors)} backend import errors")
        if frontend_errors:
            print(f"✗ Found {len(frontend_errors)} frontend dependency errors")
        if server_errors:
            print(f"✗ Found {len(server_errors)} server errors")
        if file_errors:
            print(f"✗ Found {len(file_errors)} missing critical files")
    
    # Recommendations
    print_header("RECOMMENDATIONS")
    
    if backend_errors:
        print("1. Fix backend import issues:")
        for error in backend_errors:
            print(f"   - {error['module']}: {error['error']}")
    
    if file_errors:
        print("2. Create missing critical files:")
        for error in file_errors:
            print(f"   - {error['file']}")
    
    if frontend_errors:
        print("3. Install missing frontend dependencies:")
        for error in frontend_errors:
            print(f"   - {error['dependency']}")
    
    if not any([backend_errors, frontend_errors, file_errors]):
        print("To start the system:")
        print("1. Run the backend server: python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000")
        print("2. Run the frontend: cd frontend && npm start")

if __name__ == "__main__":
    main()
