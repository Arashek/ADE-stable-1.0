import sys
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_import(module_path, description):
    try:
        logger.info(f"Testing import: {description} ({module_path})")
        __import__(module_path)
        logger.info(f"✓ Success: {description}")
        return True
    except Exception as e:
        logger.error(f"✗ Error: {description} - {str(e)}")
        logger.error(traceback.format_exc())
        return False

# Test critical imports in sequence
print("===== TESTING BACKEND COMPONENTS =====")

# Test utility modules
test_import("config.settings", "Settings configuration")
test_import("utils.security", "Security utilities")
test_import("utils.backup", "Backup utilities")

# Test database modules
test_import("database.connection", "Database connection")
test_import("database.owner_panel_db", "Owner Panel database")
test_import("database.management_db", "Management database")

# Test models
test_import("models.owner_panel", "Owner Panel models")
test_import("models.management_components", "Management component models")

# Test authentication
test_import("auth.auth", "Authentication module")

# Test Owner Panel components
test_import("services.owner_panel_service", "Owner Panel service")
test_import("routes.owner_panel_routes", "Owner Panel routes")

# Test Coordination components
test_import("services.coordination.agent_coordinator", "Agent Coordinator")
test_import("routes.coordination_api", "Coordination API routes")

print("===== TEST SUMMARY =====")
print("See logs above for detailed results")
print("If all tests passed, the main app can now be initialized")
