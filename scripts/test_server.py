"""
Simple script to test if the backend server is responding to requests.
"""
import requests
import sys

def test_endpoints():
    """Test various endpoints to see if the server is responding"""
    endpoints = [
        "http://localhost:8000/",
        "http://localhost:8000/api/health",
        "http://localhost:8000/docs",  # Swagger UI
        "http://localhost:8000/api",
        "http://localhost:8000/error-logging/health"
    ]
    
    print("Testing backend server connectivity...")
    print("-" * 50)
    
    success = False
    for endpoint in endpoints:
        print(f"Trying: {endpoint}")
        try:
            response = requests.get(endpoint, timeout=3)
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text[:100]}...")
            success = True
            break
        except requests.exceptions.RequestException as e:
            print(f"  Error: {str(e)}")
    
    if success:
        print("\n✅ Backend server is responding!")
        sys.exit(0)
    else:
        print("\n❌ Could not connect to backend server.")
        print("The server might not be fully initialized or there may be an error.")
        sys.exit(1)

if __name__ == "__main__":
    test_endpoints()
