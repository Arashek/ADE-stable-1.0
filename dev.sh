#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"
if ! command_exists docker; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command_exists docker-compose; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo -e "${BLUE}Creating necessary directories...${NC}"
mkdir -p Frontend Backend Model-Training output

# Build and start containers
echo -e "${BLUE}Building and starting containers...${NC}"
docker-compose -f docker-compose.dev.yml up --build -d

# Wait for services to be ready
echo -e "${BLUE}Waiting for services to be ready...${NC}"
sleep 10

# Check if services are running
echo -e "${BLUE}Checking service status...${NC}"
docker-compose -f docker-compose.dev.yml ps

# Print access information
echo -e "${GREEN}Development environment is ready!${NC}"
echo -e "Frontend: http://localhost:3000"
echo -e "Backend: http://localhost:5000"
echo -e "Metrics Visualizer: http://localhost:8080"

# Function to show logs
show_logs() {
    echo -e "${BLUE}Showing logs for $1...${NC}"
    docker-compose -f docker-compose.dev.yml logs -f $1
}

# Function to stop services
stop_services() {
    echo -e "${BLUE}Stopping services...${NC}"
    docker-compose -f docker-compose.dev.yml down
}

# Function to restart services
restart_services() {
    echo -e "${BLUE}Restarting services...${NC}"
    docker-compose -f docker-compose.dev.yml restart
}

# Function to rebuild services
rebuild_services() {
    echo -e "${BLUE}Rebuilding services...${NC}"
    docker-compose -f docker-compose.dev.yml up --build -d
}

# Print usage information
echo -e "\n${BLUE}Available commands:${NC}"
echo -e "  ./dev.sh logs [service]    - Show logs for a service"
echo -e "  ./dev.sh stop             - Stop all services"
echo -e "  ./dev.sh restart          - Restart all services"
echo -e "  ./dev.sh rebuild          - Rebuild all services"
echo -e "  ./dev.sh help             - Show this help message"

# Handle command line arguments
case "$1" in
    "logs")
        show_logs "$2"
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        restart_services
        ;;
    "rebuild")
        rebuild_services
        ;;
    "help"|"")
        echo -e "\n${BLUE}Usage:${NC}"
        echo -e "  ./dev.sh [command] [options]"
        ;;
    *)
        echo "Unknown command: $1"
        echo "Use ./dev.sh help for usage information"
        ;;
esac 