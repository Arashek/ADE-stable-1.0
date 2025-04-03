# Integration Tests Runner for ADE Platform
# PowerShell Script

# Display banner
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "      ADE Platform End-to-End Integration Tests       " -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

# Set error action preference
$ErrorActionPreference = "Stop"

# Create test results directory
$resultsDir = "test_results"
if (-not (Test-Path -Path $resultsDir)) {
    New-Item -Path $resultsDir -ItemType Directory | Out-Null
}

# Timestamp for test results
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backendResultsFile = "$resultsDir\backend_tests_$timestamp.log"
$frontendResultsFile = "$resultsDir\frontend_tests_$timestamp.log"

# Function to run tests and handle errors
function Invoke-TestSuite {
    param (
        [string]$Name,
        [string]$Command,
        [string]$LogFile
    )
    
    Write-Host "Running $Name integration tests..." -ForegroundColor Yellow
    
    try {
        # Run the command and capture output
        $output = Invoke-Expression $Command
        
        # Save output to log file
        $output | Out-File -FilePath $LogFile
        
        # Check for test failures
        if ($LASTEXITCODE -eq 0) {
            Write-Host "$Name tests completed successfully!" -ForegroundColor Green
            return $true
        } else {
            Write-Host "$Name tests failed with exit code $LASTEXITCODE" -ForegroundColor Red
            Write-Host "See $LogFile for details" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "Error running $Name tests: $_" -ForegroundColor Red
        "Error: $_" | Out-File -FilePath $LogFile -Append
        return $false
    }
}

# Function to check if required services are running
function Test-RequiredServices {
    # Check if backend is running
    try {
        $backendRunning = (Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -ErrorAction SilentlyContinue).StatusCode -eq 200
    } catch {
        $backendRunning = $false
    }
    
    if (-not $backendRunning) {
        Write-Host "Backend service is not running. Starting it..." -ForegroundColor Yellow
        Start-Process -FilePath "python" -ArgumentList "backend/app.py" -NoNewWindow
        
        # Wait for backend to start
        $attempts = 0
        $maxAttempts = 10
        while (-not $backendRunning -and $attempts -lt $maxAttempts) {
            Start-Sleep -Seconds 2
            $attempts++
            try {
                $backendRunning = (Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -ErrorAction SilentlyContinue).StatusCode -eq 200
            } catch {
                $backendRunning = $false
            }
        }
        
        if (-not $backendRunning) {
            Write-Host "Failed to start backend service. Tests cannot proceed." -ForegroundColor Red
            exit 1
        }
    }
}

# Main test execution
try {
    # Check for required services
    Test-RequiredServices
    
    Write-Host "Running Agent Integration Tests..." -ForegroundColor Cyan
    
    # Run backend integration tests
    $backendSuccess = Invoke-TestSuite -Name "Backend" -Command "python -m unittest tests/test_agent_integration.py" -LogFile $backendResultsFile
    
    # Run frontend integration tests
    $frontendSuccess = Invoke-TestSuite -Name "Frontend" -Command "cd frontend && npm test -- --testMatch='**/test_frontend_agent_coordination.ts'" -LogFile $frontendResultsFile
    
    # Summary
    Write-Host ""
    Write-Host "Test Results Summary:" -ForegroundColor Cyan
    Write-Host "---------------------" -ForegroundColor Cyan
    Write-Host "Backend Tests: $(if ($backendSuccess) { 'PASSED' } else { 'FAILED' })" -ForegroundColor $(if ($backendSuccess) { 'Green' } else { 'Red' })
    Write-Host "Frontend Tests: $(if ($frontendSuccess) { 'PASSED' } else { 'FAILED' })" -ForegroundColor $(if ($frontendSuccess) { 'Green' } else { 'Red' })
    Write-Host ""
    
    if ($backendSuccess -and $frontendSuccess) {
        Write-Host "All integration tests PASSED!" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "Some tests FAILED. Check the log files for details:" -ForegroundColor Red
        Write-Host "Backend: $backendResultsFile" -ForegroundColor Yellow
        Write-Host "Frontend: $frontendResultsFile" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "Error running integration tests: $_" -ForegroundColor Red
    exit 1
}
