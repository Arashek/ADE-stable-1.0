"""
ADE Platform - API Endpoint Testing Script
This script tests the API endpoints of the simplified backend to verify they're working correctly.
"""

import sys
import os
import requests
import json
import logging
from time import sleep
from typing import Dict, Any, List, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("api_tests.log")
    ]
)

logger = logging.getLogger(__name__)

# Base URL for API requests
BASE_URL = "http://localhost:8003/api"

def make_request(endpoint: str, method: str = "GET", data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Make an HTTP request to the API endpoint
    """
    url = f"{BASE_URL}/{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=5)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=5)
        else:
            logger.error(f"Unsupported HTTP method: {method}")
            return {"error": f"Unsupported HTTP method: {method}"}
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making request to {url}: {str(e)}")
        return {"error": str(e)}

def check_server_connection(max_retries=3, retry_delay=2):
    """Check if the backend server is running and accessible"""
    logger.info(f"Checking connection to backend server at {BASE_URL}...")
    
    for i in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                logger.info("Successfully connected to backend server")
                return True
            else:
                logger.warning(f"Server responded with status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {i+1}/{max_retries}: Failed to connect to server: {str(e)}")
            
        if i < max_retries - 1:
            logger.info(f"Retrying in {retry_delay} seconds...")
            sleep(retry_delay)
    
    logger.error("Backend server is not running or not accessible!")
    logger.info("Run: python scripts\\simplified_backend.py")
    return False

def test_health_endpoint() -> bool:
    """
    Test the health check endpoint
    """
    logger.info("Testing health check endpoint...")
    result = make_request("health")
    
    if "error" in result:
        logger.error(f"Health check failed: {result['error']}")
        return False
    
    logger.info(f"Health check result: {result}")
    return result.get("status") == "ok"

def test_echo_endpoint() -> bool:
    """
    Test the echo endpoint
    """
    test_data = {
        "message": "Hello, ADE!",
        "timestamp": "2025-04-04T15:20:00Z"
    }
    
    logger.info("Testing echo endpoint...")
    result = make_request("echo", method="POST", data=test_data)
    
    if "error" in result:
        logger.error(f"Echo test failed: {result['error']}")
        return False
    
    logger.info(f"Echo test result: {result}")
    return "echo" in result and result["echo"] == test_data

def test_prompt_processing() -> bool:
    """
    Test the prompt processing endpoint
    """
    test_prompt = {
        "prompt": "Create a simple React todo application with local storage"
    }
    
    logger.info("Testing prompt processing endpoint...")
    result = make_request("process_prompt", method="POST", data=test_prompt)
    
    if "error" in result:
        logger.error(f"Prompt processing test failed: {result['error']}")
        return False
    
    logger.info(f"Prompt processing result: {result}")
    return "status" in result and result["status"] == "success"

def test_status_endpoint() -> bool:
    """
    Test the status endpoint
    """
    test_task_id = "test-task-123"
    
    logger.info(f"Testing status endpoint for task {test_task_id}...")
    result = make_request(f"status/{test_task_id}")
    
    if "error" in result:
        logger.error(f"Status test failed: {result['error']}")
        return False
    
    logger.info(f"Status test result: {result}")
    return "task_id" in result and result["task_id"] == test_task_id

def run_all_tests():
    """
    Run all endpoint tests
    """
    logger.info("Starting API endpoint tests...")
    
    test_results = {
        "health": test_health_endpoint(),
        "echo": test_echo_endpoint(),
        "prompt_processing": test_prompt_processing(),
        "status": test_status_endpoint()
    }
    
    success_count = sum(1 for result in test_results.values() if result)
    total_count = len(test_results)
    
    logger.info(f"Test results: {test_results}")
    logger.info(f"Success rate: {success_count}/{total_count} tests passed")
    
    if success_count == total_count:
        logger.info("All tests passed! The API endpoints are working correctly.")
    else:
        logger.warning(f"Some tests failed. Please check the logs for details.")

if __name__ == "__main__":
    # Check if backend is running with improved connection check
    if not check_server_connection():
        sys.exit(1)
    
    # Run the tests
    run_all_tests()
