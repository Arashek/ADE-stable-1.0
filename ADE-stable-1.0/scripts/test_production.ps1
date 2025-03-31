# Function to check if a command exists
function Test-Command {
    param ($Command)
    return [bool](Get-Command -Name $Command -ErrorAction SilentlyContinue)
}

# Function to check service health
function Test-ServiceHealth {
    param (
        [string]$Service,
        [string]$Url,
        [int]$MaxAttempts = 30
    )
    
    Write-Host "Waiting for $Service to be healthy..." -ForegroundColor Yellow
    $attempt = 1
    
    while ($attempt -le $MaxAttempts) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Host "$Service is healthy!" -ForegroundColor Green
                return $true
            }
        }
        catch {
            Write-Host "." -NoNewline
            Start-Sleep -Seconds 2
            $attempt++
        }
    }
    
    Write-Host "`n$Service failed to become healthy" -ForegroundColor Red
    return $false
}

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check Docker
if (-not (Test-Command "docker")) {
    Write-Host "Docker is not installed. Please install Docker first." -ForegroundColor Red
    exit 1
}

# Check Docker Compose
if (-not (Test-Command "docker-compose")) {
    Write-Host "Docker Compose is not installed. Please install Docker Compose first." -ForegroundColor Red
    exit 1
}

# Check if .env.production exists
if (-not (Test-Path ".env.production")) {
    Write-Host ".env.production file not found. Creating from .env.example..." -ForegroundColor Red
    Copy-Item ".env.example" ".env.production"
    Write-Host "Please update .env.production with your production values." -ForegroundColor Yellow
    exit 1
}

# Stop any existing containers
Write-Host "Stopping any existing containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.prod.test.yml down -v

# Build and start services
Write-Host "Building and starting services..." -ForegroundColor Yellow
docker-compose -f docker-compose.prod.test.yml up --build -d

# Check service health
$services = @(
    @{ Name = "API"; Url = "http://localhost:8000/health" },
    @{ Name = "Frontend"; Url = "http://localhost:3000/health" },
    @{ Name = "MongoDB"; Url = "http://localhost:27017" },
    @{ Name = "Redis"; Url = "http://localhost:6379" },
    @{ Name = "Prometheus"; Url = "http://localhost:9090/-/healthy" },
    @{ Name = "Grafana"; Url = "http://localhost:3001/api/health" }
)

foreach ($service in $services) {
    if (-not (Test-ServiceHealth -Service $service.Name -Url $service.Url)) {
        exit 1
    }
}

# Print service URLs
Write-Host "`nProduction test environment is ready!" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host "API: http://localhost:8000" -ForegroundColor Yellow
Write-Host "Grafana: http://localhost:3001" -ForegroundColor Yellow
Write-Host "Prometheus: http://localhost:9090" -ForegroundColor Yellow

# Ask user if they want to run tests
$runPerfTests = Read-Host "Do you want to run performance tests? (y/n)"
if ($runPerfTests -eq 'y') {
    Write-Host "`nRunning performance tests..." -ForegroundColor Yellow
    python run_performance_tests.py
}

$runSecTests = Read-Host "Do you want to run security tests? (y/n)"
if ($runSecTests -eq 'y') {
    Write-Host "`nRunning security tests..." -ForegroundColor Yellow
    python -m pytest tests/security/ -v
}

Write-Host "`nSetup complete! You can now test the production environment locally." -ForegroundColor Green
Write-Host "To stop the environment, run: docker-compose -f docker-compose.prod.test.yml down" -ForegroundColor Yellow 