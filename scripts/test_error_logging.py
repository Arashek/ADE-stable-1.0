#!/usr/bin/env python
"""
Test Script for Error Logging System

This script tests the error logging system by generating test errors and 
verifying that they are properly captured and recorded in both backend and frontend.
"""

import os
import sys
import json
import requests
import time
from pathlib import Path
from datetime import datetime

# Constants
BACKEND_URL = "http://localhost:8000"
ERROR_LOG_ENDPOINT = f"{BACKEND_URL}/api/error-logging/log"
ERROR_QUERY_ENDPOINT = f"{BACKEND_URL}/api/error-logging/recent"

# Setup logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_error_logging.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("test_error_logging")

def test_log_backend_error():
    """Test logging a backend error directly"""
    logger.info("Testing backend error logging...")
    
    # Prepare test error data
    error_data = {
        "message": "Test backend error",
        "error_type": "TestError",
        "category": "TESTING",
        "severity": "INFO",
        "component": "test_script",
        "stack_trace": "Traceback (most recent call last):\n  File \"test_error_logging.py\", line 1, in <module>\n    raise TestError(\"Test backend error\")",
        "context": {
            "test_id": "backend_direct_test",
            "timestamp": datetime.now().isoformat()
        }
    }
    
    try:
        # Send error to backend
        response = requests.post(ERROR_LOG_ENDPOINT, json=error_data)
        
        if response.status_code == 200:
            logger.info("Successfully logged backend error")
            logger.info(f"Response: {response.json()}")
            return True
        else:
            logger.error(f"Failed to log backend error. Status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Exception when logging backend error: {str(e)}")
        return False

def test_query_error_logs():
    """Test querying error logs from the backend"""
    logger.info("Testing error log query...")
    
    try:
        # Query recent error logs
        response = requests.get(ERROR_QUERY_ENDPOINT)
        
        if response.status_code == 200:
            logs = response.json()
            logger.info(f"Successfully retrieved {len(logs)} error logs")
            
            # Display the most recent logs
            for i, log in enumerate(logs[:5]):
                logger.info(f"Log {i+1}: {json.dumps(log, indent=2)}")
            
            return True
        else:
            logger.error(f"Failed to query error logs. Status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Exception when querying error logs: {str(e)}")
        return False

def test_simulated_frontend_error():
    """Test logging a simulated frontend error"""
    logger.info("Testing simulated frontend error logging...")
    
    # Prepare simulated frontend error data
    error_data = {
        "message": "Uncaught TypeError: Cannot read property 'value' of undefined",
        "error_type": "TypeError",
        "category": "RENDERING",
        "severity": "ERROR",
        "component": "frontend",
        "source": "MainDashboard.tsx",
        "stack_trace": "TypeError: Cannot read property 'value' of undefined\n    at MainDashboard (MainDashboard.tsx:42)\n    at renderWithHooks (react-dom.development.js:16305)\n    at mountIndeterminateComponent (react-dom.development.js:20074)",
        "context": {
            "browser": "Chrome",
            "os": "Windows",
            "view": "dashboard",
            "timestamp": datetime.now().isoformat()
        }
    }
    
    try:
        # Send simulated frontend error to backend
        response = requests.post(ERROR_LOG_ENDPOINT, json=error_data)
        
        if response.status_code == 200:
            logger.info("Successfully logged simulated frontend error")
            logger.info(f"Response: {response.json()}")
            return True
        else:
            logger.error(f"Failed to log simulated frontend error. Status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Exception when logging simulated frontend error: {str(e)}")
        return False

def main():
    """Main test function"""
    logger.info("Starting error logging tests...")
    
    # Track test results
    results = {
        "backend_direct": False,
        "query_logs": False,
        "frontend_simulated": False
    }
    
    # Test backend error logging
    results["backend_direct"] = test_log_backend_error()
    
    # Wait a moment for logs to be processed
    time.sleep(1)
    
    # Test querying error logs
    results["query_logs"] = test_query_error_logs()
    
    # Test simulated frontend error
    results["frontend_simulated"] = test_simulated_frontend_error()
    
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
