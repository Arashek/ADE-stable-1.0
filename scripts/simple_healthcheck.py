import requests
import sys
import socket

def check_port_open(port):
    """Check if a port is open on localhost"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(('localhost', port))
        s.close()
        return True
    except:
        return False

def main():
    """Test if the backend server is responding"""
    print("Simple healthcheck for ADE backend")
    print("-" * 50)
    
    # Check if port is open
    port = 8000
    if check_port_open(port):
        print(f"✓ Port {port} is open")
    else:
        print(f"✗ Port {port} is not open")
        print("  The server might not be running")
        sys.exit(1)
    
    # Try to connect to the health endpoint
    try:
        print(f"Trying to connect to http://localhost:{port}/health")
        response = requests.get(f"http://localhost:{port}/health", timeout=5)
        print(f"✓ Got response: {response.status_code}")
        print(f"✓ Response data: {response.text}")
    except Exception as e:
        print(f"✗ Error connecting to server: {type(e).__name__}: {str(e)}")
        
if __name__ == "__main__":
    main()
