#!/usr/bin/env python
"""
Simple Error Checker for ADE Platform

Identifies common issues in the codebase to help get the system running locally.
Focuses on checking import errors and file existence for critical components.
"""

import os
import sys
import importlib
import subprocess
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def check_backend_imports():
    """Check critical backend imports"""
    print_header("CHECKING BACKEND IMPORTS")
    
    # Critical modules to check
    critical_modules = [
        "routes.owner_panel_routes",
        "routes.coordination_api",
        "services.owner_panel_service",
        "agents.specialized_agents.design_agent",
        "agents.specialized_agents.development_agent",
        "agents.agent_coordinator",
        "utils.security"
    ]
    
    # Add backend directory to path
    backend_dir = os.path.abspath("backend")
    sys.path.insert(0, backend_dir)
    
    # Try importing each module
    for module in critical_modules:
        print(f"Checking import for: {module}")
        try:
            # Try to import
            importlib.import_module(module)
            print(f"✓ SUCCESS: {module} imports correctly")
        except Exception as e:
            print(f"✗ ERROR: Failed to import {module}")
            print(f"  {type(e).__name__}: {str(e)}")
            
            # For import errors, suggest the missing file
            if isinstance(e, ImportError) and "No module named" in str(e):
                missing_module = str(e).split("'")[1]
                suggested_path = os.path.join(backend_dir, *missing_module.split("."))
                print(f"  Suggestion: Check if {suggested_path}.py exists")

def check_frontend_structure():
    """Check critical frontend files"""
    print_header("CHECKING FRONTEND STRUCTURE")
    
    # Critical frontend files
    critical_files = [
        "src/App.tsx",
        "src/index.tsx",
        "src/components/MainDashboard.tsx",
        "src/components/agents/AgentDashboard.tsx",
        "src/components/agents/CoordinationSystem.tsx",
        "src/services/api.ts",
        "package.json",
        "tsconfig.json"
    ]
    
    # Frontend directory
    frontend_dir = os.path.abspath("frontend")
    
    # Check each file
    for file in critical_files:
        file_path = os.path.join(frontend_dir, file)
        if os.path.exists(file_path):
            print(f"✓ FOUND: {file}")
        else:
            print(f"✗ MISSING: {file}")
            print(f"  Suggestion: Create {file} file")

def check_typescript_errors():
    """Check for TypeScript errors"""
    print_header("CHECKING TYPESCRIPT ERRORS")
    
    # Frontend directory
    frontend_dir = os.path.abspath("frontend")
    
    # Run TypeScript check
    print("Running TypeScript check...")
    try:
        result = subprocess.run(
            ["npx", "tsc", "--noEmit"],
            cwd=frontend_dir,
            capture_output=True,
            text=True
        )
        
        # Process output
        if result.returncode == 0:
            print("✓ No TypeScript errors found")
        else:
            errors = result.stdout.strip().split("\n")
            error_count = len([line for line in errors if "error TS" in line])
            print(f"✗ Found {error_count} TypeScript errors")
            
            # Show first 5 errors
            print("\nFirst 5 errors:")
            for i, line in enumerate([line for line in errors if "error TS" in line][:5]):
                print(f"{i+1}. {line.strip()}")
                
            print("\nSuggestion: Fix these TypeScript errors")
    except Exception as e:
        print(f"✗ Failed to run TypeScript check: {str(e)}")
        print("  Suggestion: Make sure TypeScript is installed (npm install typescript)")

def check_ports():
    """Check if required ports are available"""
    print_header("CHECKING REQUIRED PORTS")
    
    # Check if ports are in use
    ports = {
        "Backend": 8000,
        "Frontend": 3001
    }
    
    for service, port in ports.items():
        try:
            # Windows command to check port
            result = subprocess.run(
                ["netstat", "-ano", "|", "findstr", f":{port}"],
                shell=True,
                capture_output=True,
                text=True
            )
            
            if "LISTENING" in result.stdout:
                print(f"✗ {service} port {port} is already in use")
                print(f"  Suggestion: Either stop the process using port {port} or configure {service} to use a different port")
            else:
                print(f"✓ {service} port {port} is available")
        except Exception as e:
            print(f"! Could not check {service} port {port}: {str(e)}")

def check_dependencies():
    """Check for required dependencies"""
    print_header("CHECKING DEPENDENCIES")
    
    # Python packages
    python_deps = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "sqlalchemy",
        "pyjwt"
    ]
    
    print("Checking Python dependencies:")
    for dep in python_deps:
        try:
            importlib.import_module(dep)
            print(f"✓ {dep} is installed")
        except ImportError:
            print(f"✗ {dep} is not installed")
            print(f"  Suggestion: pip install {dep}")
    
    # Check for specific pydantic version (needs <2.0)
    try:
        import pydantic
        version = pydantic.__version__
        if version.startswith("2."):
            print(f"✗ pydantic version {version} detected - ADE requires <2.0")
            print("  Suggestion: pip install pydantic==1.10.8")
        else:
            print(f"✓ pydantic version {version} is compatible")
    except:
        pass

def main():
    """Main function"""
    print_header("ADE PLATFORM ERROR CHECKER")
    print("This script checks for common issues in the ADE codebase.")
    print("The goal is to help you get the system running locally.")
    
    # Run all checks
    check_backend_imports()
    check_frontend_structure()
    check_typescript_errors()
    check_ports()
    check_dependencies()
    
    print_header("CHECK COMPLETE")
    print("Review the issues above and fix them one by one.")
    print("Start with backend import errors as they're most critical for ADE functionality.")

if __name__ == "__main__":
    main()
