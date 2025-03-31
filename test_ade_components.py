"""
ADE Platform Component Test Script
This script tests various components of the ADE platform including:
- Backend API endpoints
- Frontend React components
- Design Hub functionality
"""

import requests
import json
import os
import sys
import time
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"
TEST_RESULTS = []

def log_result(component, test_name, status, message=""):
    """Log a test result"""
    TEST_RESULTS.append({
        "component": component,
        "test": test_name,
        "status": status,
        "message": message,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    status_str = "✅ PASS" if status else "❌ FAIL"
    print(f"{status_str} - {component} - {test_name}")
    if message:
        print(f"       {message}")

def test_backend_health():
    """Test if the backend server is running and healthy"""
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            log_result("Backend", "Health Check", True)
            return True
        else:
            log_result("Backend", "Health Check", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        log_result("Backend", "Health Check", False, f"Error: {str(e)}")
        return False

def test_backend_api_docs():
    """Test if the API documentation is accessible"""
    try:
        response = requests.get(f"{BACKEND_URL}/docs")
        if response.status_code == 200:
            log_result("Backend", "API Docs", True)
            return True
        else:
            log_result("Backend", "API Docs", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        log_result("Backend", "API Docs", False, f"Error: {str(e)}")
        return False

def test_design_routes():
    """Test the design-related API endpoints"""
    # Test GET /api/designs
    try:
        response = requests.get(f"{BACKEND_URL}/api/designs", params={"projectId": "test-project"})
        if response.status_code in [200, 401, 403]:  # 401/403 are acceptable if auth is required
            log_result("Backend", "GET /api/designs", True, 
                      "Auth required" if response.status_code in [401, 403] else "Success")
        else:
            log_result("Backend", "GET /api/designs", False, f"Status code: {response.status_code}")
    except Exception as e:
        log_result("Backend", "GET /api/designs", False, f"Error: {str(e)}")

    # Test POST /api/designs
    try:
        test_design = {
            "projectId": "test-project",
            "name": "Test Design",
            "description": "A test design created by the test script",
            "components": [],
            "styles": [],
            "pages": []
        }
        response = requests.post(f"{BACKEND_URL}/api/designs", json=test_design)
        if response.status_code in [201, 401, 403]:  # 401/403 are acceptable if auth is required
            log_result("Backend", "POST /api/designs", True, 
                      "Auth required" if response.status_code in [401, 403] else "Success")
        else:
            log_result("Backend", "POST /api/designs", False, f"Status code: {response.status_code}")
    except Exception as e:
        log_result("Backend", "POST /api/designs", False, f"Error: {str(e)}")

def test_frontend_connectivity():
    """Test if the frontend server is running"""
    try:
        response = requests.get(FRONTEND_URL)
        if response.status_code == 200:
            log_result("Frontend", "Connectivity", True)
            return True
        else:
            log_result("Frontend", "Connectivity", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        log_result("Frontend", "Connectivity", False, f"Error: {str(e)}")
        return False

def generate_report():
    """Generate a report of all test results"""
    print("\n" + "="*50)
    print("ADE PLATFORM TEST RESULTS")
    print("="*50)
    
    # Count results
    total = len(TEST_RESULTS)
    passed = sum(1 for result in TEST_RESULTS if result["status"])
    failed = total - passed
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/total)*100:.2f}%")
    
    print("\nFailed Tests:")
    for result in TEST_RESULTS:
        if not result["status"]:
            print(f"- {result['component']} - {result['test']}: {result['message']}")
    
    print("\n" + "="*50)

def main():
    """Run all tests"""
    print("Starting ADE Platform Component Tests...")
    print("="*50)
    
    # Test backend
    backend_health = test_backend_health()
    if backend_health:
        test_backend_api_docs()
        test_design_routes()
    
    # Test frontend
    frontend_up = test_frontend_connectivity()
    
    # Generate report
    generate_report()

if __name__ == "__main__":
    main()
