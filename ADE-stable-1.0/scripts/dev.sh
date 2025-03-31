#!/bin/bash

# Exit on error
set -e

# Load environment variables
if [ -f .env.development ]; then
    source .env.development
else
    echo "Error: .env.development file not found"
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for required commands
for cmd in docker docker-compose; do
    if ! command_exists "$cmd"; then
        echo "Error: $cmd is not installed"
        exit 1
    fi
done

# Create necessary directories
mkdir -p data/mongodb data/redis data/prometheus data/grafana

# Stop existing containers
echo "Stopping existing containers..."
docker-compose down --remove-orphans

# Build images
echo "Building Docker images..."
docker-compose build --no-cache

# Start services
echo "Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Check service health
echo "Checking service health..."
docker-compose ps

# Print access information
echo "
Local Development Environment is ready!

Access URLs:
- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090

Development Credentials:
- MongoDB: admin/dev_password_123
- Redis: dev_redis_password_123
- Grafana: admin/admin
- JWT Secret: dev_jwt_secret_123
- Encryption Key: dev_encryption_key_123

To view logs:
- API: docker-compose logs -f api
- MongoDB: docker-compose logs -f mongodb
- Redis: docker-compose logs -f redis
- Ollama: docker-compose logs -f ollama

To stop the environment:
- docker-compose down

To rebuild and restart:
- docker-compose down
- docker-compose build --no-cache
- docker-compose up -d
" 