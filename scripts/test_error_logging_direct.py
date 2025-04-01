#!/usr/bin/env python
"""
Direct Test Script for Error Logging System

This script tests the error logging utility directly without going through the API endpoints.
This helps isolate if issues are with the routes or with the underlying functionality.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import logging

# Add the backend directory to the path so we can import the modules
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.append(str(backend_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_error_logging_direct.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("test_error_logging_direct")

# Now import the error logging functions
try:
    from utils.error_logging import log_error, get_recent_errors, ErrorCategory, ErrorSeverity
    logger.info("Successfully imported error logging utilities")
except ImportError as e:
    logger.error(f"Failed to import error logging utilities: {str(e)}")
    sys.exit(1)

def test_direct_logging():
    """Test the log_error function directly"""
    logger.info("Testing direct error logging...")
    
    try:
        # Log a test error
        error_id = log_error(
            error="Test direct error",
            category=ErrorCategory.TESTING,
            severity=ErrorSeverity.INFO,
            component="test_script",
            context={
                "test_id": "direct_test",
                "timestamp": datetime.now().isoformat()
            }
        )
        
        logger.info(f"Successfully logged error with ID: {error_id}")
        return True
    except Exception as e:
        logger.error(f"Exception when logging error directly: {str(e)}")
        return False

def test_query_recent_errors():
    """Test querying recent errors directly"""
    logger.info("Testing direct error query...")
    
    try:
        # Get recent errors
        errors = get_recent_errors(limit=10)
        
        logger.info(f"Successfully retrieved {len(errors)} error logs")
        
        # Display the most recent logs
        for i, error in enumerate(errors[:5]):
            logger.info(f"Error {i+1}: {json.dumps(error, indent=2)}")
        
        return True
    except Exception as e:
        logger.error(f"Exception when querying errors directly: {str(e)}")
        return False

def main():
    """Main test function"""
    logger.info("Starting direct error logging tests...")
    
    # Track test results
    results = {
        "direct_logging": False,
        "query_errors": False
    }
    
    # Test direct error logging
    results["direct_logging"] = test_direct_logging()
    
    # Test querying errors directly
    results["query_errors"] = test_query_recent_errors()
    
    # Print summary
    logger.info("=== TEST RESULTS SUMMARY ===")
    for test_name, result in results.items():
        status = "PASSED" if result else "FAILED"
        logger.info(f"{test_name}: {status}")
    
    # Overall status
    if all(results.values()):
        logger.info("All tests PASSED!")
        return 0
    else:
        logger.error("Some tests FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
