# Exit on error
$ErrorActionPreference = "Stop"

# Load environment variables
if (Test-Path .env) {
    Get-Content .env | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $name = $matches[1]
            $value = $matches[2]
            Set-Item -Path "Env:$name" -Value $value
        }
    }
} else {
    Write-Error "Error: .env file not found"
    exit 1
}

# Check required environment variables
$requiredVars = @(
    "MONGODB_USER",
    "MONGODB_PASSWORD",
    "REDIS_PASSWORD",
    "JWT_SECRET"
)

foreach ($var in $requiredVars) {
    if (-not [System.Environment]::GetEnvironmentVariable($var)) {
        Write-Error "Error: $var is not set in .env file"
        exit 1
    }
}

# Create necessary directories
New-Item -ItemType Directory -Force -Path projects, static, visualizations, prometheus

# Build and start the containers
Write-Host "Building and starting containers..."
docker-compose build
docker-compose up -d

# Wait for services to be healthy
Write-Host "Waiting for services to be healthy..."
Start-Sleep -Seconds 10

# Check service health
Write-Host "Checking service health..."
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "Health check passed"
    } else {
        Write-Error "Health check failed"
        docker-compose logs api
        exit 1
    }
} catch {
    Write-Error "Health check failed: $_"
    docker-compose logs api
    exit 1
}

Write-Host "Deployment completed successfully!"
Write-Host "API is available at http://localhost:8000"
Write-Host "Grafana is available at http://localhost:3000"
Write-Host "Prometheus is available at http://localhost:9090" 