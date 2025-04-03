#!/bin/bash

# ADE Platform Cloud Deployment Script
set -e

# Display banner
echo "======================================================"
echo "         ADE Platform Cloud Deployment Script         "
echo "======================================================"
echo ""

# Run pre-deployment checks first
echo "Running pre-deployment checks..."
chmod +x ./deployment/pre_deployment_check.sh
./deployment/pre_deployment_check.sh
if [ $? -ne 0 ]; then
    echo "Pre-deployment checks failed. Please fix the issues before proceeding."
    exit 1
fi

echo "Pre-deployment checks passed. Continuing with deployment..."
echo ""

# Check if .env.cloud file exists
if [ ! -f ".env.cloud" ]; then
    echo "Error: .env.cloud file not found!"
    echo "Please create one from the template (.env.cloud.template)"
    exit 1
fi

# Load environment variables
source .env.cloud

# Validate required environment variables
required_vars=(
    "MONGODB_USER" 
    "MONGODB_PASSWORD" 
    "REDIS_PASSWORD" 
    "JWT_SECRET" 
    "OPENAI_API_KEY"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: $var is not set in .env.cloud file"
        exit 1
    fi
done

echo "Environment validation successful!"

# Build and start containers
echo "Building and starting containers..."
docker-compose -f docker-compose.cloud.yml up -d --build

# Check if containers are running
echo "Checking container status..."
sleep 10

containers=("ade-frontend" "ade-backend" "ade-redis" "ade-mongodb" "ade-ollama")
all_running=true

for container in "${containers[@]}"; do
    status=$(docker container inspect -f '{{.State.Status}}' "$container" 2>/dev/null || echo "not_found")
    
    if [ "$status" != "running" ]; then
        all_running=false
        echo "Error: Container $container is not running"
    fi
done

if [ "$all_running" = true ]; then
    echo "All containers are running successfully!"
    echo ""
    echo "ADE Platform is now deployed and accessible at:"
    echo "- Frontend: https://cloudev.ai"
    echo "- Backend API: https://cloudev.ai/api"
    echo ""
    echo "Deployment completed successfully!"
else
    echo "Error: Some containers are not running. Please check the logs for more information:"
    echo "docker-compose -f docker-compose.cloud.yml logs"
    exit 1
fi
