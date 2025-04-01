"""
Import Test Script for ADE Backend

This script tests importing all the key modules in the ADE backend
to identify which specific imports are causing issues.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("import_test")

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_import(module_path):
    """Test importing a specific module"""
    try:
        exec(f"import {module_path}")
        logger.info(f"✅ Successfully imported {module_path}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to import {module_path}: {str(e)}")
        return False

def main():
    """Main function to test imports"""
    logger.info("Testing imports for ADE backend modules...")
    
    # List of key modules to test
    modules = [
        "config.settings",
        "routes.owner_panel_routes",
        "routes.coordination_api",
        "services.owner_panel_service",
        "services.coordination.agent_coordinator",
        "services.memory.memory_service",
        "services.memory.api.memory_api",
        "services.mcp.visual_perception_mcp",
        "services.monitoring",
        "services.core.base_agent",
        "services.agents.specialized.validation_agent",
        "services.agents.specialized.design_agent",
        "services.agents.specialized.architecture_agent",
        "services.agents.specialized.security_agent",
        "services.agents.specialized.performance_agent"
    ]
    
    success_count = 0
    for module in modules:
        if test_import(module):
            success_count += 1
    
    logger.info(f"Import test completed: {success_count}/{len(modules)} modules imported successfully")

if __name__ == "__main__":
    main()
