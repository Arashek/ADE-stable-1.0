from typing import Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Server configuration
SERVER_URL = os.getenv('TEST_SERVER_URL', 'http://localhost:8000')

# Test user credentials
TEST_USER = {
    'username': os.getenv('TEST_USERNAME', 'test_user'),
    'password': os.getenv('TEST_PASSWORD', 'test_password')
}

# Timeout settings (in seconds)
TIMEOUTS = {
    'request': 30,
    'long_request': 60,
    'condition': 120,
    'setup': 300
}

# Test case parameters
TEST_PARAMS = {
    'max_response_time': 2.0,  # Maximum acceptable response time in seconds
    'retry_attempts': 3,       # Number of retry attempts for failed requests
    'concurrent_users': 10,    # Number of concurrent users for load tests
    'test_duration': 3600,     # Duration of long-running tests in seconds
}

# MongoDB configuration
MONGODB_CONFIG = {
    'uri': os.getenv('TEST_MONGODB_URI', 'mongodb://localhost:27017'),
    'database': os.getenv('TEST_MONGODB_DB', 'ade_test_db')
}

# AI Provider configuration
AI_PROVIDER_CONFIG = {
    'api_key': os.getenv('TEST_AI_API_KEY', ''),
    'model': os.getenv('TEST_AI_MODEL', 'gpt-4'),
    'max_tokens': 2000,
    'temperature': 0.7
}

# Orchestrator settings
ORCHESTRATOR_CONFIG = {
    'max_concurrent_tasks': 5,
    'task_timeout': 300,
    'retry_interval': 5
}

# Agent system configuration
AGENT_CONFIG = {
    'max_agents': 3,
    'agent_timeout': 600,
    'memory_limit': 1000
}

def get_config() -> Dict[str, Any]:
    """Get the complete configuration dictionary."""
    return {
        'server_url': SERVER_URL,
        'test_user': TEST_USER,
        'timeouts': TIMEOUTS,
        'test_params': TEST_PARAMS,
        'mongodb': MONGODB_CONFIG,
        'ai_provider': AI_PROVIDER_CONFIG,
        'orchestrator': ORCHESTRATOR_CONFIG,
        'agent': AGENT_CONFIG
    } 