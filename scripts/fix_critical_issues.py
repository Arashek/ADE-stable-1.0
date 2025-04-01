#!/usr/bin/env python
"""
Critical Issue Fixer for ADE Platform

Addresses the most common issues preventing ADE from running locally:
1. Import errors in backend Python code
2. Pydantic version issues 
3. Missing __init__.py files

Focus is on getting the core Agent Coordination System working first.
"""

import os
import sys
import importlib
import subprocess
from pathlib import Path
import re
import shutil
import glob

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def fix_init_files():
    """Create missing __init__.py files in Python packages"""
    print_header("FIXING MISSING __init__.py FILES")
    
    backend_dir = Path("backend")
    
    # Find all directories in backend
    dirs = []
    for root, subdirs, _ in os.walk(backend_dir):
        root_path = Path(root)
        dirs.append(root_path)
    
    # Create __init__.py in each directory if missing
    for dir_path in dirs:
        init_file = dir_path / "__init__.py"
        if not init_file.exists():
            print(f"Creating missing {init_file}")
            init_file.touch()
    
    print("✓ Created all missing __init__.py files")

def fix_import_errors():
    """Fix import errors in Python files"""
    print_header("FIXING IMPORT ERRORS")
    
    problematic_files = [
        "backend/routes/owner_panel_routes.py",
        "backend/routes/coordination_api.py",
        "backend/services/owner_panel_service.py"
    ]
    
    for file_path in problematic_files:
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"File doesn't exist: {file_path}")
            continue
            
        print(f"Fixing imports in {file_path}")
        
        # Read file content
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Fix relative imports with absolute imports
        # Replace relative imports (from .. or from .) with absolute imports
        modified_content = re.sub(
            r'from \.\.(\w+)', 
            r'from backend.\1', 
            content
        )
        modified_content = re.sub(
            r'from \.(\w+)', 
            lambda m: f'from backend.{file_path.parent.name}.{m.group(1)}', 
            modified_content
        )
        
        # Write modified content back
        with open(file_path, 'w') as f:
            f.write(modified_content)
        
        print(f"✓ Fixed imports in {file_path}")

def disable_owner_panel():
    """Temporarily disable owner panel until core functionality is working"""
    print_header("TEMPORARILY DISABLING OWNER PANEL")
    
    main_file = Path("backend/main.py")
    if not main_file.exists():
        print(f"Main file doesn't exist: {main_file}")
        return
    
    print(f"Modifying {main_file} to disable owner panel routes")
    
    # Read file content
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Modify the include_router line for owner panel
    modified_content = re.sub(
        r'app\.include_router\(owner_panel_router, prefix=settings\.API_PREFIX\)',
        r'# Temporarily disabled: app.include_router(owner_panel_router, prefix=settings.API_PREFIX)',
        content
    )
    
    # Write modified content back
    with open(main_file, 'w') as f:
        f.write(modified_content)
    
    print(f"✓ Temporarily disabled owner panel routes in main.py")

def check_pydantic_version():
    """Check and downgrade pydantic if needed"""
    print_header("CHECKING PYDANTIC VERSION")
    
    try:
        import pydantic
        version = pydantic.__version__
        print(f"Current pydantic version: {version}")
        
        if version.startswith("2."):
            print("Pydantic 2.x detected, needs downgrade to 1.10.8")
            
            # Run pip to downgrade
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "pydantic==1.10.8", "--force-reinstall"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✓ Successfully downgraded pydantic to 1.10.8")
            else:
                print("❌ Failed to downgrade pydantic")
                print(result.stderr)
        else:
            print(f"✓ Pydantic version is already compatible: {version}")
    except ImportError:
        print("Pydantic not installed, installing version 1.10.8")
        # Install pydantic 1.10.8
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "pydantic==1.10.8"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ Successfully installed pydantic 1.10.8")
        else:
            print("❌ Failed to install pydantic")
            print(result.stderr)

def create_base_agent():
    """Create base_agent.py file if missing"""
    print_header("CREATING BASE AGENT")
    
    base_agent_path = Path("backend/agents/base_agent.py")
    
    # Create the directory if it doesn't exist
    base_agent_path.parent.mkdir(parents=True, exist_ok=True)
    
    if not base_agent_path.exists():
        print(f"Creating missing {base_agent_path}")
        
        base_agent_content = """\"\"\"
Base Agent Module 

This module defines the base agent class that all specialized agents inherit from.
\"\"\"

from typing import Dict, List, Any, Optional
import logging
import uuid

logger = logging.getLogger(__name__)

class BaseAgent:
    \"\"\"Base class for all agents in the system\"\"\"
    
    def __init__(self, agent_id: Optional[str] = None, agent_type: str = "base"):
        self.agent_id = agent_id or str(uuid.uuid4())
        self.agent_type = agent_type
        self.status = "initialized"
        self.capabilities = []
        logger.info(f"Initialized {agent_type} agent with ID {self.agent_id}")
    
    async def initialize(self) -> bool:
        \"\"\"Initialize the agent\"\"\"
        self.status = "ready"
        return True
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Process a request\"\"\"
        raise NotImplementedError("Subclasses must implement process_request()")
    
    async def cleanup(self) -> bool:
        \"\"\"Clean up resources\"\"\"
        self.status = "terminated"
        return True
    
    def get_status(self) -> Dict[str, Any]:
        \"\"\"Get current status\"\"\"
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": self.status,
            "capabilities": self.capabilities
        }
"""
        
        with open(base_agent_path, 'w') as f:
            f.write(base_agent_content)
        
        print(f"✓ Created {base_agent_path}")
    else:
        print(f"✓ Base agent file already exists")

def fix_cors_settings():
    """Fix CORS settings to allow frontend to connect to backend"""
    print_header("FIXING CORS SETTINGS")
    
    main_file = Path("backend/main.py")
    if not main_file.exists():
        print(f"Main file doesn't exist: {main_file}")
        return
    
    print(f"Modifying {main_file} to enable CORS for local frontend")
    
    # Read file content
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Look for the CORS middleware section and ensure it allows the frontend origin
    if "CORSMiddleware" in content:
        # Find the origins list
        origins_pattern = r'origins\s*=\s*\[(.*?)\]'
        origins_match = re.search(origins_pattern, content, re.DOTALL)
        
        if origins_match:
            origins_text = origins_match.group(1)
            if "http://localhost:3001" not in origins_text:
                # Add the frontend origin if it's not already there
                modified_origins = origins_text + ', "http://localhost:3001"'
                modified_content = content.replace(origins_text, modified_origins)
                
                # Write modified content back
                with open(main_file, 'w') as f:
                    f.write(modified_content)
                
                print("✓ Added frontend origin to CORS allowed origins")
            else:
                print("✓ Frontend origin already in CORS allowed origins")
        else:
            print("Could not find origins list in CORS middleware setup")
    else:
        print("Could not find CORS middleware in main.py")

def main():
    """Main function"""
    print_header("ADE PLATFORM CRITICAL ISSUE FIXER")
    print("This script fixes critical issues preventing ADE from running locally.")
    
    # Run fixes
    fix_init_files()
    fix_import_errors()
    create_base_agent()
    check_pydantic_version()
    fix_cors_settings()
    disable_owner_panel()
    
    print_header("FIX COMPLETE")
    print("Critical issues have been addressed. Try running the backend server with:")
    print("  cd d:\\ADE-stable-1.0")
    print("  python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000")
    print("\nAnd the frontend with:")
    print("  cd d:\\ADE-stable-1.0\\frontend")
    print("  npm start")

if __name__ == "__main__":
    main()
