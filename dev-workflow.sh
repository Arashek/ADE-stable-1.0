#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a service is running
service_running() {
    docker-compose -f docker-compose.dev.yml ps $1 | grep -q "Up"
}

# Function to wait for a service to be ready
wait_for_service() {
    echo -e "${BLUE}Waiting for $1 to be ready...${NC}"
    while ! service_running $1; do
        sleep 2
    done
    echo -e "${GREEN}$1 is ready!${NC}"
}

# Function to run tests
run_tests() {
    echo -e "${BLUE}Running tests...${NC}"
    docker-compose -f docker-compose.dev.yml run --rm model-training pytest tests/ -v
}

# Function to check code style
check_style() {
    echo -e "${BLUE}Checking code style...${NC}"
    docker-compose -f docker-compose.dev.yml run --rm backend flake8 .
    docker-compose -f docker-compose.dev.yml run --rm frontend npm run lint
}

# Function to generate documentation
generate_docs() {
    echo -e "${BLUE}Generating documentation...${NC}"
    docker-compose -f docker-compose.dev.yml run --rm backend sphinx-build -b html docs/source docs/build
}

# Function to analyze code metrics
analyze_metrics() {
    echo -e "${BLUE}Analyzing code metrics...${NC}"
    docker-compose -f docker-compose.dev.yml run --rm model-training python -m src.refactoring.metrics_analyzer
}

# Function to start debugging session
start_debugging() {
    echo -e "${BLUE}Starting debugging session...${NC}"
    echo -e "${YELLOW}Frontend debugging available at: http://localhost:9229${NC}"
    echo -e "${YELLOW}Backend debugging available at: http://localhost:5678${NC}"
    echo -e "${YELLOW}Use Chrome DevTools or VS Code to connect to these ports${NC}"
}

# Function to monitor logs
monitor_logs() {
    echo -e "${BLUE}Monitoring logs...${NC}"
    docker-compose -f docker-compose.dev.yml logs -f
}

# Function to check system health
check_health() {
    echo -e "${BLUE}Checking system health...${NC}"
    
    # Check services
    echo -e "\n${YELLOW}Service Status:${NC}"
    docker-compose -f docker-compose.dev.yml ps
    
    # Check resources
    echo -e "\n${YELLOW}Resource Usage:${NC}"
    docker stats --no-stream
    
    # Check logs for errors
    echo -e "\n${YELLOW}Recent Errors:${NC}"
    docker-compose -f docker-compose.dev.yml logs --tail=100 | grep -i error
}

# Function to backup data
backup_data() {
    echo -e "${BLUE}Creating backup...${NC}"
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_dir="backups/$timestamp"
    
    mkdir -p $backup_dir
    
    # Backup volumes
    docker-compose -f docker-compose.dev.yml down
    docker run --rm -v ade-platform_postgres_data:/source -v $(pwd)/$backup_dir:/backup alpine tar czf /backup/postgres.tar.gz -C /source .
    docker-compose -f docker-compose.dev.yml up -d
}

# Function to restore data
restore_data() {
    if [ -z "$1" ]; then
        echo -e "${RED}Please specify backup directory${NC}"
        return 1
    fi
    
    echo -e "${BLUE}Restoring from backup...${NC}"
    docker-compose -f docker-compose.dev.yml down
    docker run --rm -v ade-platform_postgres_data:/target -v $(pwd)/$1:/backup alpine sh -c "cd /target && tar xzf /backup/postgres.tar.gz"
    docker-compose -f docker-compose.dev.yml up -d
}

# Function to show available commands
show_help() {
    echo -e "${BLUE}Available commands:${NC}"
    echo -e "  ./dev-workflow.sh test              - Run tests"
    echo -e "  ./dev-workflow.sh style             - Check code style"
    echo -e "  ./dev-workflow.sh docs              - Generate documentation"
    echo -e "  ./dev-workflow.sh metrics           - Analyze code metrics"
    echo -e "  ./dev-workflow.sh debug             - Start debugging session"
    echo -e "  ./dev-workflow.sh logs              - Monitor logs"
    echo -e "  ./dev-workflow.sh health            - Check system health"
    echo -e "  ./dev-workflow.sh backup            - Create backup"
    echo -e "  ./dev-workflow.sh restore <dir>     - Restore from backup"
    echo -e "  ./dev-workflow.sh help              - Show this help message"
}

# Handle command line arguments
case "$1" in
    "test")
        run_tests
        ;;
    "style")
        check_style
        ;;
    "docs")
        generate_docs
        ;;
    "metrics")
        analyze_metrics
        ;;
    "debug")
        start_debugging
        ;;
    "logs")
        monitor_logs
        ;;
    "health")
        check_health
        ;;
    "backup")
        backup_data
        ;;
    "restore")
        restore_data "$2"
        ;;
    "help"|"")
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        show_help
        exit 1
        ;;
esac 