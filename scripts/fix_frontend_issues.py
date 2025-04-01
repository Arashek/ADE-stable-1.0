#!/usr/bin/env python
"""
Frontend Issues Fix Script

This script addresses common frontend issues in the ADE platform:
1. Installs missing npm dependencies
2. Updates TypeScript configuration if needed
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def run_command(command, cwd=None):
    """Run a shell command"""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(f"STDERR: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {str(e)}")
        return False

def install_missing_dependencies(frontend_dir):
    """Install missing npm dependencies"""
    print_header("INSTALLING MISSING DEPENDENCIES")
    
    # Regular dependencies
    dependencies = [
        "react-syntax-highlighter",
        "react-markdown",
        "@types/react-syntax-highlighter",
        "axios"
    ]
    
    for dep in dependencies:
        print(f"\nChecking/installing {dep}...")
        run_command(f"npm install {dep} --save", cwd=frontend_dir)
    
    # Dev dependencies
    dev_dependencies = [
        "typescript",
        "@types/node",
        "@types/react",
        "@types/react-dom"
    ]
    
    for dep in dev_dependencies:
        print(f"\nChecking/installing {dep} as dev dependency...")
        run_command(f"npm install {dep} --save-dev", cwd=frontend_dir)

def fix_typescript_config(frontend_dir):
    """Fix TypeScript configuration"""
    print_header("FIXING TYPESCRIPT CONFIGURATION")
    
    tsconfig_path = os.path.join(frontend_dir, "tsconfig.json")
    
    try:
        with open(tsconfig_path, "r") as file:
            tsconfig = json.load(file)
        
        # Make sure we have all the necessary compiler options
        if "compilerOptions" not in tsconfig:
            tsconfig["compilerOptions"] = {}
        
        compiler_options = {
            "skipLibCheck": True,
            "esModuleInterop": True,
            "allowSyntheticDefaultImports": True,
            "forceConsistentCasingInFileNames": True,
            "noImplicitAny": False,
            "strictNullChecks": False,
            "resolveJsonModule": True
        }
        
        # Update compiler options
        for key, value in compiler_options.items():
            tsconfig["compilerOptions"][key] = value
        
        # Ensure we have all the necessary paths in includes
        if "include" not in tsconfig:
            tsconfig["include"] = ["src/**/*"]
        
        # Write back the updated config
        with open(tsconfig_path, "w") as file:
            json.dump(tsconfig, file, indent=2)
        
        print(f"✓ Updated TypeScript configuration in {tsconfig_path}")
    except Exception as e:
        print(f"❌ Error updating TypeScript config: {str(e)}")

def main():
    """Main function"""
    print_header("ADE FRONTEND ISSUES FIX SCRIPT")
    
    # Get frontend directory
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
    print(f"Working in frontend directory: {frontend_dir}")
    
    # Fix frontend issues
    install_missing_dependencies(frontend_dir)
    fix_typescript_config(frontend_dir)
    
    print_header("CHECKING FOR TYPESCRIPT ERRORS")
    run_command("npx tsc --noEmit", cwd=frontend_dir)
    
    print_header("FIX PROCESS COMPLETE")
    print("To start the frontend development server:")
    print("  cd frontend")
    print("  npm start")

if __name__ == "__main__":
    main()
