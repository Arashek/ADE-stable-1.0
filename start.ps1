# Check for required API keys
$requiredKeys = @(
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "MISTRAL_API_KEY"
)

$missingKeys = @()
foreach ($key in $requiredKeys) {
    if (-not [System.Environment]::GetEnvironmentVariable($key)) {
        $missingKeys += $key
    }
}

if ($missingKeys.Count -gt 0) {
    Write-Host "Error: Missing required API keys. Please set the following environment variables:"
    foreach ($key in $missingKeys) {
        Write-Host "- $key"
    }
    Write-Host "`nYou can set these in the .env file or as environment variables."
    exit 1
}

# Build and start the containers
Write-Host "Building and starting ADE containers..."
docker-compose up --build -d

# Wait for services to be ready
Write-Host "Waiting for services to initialize..."
Start-Sleep -Seconds 10

# Check if services are running
$services = @("backend", "frontend", "redis", "prometheus", "grafana")
foreach ($service in $services) {
    $container = docker-compose ps $service -q
    if ($container) {
        Write-Host "$service is running"
    } else {
        Write-Host "Error: $service failed to start"
        exit 1
    }
}

Write-Host "ADE system is ready!"
Write-Host "Frontend: http://localhost:3000"
Write-Host "Backend API: http://localhost:8000"
Write-Host "Grafana: http://localhost:3001 (admin/admin)"
Write-Host "Prometheus: http://localhost:9090" 