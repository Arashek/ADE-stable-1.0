#!/bin/bash

# Set default environment
ENV=${1:-development}
COMMAND=${2:-up}

# Validate environment
if [[ ! "$ENV" =~ ^(development|testing|production)$ ]]; then
    echo "Invalid environment. Use: development, testing, or production"
    exit 1
fi

# Validate command
if [[ ! "$COMMAND" =~ ^(up|down|build|test|logs|status)$ ]]; then
    echo "Invalid command. Use: up, down, build, test, logs, or status"
    exit 1
fi

# Set environment-specific variables
COMPOSE_FILE="environments/$ENV/docker-compose.yml"
ENV_FILE="environments/$ENV/.env"

# Check if environment files exist
if [ ! -f "$COMPOSE_FILE" ]; then
    echo "Error: Docker Compose file not found at $COMPOSE_FILE"
    exit 1
fi

# Function to run pre-build checks
run_prebuild_checks() {
    echo "Running pre-build checks for $ENV environment..."
    
    # Check for required files
    for file in "requirements.txt" "pyproject.toml" "setup.py"; do
        if [ ! -f "$file" ]; then
            echo "Error: Required file $file not found"
            exit 1
        fi
    done
    
    # Run linting if in development or testing
    if [[ "$ENV" =~ ^(development|testing)$ ]]; then
        echo "Running linting checks..."
        python -m pylint src/ tests/ || true
    fi
}

# Function to run post-build verification
run_postbuild_verification() {
    echo "Running post-build verification for $ENV environment..."
    
    # Wait for services to be ready
    sleep 5
    
    # Check API health
    if [[ "$ENV" == "production" ]]; then
        curl -f http://localhost/health || echo "Warning: API health check failed"
    else
        curl -f http://localhost:8000/health || echo "Warning: API health check failed"
    fi
}

# Main workflow
case $COMMAND in
    "up")
        run_prebuild_checks
        docker-compose -f $COMPOSE_FILE up -d
        run_postbuild_verification
        ;;
    "down")
        docker-compose -f $COMPOSE_FILE down
        ;;
    "build")
        run_prebuild_checks
        docker-compose -f $COMPOSE_FILE build
        ;;
    "test")
        if [[ "$ENV" == "testing" ]]; then
            docker-compose -f $COMPOSE_FILE run integration-tests
            docker-compose -f $COMPOSE_FILE run performance-tests
        else
            echo "Tests can only be run in testing environment"
            exit 1
        fi
        ;;
    "logs")
        docker-compose -f $COMPOSE_FILE logs -f
        ;;
    "status")
        docker-compose -f $COMPOSE_FILE ps
        ;;
esac 