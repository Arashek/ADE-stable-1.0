# API Gateway

A comprehensive API Gateway implementation with advanced features for request handling, transformation, and monitoring.

## Features

### 1. Request Handling
- Route management
- Request/response transformation
- Authentication and authorization
- Rate limiting
- Circuit breaking
- Load balancing

### 2. Monitoring and Observability
- Prometheus metrics integration
- Distributed tracing with OpenTelemetry
- Audit logging
- Health checks
- Performance monitoring

### 3. Security
- JWT authentication
- Rate limiting
- Circuit breaker
- Request validation
- IP filtering
- CORS support

### 4. Traffic Management
- Adaptive load balancing
- Request prioritization
- Rate limiting per user tier
- Circuit breaker with fallback
- Request/response transformation

## Components

### 1. Core Gateway (`api_gateway.py`)
Main gateway implementation with request handling and routing.

### 2. Rate Limiting (`rate_limiting.py`)
Configurable rate limiting based on user tiers and endpoints.

### 3. Service Discovery (`service_discovery.py`)
Service registration and discovery with health checks.

### 4. Monitoring Integration
- Audit logging
- Metrics collection
- Distributed tracing
- Alert management

## Configuration

### 1. Routes (`routes.yaml`)
```yaml
- path: "/api/v1/users"
  method: "GET"
  service: "user_service"
  auth_required: true
  rate_limit: 100
  timeout: 30.0
  retry_count: 3
```

### 2. Services (`services.yaml`)
```yaml
- name: "user_service"
  version: "1.0.0"
  base_url: "http://user-service:8080"
  timeout: 30.0
  retry_count: 3
  metadata:
    region: "us-east"
    environment: "production"
```

### 3. Transformations (`transforms.yaml`)
```yaml
- name: "user_response_transform"
  condition:
    path: "/api/v1/users/*"
    method: "GET"
  response_transform:
    jsonpath:
      "user_id": "$.id"
      "email": "$.email"
    template:
      "full_name": "{{ first_name }} {{ last_name }}"
```

## Usage

### 1. Initialize Gateway
```python
from api_gateway import APIGateway

gateway = APIGateway(
    config_dir="config",
    elasticsearch_url="http://localhost:9200",
    redis_url="redis://localhost:6379",
    jwt_secret="your-secret-key"
)
```

### 2. Handle Request
```python
response = await gateway.handle_request(
    request={
        "method": "GET",
        "path": "/api/v1/users",
        "headers": {
            "Authorization": "Bearer token"
        }
    },
    context={
        "user_id": "user123",
        "ip_address": "192.168.1.1"
    }
)
```

### 3. Update Configuration
```python
await gateway.update_config(
    config_type="routes",
    config_data=[
        {
            "path": "/api/v1/users",
            "method": "GET",
            "service": "user_service"
        }
    ]
)
```

## Monitoring

### 1. Metrics
- Request count
- Request latency
- Error rate
- Active connections
- Circuit breaker state

### 2. Tracing
- Request flow
- Service dependencies
- Performance bottlenecks
- Error tracking

### 3. Audit Logging
- Authentication events
- Data access
- Configuration changes
- Security events

## Rate Limiting

### 1. User Tiers
- FREE: 60 requests/minute
- BASIC: 300 requests/minute
- PRO: 1000 requests/minute
- ENTERPRISE: Custom limits

### 2. Configuration
```python
rate_limiter = RateLimiter(
    redis_url="redis://localhost:6379",
    tiers={
        "FREE": {"requests_per_minute": 60},
        "BASIC": {"requests_per_minute": 300},
        "PRO": {"requests_per_minute": 1000}
    }
)
```

## Circuit Breaker

### 1. States
- CLOSED: Normal operation
- OPEN: Failing, using fallback
- HALF-OPEN: Testing recovery

### 2. Configuration
```python
circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    reset_timeout=60,
    fallback_response={
        "error": "Service temporarily unavailable"
    }
)
```

## Load Balancing

### 1. Strategies
- Round Robin
- Least Connections
- Weighted Round Robin
- Adaptive (based on performance)

### 2. Configuration
```python
load_balancer = LoadBalancer(
    strategy="adaptive",
    health_check_interval=30,
    metrics_window=300
)
```

## Security

### 1. Authentication
- JWT validation
- Token refresh
- Role-based access
- Session management

### 2. Rate Limiting
- Per user limits
- Per endpoint limits
- Burst handling
- Custom rules

## Development

### 1. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/

# Start gateway
python -m src.core.gateway
```

### 2. Testing
```python
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Load tests
pytest tests/load/
```

## Deployment

### 1. Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

CMD ["python", "-m", "src.core.gateway"]
```

### 2. Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: api-gateway
        image: api-gateway:latest
        ports:
        - containerPort: 8000
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 