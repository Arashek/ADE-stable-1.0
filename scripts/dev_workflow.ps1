# Development workflow script for ADE platform

# Function to check if Docker is running
function Test-DockerRunning {
    try {
        $null = docker info
        return $true
    }
    catch {
        return $false
    }
}

# Function to check if required environment variables are set
function Test-RequiredEnvVars {
    $requiredVars = @(
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "DEEPSEEK_API_KEY",
        "GROQ_API_KEY"
    )
    
    $missingVars = @()
    foreach ($var in $requiredVars) {
        if (-not [System.Environment]::GetEnvironmentVariable($var, "User")) {
            $missingVars += $var
        }
    }
    
    if ($missingVars.Count -gt 0) {
        Write-Host "Missing required environment variables:"
        foreach ($var in $missingVars) {
            Write-Host "- $var"
        }
        return $false
    }
    return $true
}

# Function to create necessary directories
function New-RequiredDirectories {
    $directories = @(
        "data/training",
        "data/validation",
        "data/test",
        "output/checkpoints",
        "output/logs",
        "output/metrics",
        "output/visualizations"
    )
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "Created directory: $dir"
        }
    }
}

# Function to build and start the development environment
function Start-DevEnvironment {
    param (
        [switch]$Force
    )
    
    # Check if Docker is running
    if (-not (Test-DockerRunning)) {
        Write-Host "Docker is not running. Please start Docker and try again."
        return
    }
    
    # Check environment variables
    if (-not (Test-RequiredEnvVars)) {
        Write-Host "Please set the required environment variables and try again."
        return
    }
    
    # Create required directories
    New-RequiredDirectories
    
    # Stop existing containers if force flag is set
    if ($Force) {
        Write-Host "Stopping existing containers..."
        docker-compose -f docker-compose.dev.yml down
    }
    
    # Build and start the development environment
    Write-Host "Building and starting development environment..."
    docker-compose -f docker-compose.dev.yml up --build -d
    
    # Wait for services to be ready
    Write-Host "Waiting for services to be ready..."
    Start-Sleep -Seconds 10
    
    # Check service health
    $services = @(
        "api",
        "frontend",
        "model-trainer",
        "mongodb",
        "redis"
    )
    
    foreach ($service in $services) {
        $container = docker ps -q -f "name=$service"
        if ($container) {
            Write-Host "$service is running"
        }
        else {
            Write-Host "Warning: $service is not running"
        }
    }
}

# Function to stop the development environment
function Stop-DevEnvironment {
    Write-Host "Stopping development environment..."
    docker-compose -f docker-compose.dev.yml down
}

# Function to view logs
function View-Logs {
    param (
        [string]$Service
    )
    
    if ($Service) {
        docker-compose -f docker-compose.dev.yml logs -f $Service
    }
    else {
        docker-compose -f docker-compose.dev.yml logs -f
    }
}

# Function to restart a service
function Restart-Service {
    param (
        [string]$Service
    )
    
    if (-not $Service) {
        Write-Host "Please specify a service to restart"
        return
    }
    
    Write-Host "Restarting $Service..."
    docker-compose -f docker-compose.dev.yml restart $Service
}

# Function to show help
function Show-Help {
    Write-Host @"
ADE Development Workflow Script

Usage:
    .\dev_workflow.ps1 [command] [options]

Commands:
    start           Start the development environment
    stop            Stop the development environment
    logs            View logs (optionally specify service)
    restart         Restart a specific service
    help            Show this help message

Options:
    -Force          Force rebuild of containers
    -Service        Specify service name for logs/restart

Examples:
    .\dev_workflow.ps1 start
    .\dev_workflow.ps1 start -Force
    .\dev_workflow.ps1 stop
    .\dev_workflow.ps1 logs api
    .\dev_workflow.ps1 restart model-trainer
"@
}

# Main script logic
$command = $args[0]

switch ($command) {
    "start" {
        Start-DevEnvironment -Force:$args.Contains("-Force")
    }
    "stop" {
        Stop-DevEnvironment
    }
    "logs" {
        $service = $args | Where-Object { $_ -ne "-Service" } | Select-Object -First 1
        View-Logs -Service $service
    }
    "restart" {
        $service = $args | Where-Object { $_ -ne "-Service" } | Select-Object -First 1
        Restart-Service -Service $service
    }
    "help" {
        Show-Help
    }
    default {
        Show-Help
    }
} 