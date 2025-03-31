# Colors for output
$Green = [System.ConsoleColor]::Green
$Yellow = [System.ConsoleColor]::Yellow
$Red = [System.ConsoleColor]::Red

# Function to check if a command exists
function Test-Command {
    param($Command)
    return [bool](Get-Command -Name $Command -ErrorAction SilentlyContinue)
}

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor $Yellow
if (-not (Test-Command docker)) {
    Write-Host "Docker is not installed. Please install Docker first." -ForegroundColor $Red
    exit 1
}

if (-not (Test-Command docker-compose)) {
    Write-Host "Docker Compose is not installed. Please install Docker Compose first." -ForegroundColor $Red
    exit 1
}

# Check for .env.development file
if (-not (Test-Path .env.development)) {
    Write-Host "Creating .env.development from .env.example..." -ForegroundColor $Yellow
    Copy-Item .env.example .env.development
    Write-Host "Please update .env.development with your API keys and configuration." -ForegroundColor $Yellow
    exit 1
}

# Create necessary directories
Write-Host "Creating necessary directories..." -ForegroundColor $Yellow
$directories = @(
    "projects",
    "logs",
    "data"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "Created directory: $dir" -ForegroundColor $Green
    }
}

# Build and start containers
Write-Host "Building and starting containers..." -ForegroundColor $Yellow
docker-compose -f docker-compose.dev.yml up --build -d

# Wait for services to be ready
Write-Host "Waiting for services to be ready..." -ForegroundColor $Yellow
$maxAttempts = 30
$attempts = 0
$ready = $false

while (-not $ready -and $attempts -lt $maxAttempts) {
    $attempts++
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            $ready = $true
        }
    } catch {
        Write-Host "Waiting for API to be ready... (Attempt $attempts/$maxAttempts)" -ForegroundColor $Yellow
        Start-Sleep -Seconds 2
    }
}

if (-not $ready) {
    Write-Host "Services failed to start in time. Please check Docker logs." -ForegroundColor $Red
    docker-compose -f docker-compose.dev.yml logs
    exit 1
}

# Print access information
Write-Host "`nDevelopment environment is ready!" -ForegroundColor $Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor $Green
Write-Host "API: http://localhost:8000" -ForegroundColor $Green
Write-Host "Adminer: http://localhost:8080" -ForegroundColor $Green
Write-Host "`nAPI Documentation: http://localhost:8000/docs" -ForegroundColor $Green

# Function to show logs
function Show-Logs {
    param($Service)
    docker-compose -f docker-compose.dev.yml logs -f $Service
}

# Function to stop services
function Stop-Services {
    docker-compose -f docker-compose.dev.yml down
}

# Function to restart services
function Restart-Services {
    docker-compose -f docker-compose.dev.yml restart
}

# Function to rebuild services
function Rebuild-Services {
    docker-compose -f docker-compose.dev.yml up --build -d
}

# Print usage information
Write-Host "`nAvailable commands:" -ForegroundColor $Yellow
Write-Host "  ./scripts/dev.ps1 logs [service]    - Show logs for a service" -ForegroundColor $Green
Write-Host "  ./scripts/dev.ps1 stop             - Stop all services" -ForegroundColor $Green
Write-Host "  ./scripts/dev.ps1 restart          - Restart all services" -ForegroundColor $Green
Write-Host "  ./scripts/dev.ps1 rebuild          - Rebuild all services" -ForegroundColor $Green
Write-Host "  ./scripts/dev.ps1 help             - Show this help message" -ForegroundColor $Green 