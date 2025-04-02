# ADE Platform Cloud Deployment Script for Windows
# PowerShell Script

# Display banner
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "         ADE Platform Cloud Deployment Script         " -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env.cloud file exists
if (-not (Test-Path -Path ".env.cloud")) {
    Write-Host "Error: .env.cloud file not found!" -ForegroundColor Red
    Write-Host "Please create one from the template (.env.cloud.template)" -ForegroundColor Yellow
    exit 1
}

# Load environment variables
$envContent = Get-Content ".env.cloud"
$envVars = @{}

foreach ($line in $envContent) {
    if (-not [string]::IsNullOrWhiteSpace($line) -and -not $line.StartsWith('#')) {
        $key, $value = $line -split '=', 2
        $envVars[$key] = $value
    }
}

# Validate required environment variables
$requiredVars = @(
    "MONGODB_USER", 
    "MONGODB_PASSWORD", 
    "REDIS_PASSWORD", 
    "JWT_SECRET", 
    "OPENAI_API_KEY"
)

$missingVars = $false
foreach ($var in $requiredVars) {
    if (-not $envVars.ContainsKey($var) -or [string]::IsNullOrWhiteSpace($envVars[$var])) {
        Write-Host "Error: $var is not set in .env.cloud file" -ForegroundColor Red
        $missingVars = $true
    }
}

if ($missingVars) {
    exit 1
}

Write-Host "Environment validation successful!" -ForegroundColor Green

# Build and start containers
Write-Host "Building and starting containers..." -ForegroundColor Cyan
docker-compose -f docker-compose.cloud.yml up -d --build

# Check if containers are running
Write-Host "Checking container status..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

$containers = @("ade-frontend", "ade-backend", "ade-redis", "ade-mongodb", "ade-ollama")
$allRunning = $true

foreach ($container in $containers) {
    $status = docker container inspect -f "{{.State.Status}}" $container 2>$null
    
    if ($status -ne "running") {
        $allRunning = $false
        Write-Host "Error: Container $container is not running" -ForegroundColor Red
    }
}

if ($allRunning) {
    Write-Host "All containers are running successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "ADE Platform is now deployed and accessible at:" -ForegroundColor Green
    Write-Host "- Frontend: https://cloudev.ai" -ForegroundColor Green
    Write-Host "- Backend API: https://cloudev.ai/api" -ForegroundColor Green
    Write-Host ""
    Write-Host "Deployment completed successfully!" -ForegroundColor Green
} else {
    Write-Host "Error: Some containers are not running. Please check the logs for more information:" -ForegroundColor Red
    Write-Host "docker-compose -f docker-compose.cloud.yml logs" -ForegroundColor Yellow
    exit 1
}
