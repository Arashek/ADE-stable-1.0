# PowerShell script to start ADE Platform
Write-Host "🚀 Starting ADE Platform..." -ForegroundColor Cyan

# Function to check if a port is available
function Test-Port {
    param($port)
    try {
        $null = New-Object System.Net.Sockets.TcpClient('localhost', $port)
        return $true
    } catch {
        return $false
    }
}

# Function to show Docker logs in real-time
function Show-DockerLogs {
    docker-compose logs -f --tail=50
}

# Function to check project type and set up preview
function Get-ProjectType {
    $files = Get-ChildItem -Path "." -File
    $projectType = @{
        Type = "unknown"
        Framework = "unknown"
        PreviewPort = 8000
    }

    # Check for React/Next.js
    if (Test-Path "package.json") {
        $packageJson = Get-Content "package.json" -Raw | ConvertFrom-Json
        if ($packageJson.dependencies.react) {
            $projectType.Type = "react"
            $projectType.Framework = if ($packageJson.dependencies.'next') { "next.js" } else { "react" }
            $projectType.PreviewPort = 3000
        }
    }

    # Check for Vue.js
    if (Test-Path "vue.config.js") {
        $projectType.Type = "vue"
        $projectType.Framework = "vue.js"
        $projectType.PreviewPort = 8080
    }

    # Check for Angular
    if (Test-Path "angular.json") {
        $projectType.Type = "angular"
        $projectType.Framework = "angular"
        $projectType.PreviewPort = 4200
    }

    # Check for Flask/Django
    if (Test-Path "requirements.txt") {
        $requirements = Get-Content "requirements.txt"
        if ($requirements -match "flask") {
            $projectType.Type = "python"
            $projectType.Framework = "flask"
            $projectType.PreviewPort = 5000
        }
        elseif ($requirements -match "django") {
            $projectType.Type = "python"
            $projectType.Framework = "django"
            $projectType.PreviewPort = 8000
        }
    }

    return $projectType
}

# Function to set up Boundaries
function Initialize-Boundaries {
    # Create Boundaries directory if it doesn't exist
    if (-not (Test-Path ".boundaries")) {
        New-Item -ItemType Directory -Path ".boundaries" | Out-Null
        
        # Create main configuration file
        @{
            version = "1.0"
            projectType = (Get-ProjectType)
            rules = @{
                development = @{
                    allowedPaths = @("src/", "public/", "assets/")
                    restrictedPaths = @("node_modules/", "dist/", "build/")
                    environmentChecks = @{
                        requiredVars = @("NODE_ENV", "API_KEY")
                        development = @{
                            allowedHosts = @("localhost", "127.0.0.1")
                            corsOrigins = @("http://localhost:3000", "http://localhost:8000")
                        }
                    }
                }
                preview = @{
                    ports = @{
                        main = 8000
                        preview = 3000
                        api = 8080
                    }
                    autoReload = $true
                    watchDirs = @("src/", "public/")
                }
                security = @{
                    allowedEnvFiles = @(".env.development", ".env.local")
                    secretPatterns = @(
                        "API_KEY_*",
                        "*_SECRET_*",
                        "PASSWORD_*"
                    )
                }
            }
        } | ConvertTo-Json -Depth 10 | Set-Content ".boundaries/config.json"

        # Create preview configuration
        @{
            previewConfig = @{
                enableHotReload = $true
                supportedFileTypes = @(
                    "js", "jsx", "ts", "tsx",
                    "vue", "svelte",
                    "html", "css", "scss",
                    "py", "rb",
                    "php", "java"
                )
                previewModes = @(
                    "web-browser",
                    "mobile-responsive",
                    "component-isolation"
                )
            }
        } | ConvertTo-Json -Depth 5 | Set-Content ".boundaries/preview.json"
    }
}

# Ensure we're in the right directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Initialize Boundaries
Write-Host "🔧 Initializing Boundaries..." -ForegroundColor Yellow
Initialize-Boundaries

# Check if Docker is running
Write-Host "⚙️ Checking Docker..." -ForegroundColor Yellow
try {
    $null = & docker info
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# Run environment sync
Write-Host "🔄 Syncing environment..." -ForegroundColor Yellow
node .cursor/scripts/sync-docker-env.js
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Environment sync failed. Please check the errors above." -ForegroundColor Red
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# Create data directories if they don't exist
$directories = @(
    ".\data",
    ".\projects",
    ".\storage",
    ".\logs",
    ".\preview-cache"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "📁 Created directory: $dir" -ForegroundColor Green
    }
}

# Build and start containers
Write-Host "🏗️ Building Docker containers..." -ForegroundColor Yellow
docker-compose build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed. Please check the errors above." -ForegroundColor Red
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host "🚀 Starting Docker containers..." -ForegroundColor Yellow
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker start failed. Please check the errors above." -ForegroundColor Red
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# Wait for services to be ready
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
$maxAttempts = 30
$attempts = 0
$ready = $false

while (-not $ready -and $attempts -lt $maxAttempts) {
    $attempts++
    if (Test-Port -port 8000) {
        $ready = $true
    } else {
        Write-Host "⏳ Waiting for API to be ready... (Attempt $attempts/$maxAttempts)" -ForegroundColor Yellow
        Start-Sleep -Seconds 2
    }
}

if (-not $ready) {
    Write-Host "❌ Services failed to start in time. Please check Docker logs." -ForegroundColor Red
    Show-DockerLogs
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# Get project type and configure preview
$projectType = Get-ProjectType
Write-Host "`n🔍 Detected project type: $($projectType.Framework)" -ForegroundColor Cyan

# Open browser with appropriate URL
Write-Host "🌐 Opening browsers..." -ForegroundColor Green
Start-Process "http://localhost:8000"  # ADE Platform
if ($projectType.PreviewPort -ne 8000) {
    Start-Sleep -Seconds 2  # Small delay between browser opens
    Start-Process "http://localhost:$($projectType.PreviewPort)"  # Project Preview
}

# Show status
Write-Host "`n✨ ADE Platform is ready!" -ForegroundColor Green
Write-Host "📂 Your data is stored in:" -ForegroundColor Cyan
Write-Host "   - Projects: ./projects" -ForegroundColor White
Write-Host "   - Storage: ./storage" -ForegroundColor White
Write-Host "   - Logs: ./logs" -ForegroundColor White
Write-Host "`n📌 Access points:" -ForegroundColor Cyan
Write-Host "   - ADE Platform: http://localhost:8000" -ForegroundColor White
Write-Host "   - Project Preview: http://localhost:$($projectType.PreviewPort)" -ForegroundColor White
Write-Host "`n🔧 Development tools:" -ForegroundColor Cyan
Write-Host "   - Boundaries Config: ./.boundaries/" -ForegroundColor White
Write-Host "   - Preview Cache: ./preview-cache" -ForegroundColor White
Write-Host "`n📊 Monitoring:" -ForegroundColor Cyan
Write-Host "   - Prometheus: http://localhost:9090" -ForegroundColor White
Write-Host "   - Grafana: http://localhost:3000" -ForegroundColor White

# Show logs
Write-Host "`n📜 Showing logs (Press Ctrl+C to exit)..." -ForegroundColor Yellow
Show-DockerLogs 