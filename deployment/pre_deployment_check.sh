#!/bin/bash

# ADE Platform Pre-Deployment Check Script

# Display banner
echo "======================================================"
echo "         ADE Platform Pre-Deployment Check            "
echo "======================================================"
echo ""

# Initialize results tracking
CHECKS_PASSED=()
CHECKS_FAILED=()

# Function to run a check and record the result
run_check() {
    local name=$1
    local command=$2
    
    echo "Checking $name..."
    
    if eval "$command"; then
        echo "  - PASSED: $name"
        CHECKS_PASSED+=("$name")
        return 0
    else
        echo "  - FAILED: $name"
        CHECKS_FAILED+=("$name")
        return 1
    fi
}

# Check for required tools
run_check "Docker installation" "
    if ! command -v docker &> /dev/null; then
        echo '  - Docker is not installed or not in PATH'
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        echo '  - Docker is installed but not running'
        exit 1
    fi
    
    exit 0
"

run_check "Docker Compose installation" "command -v docker-compose &> /dev/null"

# Check if .env.cloud template exists
run_check "Environment template" "test -f .env.cloud.template"

# Check if deployment scripts exist
run_check "Deployment scripts" "test -f deployment/deploy.sh && test -f deployment/deploy.ps1"

# Check for required files
run_check "Docker configuration files" "
    missing_files=()
    
    if [ ! -f Dockerfile.backend ]; then
        echo '  - Missing Dockerfile.backend'
        missing_files+=(Dockerfile.backend)
    fi
    
    if [ ! -f Dockerfile.frontend ]; then
        echo '  - Missing Dockerfile.frontend'
        missing_files+=(Dockerfile.frontend)
    fi
    
    if [ ! -f docker-compose.cloud.yml ]; then
        echo '  - Missing docker-compose.cloud.yml'
        missing_files+=(docker-compose.cloud.yml)
    fi
    
    if [ ! -f deployment/nginx.conf ]; then
        echo '  - Missing deployment/nginx.conf'
        missing_files+=(deployment/nginx.conf)
    fi
    
    if [ \${#missing_files[@]} -eq 0 ]; then
        exit 0
    else
        exit 1
    fi
"

# Check frontend readiness
run_check "Frontend code check" "test -f frontend/package.json"

# Check backend readiness
run_check "Backend code check" "
    if [ ! -f backend/app.py ]; then
        echo '  - Missing backend/app.py'
        exit 1
    fi
    
    if [ ! -f backend/requirements.txt ]; then
        echo '  - Missing backend/requirements.txt'
        exit 1
    fi
    
    if command -v python3 &> /dev/null; then
        if ! python3 -m py_compile backend/app.py &> /dev/null; then
            echo '  - Python syntax error in app.py'
            exit 1
        fi
    else
        echo '  - Python not found, skipping syntax check'
    fi
    
    exit 0
"

# Check Agent Coordinator integration
run_check "Agent Coordinator integration" "
    if [ ! -f backend/agents/agent_coordinator.py ]; then
        echo '  - Missing agent_coordinator.py'
        exit 1
    fi
    
    if [ ! -f backend/services/task_allocator.py ]; then
        echo '  - Missing task_allocator.py'
        exit 1
    fi
    
    if [ ! -f backend/services/agent_cache.py ]; then
        echo '  - Missing agent_cache.py'
        exit 1
    fi
    
    if ! grep -q 'task_allocator' backend/agents/agent_coordinator.py; then
        echo '  - Task allocator not integrated in agent_coordinator.py'
        exit 1
    fi
    
    if ! grep -q 'agent_cache' backend/agents/agent_coordinator.py; then
        echo '  - Agent cache not integrated in agent_coordinator.py'
        exit 1
    fi
    
    exit 0
"

# Check integration test suite
run_check "Integration test suite" "
    if [ ! -f tests/test_agent_integration.py ]; then
        echo '  - Missing backend integration tests'
        exit 1
    fi
    
    if [ ! -f tests/test_frontend_agent_coordination.ts ]; then
        echo '  - Missing frontend integration tests'
        exit 1
    fi
    
    if [ ! -f tests/run_integration_tests.ps1 ]; then
        echo '  - Missing test runner script'
        exit 1
    fi
    
    exit 0
"

# Check for error logging integration
run_check "Error logging system" "
    if [ ! -f scripts/basic_error_logging.py ]; then
        echo '  - Missing error logging system'
        exit 1
    fi
    
    if ! grep -q 'error_logging' backend/agents/agent_coordinator.py 2>/dev/null; then
        echo '  - Error logging not integrated in agent_coordinator.py'
    fi
    
    exit 0
"

# Check disk space
run_check "System resources" "
    free_space=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    required_space=5
    
    if [ \$free_space -lt \$required_space ]; then
        echo \"  - Insufficient disk space: \${free_space}GB free, \${required_space}GB required\"
        exit 1
    fi
    
    echo \"  - \${free_space}GB of free disk space available\"
    exit 0
"

# Summary
echo ""
echo "Pre-Deployment Check Summary:"
echo "------------------------------"

if [ ${#CHECKS_FAILED[@]} -eq 0 ]; then
    echo "All checks passed! The system is ready for deployment."
    
    echo ""
    echo "Next steps:"
    echo "1. Create a .env.cloud file from the template"
    echo "2. Run the deployment script:"
    echo "   ./deployment/deploy.sh"
    
    exit 0
else
    echo "Failed checks (${#CHECKS_FAILED[@]}):"
    for check in "${CHECKS_FAILED[@]}"; do
        echo "  - $check"
    done
    
    echo ""
    echo "Passed checks (${#CHECKS_PASSED[@]}):"
    for check in "${CHECKS_PASSED[@]}"; do
        echo "  - $check"
    done
    
    echo ""
    echo "Please fix the failed checks before proceeding with deployment."
    exit 1
fi
