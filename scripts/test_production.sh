#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check Docker
if ! command_exists docker; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check Docker Compose
if ! command_exists docker-compose; then
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Check if .env.production exists
if [ ! -f .env.production ]; then
    echo -e "${RED}.env.production file not found. Creating from .env.example...${NC}"
    cp .env.example .env.production
    echo -e "${YELLOW}Please update .env.production with your production values.${NC}"
    exit 1
fi

# Function to check service health
check_service_health() {
    local service=$1
    local url=$2
    local max_attempts=30
    local attempt=1

    echo -e "${YELLOW}Waiting for $service to be healthy...${NC}"
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" > /dev/null; then
            echo -e "${GREEN}$service is healthy!${NC}"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    echo -e "\n${RED}$service failed to become healthy${NC}"
    return 1
}

# Stop any existing containers
echo -e "${YELLOW}Stopping any existing containers...${NC}"
docker-compose -f docker-compose.prod.test.yml down -v

# Build and start services
echo -e "${YELLOW}Building and starting services...${NC}"
docker-compose -f docker-compose.prod.test.yml up --build -d

# Check service health
check_service_health "API" "http://localhost:8000/health" || exit 1
check_service_health "Frontend" "http://localhost:3000/health" || exit 1
check_service_health "MongoDB" "http://localhost:27017" || exit 1
check_service_health "Redis" "http://localhost:6379" || exit 1
check_service_health "Prometheus" "http://localhost:9090/-/healthy" || exit 1
check_service_health "Grafana" "http://localhost:3001/api/health" || exit 1

# Print service URLs
echo -e "\n${GREEN}Production test environment is ready!${NC}"
echo -e "Frontend: ${YELLOW}http://localhost:3000${NC}"
echo -e "API: ${YELLOW}http://localhost:8000${NC}"
echo -e "Grafana: ${YELLOW}http://localhost:3001${NC}"
echo -e "Prometheus: ${YELLOW}http://localhost:9090${NC}"

# Function to run performance tests
run_performance_tests() {
    echo -e "\n${YELLOW}Running performance tests...${NC}"
    python run_performance_tests.py
}

# Function to run security tests
run_security_tests() {
    echo -e "\n${YELLOW}Running security tests...${NC}"
    python -m pytest tests/security/ -v
}

# Ask user if they want to run tests
read -p "Do you want to run performance tests? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    run_performance_tests
fi

read -p "Do you want to run security tests? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    run_security_tests
fi

echo -e "\n${GREEN}Setup complete! You can now test the production environment locally.${NC}"
echo -e "To stop the environment, run: ${YELLOW}docker-compose -f docker-compose.prod.test.yml down${NC}" 