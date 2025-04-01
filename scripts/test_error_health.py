#!/usr/bin/env python
"""
Test Script for Error Logging Health Endpoint

This script tests the health check endpoint for the error logging system
to verify that our routes are properly registered and accessible.
"""

import sys
import requests
import json
from datetime import datetime

# Constants
BACKEND_URL = "http://localhost:8000"
HEALTH_ENDPOINT = f"{BACKEND_URL}/error-logging/health"

def test_health_endpoint():
    """Test the health check endpoint"""
    print(f"Testing error logging health endpoint: {HEALTH_ENDPOINT}")
    
    try:
        response = requests.get(HEALTH_ENDPOINT)
        
        if response.status_code == 200:
            print(f"✅ Success! Status code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"❌ Failed. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        return False

if __name__ == "__main__":
    print(f"==== Error Logging Health Check Test ====")
    print(f"Time: {datetime.now().isoformat()}")
    print(f"======================================")
    
    success = test_health_endpoint()
    
    if success:
        print(f"\n✅ Health check test PASSED!")
        sys.exit(0)
    else:
        print(f"\n❌ Health check test FAILED!")
        sys.exit(1)
