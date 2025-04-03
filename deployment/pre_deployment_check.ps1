# ADE Platform Pre-Deployment Check Script
# PowerShell Script

# Display banner
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "         ADE Platform Pre-Deployment Check            " -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

# Set error action preference
$ErrorActionPreference = "Stop"

# Initialize results tracking
$checksPassed = @()
$checksFailed = @()

# Function to check if a command exists
function Test-CommandExists {
    param (
        [string]$command
    )
    
    $exists = $null -ne (Get-Command $command -ErrorAction SilentlyContinue)
    return $exists
}

# Function to run a check and record the result
function Invoke-Check {
    param (
        [string]$Name,
        [scriptblock]$CheckScript
    )
    
    Write-Host "Checking $Name..." -ForegroundColor Yellow
    
    try {
        $result = & $CheckScript
        
        if ($result) {
            Write-Host "  - PASSED: $Name" -ForegroundColor Green
            $script:checksPassed += $Name
            return $true
        } else {
            Write-Host "  - FAILED: $Name" -ForegroundColor Red
            $script:checksFailed += $Name
            return $false
        }
    } catch {
        Write-Host "  - ERROR: $Name - $_" -ForegroundColor Red
        $script:checksFailed += "$Name (Error: $_)"
        return $false
    }
}

# Check for required tools
Invoke-Check -Name "Docker installation" -CheckScript {
    $dockerExists = Test-CommandExists -command "docker"
    if (-not $dockerExists) {
        Write-Host "  - Docker is not installed or not in PATH" -ForegroundColor Red
        return $false
    }
    
    # Check Docker is running
    try {
        docker info 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  - Docker is installed but not running" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "  - Failed to check Docker status: $_" -ForegroundColor Red
        return $false
    }
    
    return $true
}

Invoke-Check -Name "Docker Compose installation" -CheckScript {
    return (Test-CommandExists -command "docker-compose")
}

# Check if .env.cloud template exists
Invoke-Check -Name "Environment template" -CheckScript {
    return (Test-Path -Path ".env.cloud.template")
}

# Check if deployment scripts exist
Invoke-Check -Name "Deployment scripts" -CheckScript {
    $deployShExists = Test-Path -Path "deployment/deploy.sh"
    $deployPsExists = Test-Path -Path "deployment/deploy.ps1"
    
    return ($deployShExists -and $deployPsExists)
}

# Check for required files
Invoke-Check -Name "Docker configuration files" -CheckScript {
    $backendDockerfile = Test-Path -Path "Dockerfile.backend"
    $frontendDockerfile = Test-Path -Path "Dockerfile.frontend"
    $dockerComposeFile = Test-Path -Path "docker-compose.cloud.yml"
    $nginxConfig = Test-Path -Path "deployment/nginx.conf"
    
    $result = $backendDockerfile -and $frontendDockerfile -and $dockerComposeFile -and $nginxConfig
    
    if (-not $backendDockerfile) { Write-Host "  - Missing Dockerfile.backend" -ForegroundColor Red }
    if (-not $frontendDockerfile) { Write-Host "  - Missing Dockerfile.frontend" -ForegroundColor Red }
    if (-not $dockerComposeFile) { Write-Host "  - Missing docker-compose.cloud.yml" -ForegroundColor Red }
    if (-not $nginxConfig) { Write-Host "  - Missing deployment/nginx.conf" -ForegroundColor Red }
    
    return $result
}

# Check frontend readiness
Invoke-Check -Name "Frontend code check" -CheckScript {
    if (Test-Path -Path "scripts/fix_frontend_errors.ps1") {
        # Run the frontend error detection and fixing script
        & "scripts/fix_frontend_errors.ps1"
        return ($LASTEXITCODE -eq 0)
    } else {
        Write-Host "  - Frontend error fixing script not found" -ForegroundColor Yellow
        # Basic check for package.json and required files
        return (Test-Path -Path "frontend/package.json")
    }
}

# Check backend readiness
Invoke-Check -Name "Backend code check" -CheckScript {
    # Check for required backend files
    $appPyExists = Test-Path -Path "backend/app.py"
    $requirementsExists = Test-Path -Path "backend/requirements.txt"
    
    if (-not $appPyExists) { Write-Host "  - Missing backend/app.py" -ForegroundColor Red }
    if (-not $requirementsExists) { Write-Host "  - Missing backend/requirements.txt" -ForegroundColor Red }
    
    # If Python is installed, do a basic syntax check
    if (Test-CommandExists -command "python") {
        if ($appPyExists) {
            $syntaxCheck = python -m py_compile backend/app.py 2>&1
            if ($LASTEXITCODE -ne 0) {
                Write-Host "  - Python syntax error in app.py: $syntaxCheck" -ForegroundColor Red
                return $false
            }
        }
    } else {
        Write-Host "  - Python not found, skipping syntax check" -ForegroundColor Yellow
    }
    
    return ($appPyExists -and $requirementsExists)
}

# Check Agent Coordinator integration
Invoke-Check -Name "Agent Coordinator integration" -CheckScript {
    # Check if the agent coordinator file exists
    $agentCoordinatorExists = Test-Path -Path "backend/agents/agent_coordinator.py"
    $taskAllocatorExists = Test-Path -Path "backend/services/task_allocator.py"
    $agentCacheExists = Test-Path -Path "backend/services/agent_cache.py"
    
    if (-not $agentCoordinatorExists) { Write-Host "  - Missing agent_coordinator.py" -ForegroundColor Red }
    if (-not $taskAllocatorExists) { Write-Host "  - Missing task_allocator.py" -ForegroundColor Red }
    if (-not $agentCacheExists) { Write-Host "  - Missing agent_cache.py" -ForegroundColor Red }
    
    # Check for integration in agent_coordinator
    if ($agentCoordinatorExists) {
        $agentCoordinatorContent = Get-Content -Path "backend/agents/agent_coordinator.py" -Raw
        $hasTaskAllocator = $agentCoordinatorContent -match "task_allocator"
        $hasAgentCache = $agentCoordinatorContent -match "agent_cache"
        
        if (-not $hasTaskAllocator) { Write-Host "  - Task allocator not integrated in agent_coordinator.py" -ForegroundColor Red }
        if (-not $hasAgentCache) { Write-Host "  - Agent cache not integrated in agent_coordinator.py" -ForegroundColor Red }
        
        return ($hasTaskAllocator -and $hasAgentCache)
    }
    
    return $false
}

# Check integration test suite
Invoke-Check -Name "Integration test suite" -CheckScript {
    $backendTestExists = Test-Path -Path "tests/test_agent_integration.py"
    $frontendTestExists = Test-Path -Path "tests/test_frontend_agent_coordination.ts"
    $testRunnerExists = Test-Path -Path "tests/run_integration_tests.ps1"
    
    if (-not $backendTestExists) { Write-Host "  - Missing backend integration tests" -ForegroundColor Red }
    if (-not $frontendTestExists) { Write-Host "  - Missing frontend integration tests" -ForegroundColor Red }
    if (-not $testRunnerExists) { Write-Host "  - Missing test runner script" -ForegroundColor Red }
    
    return ($backendTestExists -and $frontendTestExists -and $testRunnerExists)
}

# Check for error logging integration
Invoke-Check -Name "Error logging system" -CheckScript {
    $errorLoggingExists = Test-Path -Path "scripts/basic_error_logging.py"
    
    if (-not $errorLoggingExists) {
        Write-Host "  - Missing error logging system" -ForegroundColor Red
        return $false
    }
    
    # Check for integration in agent_coordinator
    $agentCoordinatorContent = Get-Content -Path "backend/agents/agent_coordinator.py" -Raw -ErrorAction SilentlyContinue
    $hasErrorLogging = $agentCoordinatorContent -match "error_logging"
    
    if (-not $hasErrorLogging) {
        Write-Host "  - Error logging not integrated in agent_coordinator.py" -ForegroundColor Yellow
    }
    
    return $true
}

# Check disk space
Invoke-Check -Name "System resources" -CheckScript {
    $drive = Get-PSDrive -Name (Split-Path -Path (Get-Location) -Qualifier).TrimEnd(":")
    $freeSpaceGB = [Math]::Round($drive.Free / 1GB, 2)
    $requiredSpaceGB = 5
    
    if ($freeSpaceGB -lt $requiredSpaceGB) {
        Write-Host "  - Insufficient disk space: $freeSpaceGB GB free, $requiredSpaceGB GB required" -ForegroundColor Red
        return $false
    }
    
    Write-Host "  - $freeSpaceGB GB of free disk space available" -ForegroundColor Green
    return $true
}

# Summary
Write-Host ""
Write-Host "Pre-Deployment Check Summary:" -ForegroundColor Cyan
Write-Host "------------------------------" -ForegroundColor Cyan

if ($checksFailed.Count -eq 0) {
    Write-Host "All checks passed! The system is ready for deployment." -ForegroundColor Green
    
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Create a .env.cloud file from the template" -ForegroundColor Yellow
    Write-Host "2. Run the deployment script:" -ForegroundColor Yellow
    Write-Host "   .\deployment\deploy.ps1" -ForegroundColor Yellow
    
    exit 0
} else {
    Write-Host "Failed checks ($($checksFailed.Count)):" -ForegroundColor Red
    foreach ($check in $checksFailed) {
        Write-Host "  - $check" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "Passed checks ($($checksPassed.Count)):" -ForegroundColor Green
    foreach ($check in $checksPassed) {
        Write-Host "  - $check" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "Please fix the failed checks before proceeding with deployment." -ForegroundColor Yellow
    exit 1
}
