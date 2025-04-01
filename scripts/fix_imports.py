#!/usr/bin/env python
"""
Import Fix Script for ADE Backend

This script diagnoses and fixes common import issues in the ADE backend,
focusing on the problems that prevent the Agent Coordination System from working.
"""

import os
import sys
import importlib
import pkgutil
from pathlib import Path
import re

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def check_package_structure():
    """Check and fix package structure issues"""
    print_section("CHECKING PACKAGE STRUCTURE")
    
    # Critical directories that should have __init__.py files
    critical_dirs = [
        "",  # root backend directory
        "agents",
        "agents/specialized_agents",
        "routes",
        "services",
        "services/coordination",
        "utils",
        "config",
        "database"
    ]
    
    for dir_path in critical_dirs:
        full_path = backend_dir / dir_path
        init_path = full_path / "__init__.py"
        
        if not full_path.exists():
            print(f"✗ Directory missing: {dir_path}")
            continue
            
        if not init_path.exists():
            print(f"✗ Missing __init__.py in {dir_path}")
            print(f"  Creating {init_path}")
            
            # Create __init__.py file
            init_path.touch()
            print(f"✓ Created {init_path}")
        else:
            print(f"✓ Found __init__.py in {dir_path}")

def fix_relative_imports(file_path):
    """Fix relative imports in a Python file"""
    if not Path(file_path).exists():
        print(f"✗ File not found: {file_path}")
        return False
        
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Detect and fix relative imports that are beyond top level
    # Pattern: from ..module import X or import ..module
    relative_import_pattern = r'(from \.\.+[\w\.]+|import \.\.+[\w\.]+)'
    has_relative_imports = bool(re.search(relative_import_pattern, content))
    
    if has_relative_imports:
        print(f"✗ Found problematic relative imports in {file_path}")
        
        # Get the file's relative path from backend directory
        rel_path = os.path.relpath(file_path, backend_dir)
        # Calculate the module path
        module_path = os.path.dirname(rel_path).replace(os.path.sep, '.')
        
        # Replace relative imports with absolute imports
        # This is a simplified approach; a more robust solution would be needed for complex cases
        updated_content = re.sub(
            r'from \.\.([\w\.]+) import', 
            lambda m: f'from {module_path.split(".", 1)[0]}.{m.group(1)} import', 
            content
        )
        updated_content = re.sub(
            r'import \.\.([\w\.]+)', 
            lambda m: f'import {module_path.split(".", 1)[0]}.{m.group(1)}', 
            updated_content
        )
        
        if updated_content != content:
            with open(file_path, 'w') as f:
                f.write(updated_content)
            print(f"✓ Fixed relative imports in {file_path}")
            return True
        else:
            print(f"! Could not automatically fix imports in {file_path}")
            return False
    else:
        print(f"✓ No problematic relative imports in {file_path}")
        return False

def check_specific_imports():
    """Check and try to fix specific import issues based on known problems"""
    print_section("CHECKING CRITICAL IMPORTS")
    
    # Key files with known import issues
    critical_files = [
        "routes/owner_panel_routes.py",
        "routes/coordination_api.py",
        "services/owner_panel_service.py",
        "agents/specialized_agents/design_agent.py",
        "agents/specialized_agents/development_agent.py",
        "agents/agent_coordinator.py"
    ]
    
    files_fixed = []
    for file_path in critical_files:
        full_path = backend_dir / file_path
        print(f"\nChecking {file_path}...")
        if fix_relative_imports(full_path):
            files_fixed.append(file_path)
    
    if files_fixed:
        print(f"\nFixed imports in {len(files_fixed)} files:")
        for file in files_fixed:
            print(f"  - {file}")
    else:
        print("\nNo files needed import fixes")

def create_missing_base_agent():
    """Create base_agent.py if missing"""
    print_section("CHECKING FOR MISSING BASE AGENT")
    
    base_agent_path = backend_dir / "agents" / "base_agent.py"
    if not base_agent_path.exists():
        print(f"✗ Missing {base_agent_path}")
        print(f"  Creating base_agent.py...")
        
        # Create a basic base_agent.py file
        base_agent_content = '''"""
Base Agent Module

This module provides the BaseAgent class that all specialized agents inherit from.
It defines the common interface and functionality for all agents in the ADE platform.
"""

from typing import Dict, List, Any, Optional
import logging
import asyncio
import uuid

logger = logging.getLogger(__name__)

class BaseAgent:
    """Base class for all agents in the ADE platform"""
    
    def __init__(self, agent_id: Optional[str] = None, agent_type: str = "base"):
        """Initialize the base agent
        
        Args:
            agent_id: Unique identifier for this agent instance
            agent_type: Type of agent (e.g., 'design', 'development')
        """
        self.agent_id = agent_id or str(uuid.uuid4())
        self.agent_type = agent_type
        self.status = "initialized"
        self.capabilities = []
        logger.info(f"Initialized {agent_type} agent with ID {self.agent_id}")
    
    async def initialize(self) -> bool:
        """Initialize the agent's resources and connections
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        self.status = "ready"
        return True
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a request and return a response
        
        Args:
            request: Dictionary containing the request parameters
            
        Returns:
            Dict[str, Any]: Response from the agent
        """
        raise NotImplementedError("Subclasses must implement process_request()")
    
    async def cleanup(self) -> bool:
        """Clean up resources used by the agent
        
        Returns:
            bool: True if cleanup was successful, False otherwise
        """
        self.status = "terminated"
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the agent
        
        Returns:
            Dict[str, Any]: Dictionary with status information
        """
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": self.status,
            "capabilities": self.capabilities
        }
'''
        
        # Write the file
        with open(base_agent_path, 'w') as f:
            f.write(base_agent_content)
            
        print(f"✓ Created {base_agent_path}")
    else:
        print(f"✓ base_agent.py exists")

def check_pydantic_version():
    """Check if pydantic version is correct"""
    print_section("CHECKING PYDANTIC VERSION")
    
    try:
        import pydantic
        version = pydantic.__version__
        print(f"Found pydantic version {version}")
        
        if version.startswith("2."):
            print(f"✗ Pydantic version 2.x detected - ADE requires < 2.0")
            print("  To fix: pip install pydantic==1.10.8")
            print("  Run this command to downgrade:")
            print("  pip install pydantic==1.10.8 --force-reinstall")
        else:
            print(f"✓ Pydantic version {version} is compatible")
    except ImportError:
        print("✗ Pydantic not installed")
        print("  To fix: pip install pydantic==1.10.8")

def main():
    """Main function"""
    print_section("ADE BACKEND IMPORT FIXER")
    print("This script checks and fixes common import issues in the ADE backend.")
    
    # Run all checks and fixes
    check_package_structure()
    create_missing_base_agent()
    check_specific_imports()
    check_pydantic_version()
    
    print_section("FIX COMPLETE")
    print("Import issues have been identified and fixed where possible.")
    print("Try running the backend server now:")
    print("  cd d:\\ADE-stable-1.0")
    print("  python -m uvicorn backend.main:app --reload --port 8000")

if __name__ == "__main__":
    main()
