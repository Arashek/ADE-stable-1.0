import requests
import time
import sys
from typing import Dict, Any

def check_service(url: str, name: str) -> bool:
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Error checking {name}: {str(e)}")
        return False

def test_deployment() -> Dict[str, Any]:
    results = {
        "api": False,
        "grafana": False,
        "prometheus": False,
        "mongodb": False,
        "redis": False,
        "ollama": False
    }
    
    # Test API
    print("Testing API...")
    results["api"] = check_service("http://localhost:8000/health", "API")
    
    # Test Grafana
    print("Testing Grafana...")
    results["grafana"] = check_service("http://localhost:3000/api/health", "Grafana")
    
    # Test Prometheus
    print("Testing Prometheus...")
    results["prometheus"] = check_service("http://localhost:9090/-/healthy", "Prometheus")
    
    # Test MongoDB
    print("Testing MongoDB...")
    try:
        import pymongo
        client = pymongo.MongoClient("mongodb://admin:dev_password_123@localhost:27017/")
        client.server_info()
        results["mongodb"] = True
    except Exception as e:
        print(f"Error checking MongoDB: {str(e)}")
    
    # Test Redis
    print("Testing Redis...")
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, password='dev_redis_password_123')
        r.ping()
        results["redis"] = True
    except Exception as e:
        print(f"Error checking Redis: {str(e)}")
    
    # Test Ollama
    print("Testing Ollama...")
    results["ollama"] = check_service("http://localhost:11434/api/version", "Ollama")
    
    return results

def main():
    print("Starting deployment test...")
    print("Waiting for services to be ready...")
    time.sleep(10)  # Give services time to start
    
    results = test_deployment()
    
    print("\nTest Results:")
    print("-" * 50)
    for service, status in results.items():
        print(f"{service.upper()}: {'✓' if status else '✗'}")
    
    if all(results.values()):
        print("\nAll services are running correctly! ✓")
    else:
        print("\nSome services are not running correctly. Please check the logs.")
        sys.exit(1)

if __name__ == "__main__":
    main() 