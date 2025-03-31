# Script to configure Docker to use D drive

# Function to check if running with administrator privileges
function Test-AdminPrivileges {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Function to check if Docker is installed
function Test-DockerInstalled {
    try {
        $null = Get-Command docker -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

# Function to check if Docker service is running
function Test-DockerService {
    try {
        $service = Get-Service docker
        return $service.Status -eq "Running"
    }
    catch {
        return $false
    }
}

# Function to create Docker data directory
function New-DockerDataDirectory {
    $dockerPath = "D:\Docker"
    if (-not (Test-Path $dockerPath)) {
        New-Item -ItemType Directory -Path $dockerPath -Force | Out-Null
        Write-Host "Created Docker data directory at $dockerPath"
    }
    return $dockerPath
}

# Function to create Docker daemon configuration
function Set-DockerDaemonConfig {
    param (
        [string]$DataRoot
    )
    
    $configPath = "$env:ProgramData\docker\config\daemon.json"
    $configDir = Split-Path -Parent $configPath
    
    # Create config directory if it doesn't exist
    if (-not (Test-Path $configDir)) {
        New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    }
    
    # Create or update daemon.json
    $config = @{
        "data-root" = $DataRoot
        "storage-driver" = "overlay2"
        "log-driver" = "json-file"
        "log-opts" = @{
            "max-size" = "10m"
            "max-file" = "3"
        }
    }
    
    $configJson = $config | ConvertTo-Json -Depth 10
    Set-Content -Path $configPath -Value $configJson
    Write-Host "Created Docker daemon configuration at $configPath"
}

# Function to stop Docker service
function Stop-DockerService {
    Write-Host "Stopping Docker service..."
    Stop-Service docker
    Start-Sleep -Seconds 5
}

# Function to start Docker service
function Start-DockerService {
    Write-Host "Starting Docker service..."
    Start-Service docker
    Start-Sleep -Seconds 10
}

# Function to verify Docker configuration
function Test-DockerConfig {
    try {
        $dockerInfo = docker info
        $dataRoot = ($dockerInfo | Select-String "Docker Root Dir:").ToString().Split(":")[1].Trim()
        Write-Host "Current Docker Root Dir: $dataRoot"
        return $dataRoot -eq "D:\Docker"
    }
    catch {
        Write-Host "Error verifying Docker configuration: $_"
        return $false
    }
}

# Main script logic
Write-Host "Configuring Docker to use D drive..."

# Check for administrator privileges
if (-not (Test-AdminPrivileges)) {
    Write-Host "Error: This script requires administrator privileges. Please run as administrator."
    exit 1
}

# Check if Docker is installed
if (-not (Test-DockerInstalled)) {
    Write-Host "Error: Docker is not installed. Please install Docker first."
    exit 1
}

# Check if Docker service is running
if (-not (Test-DockerService)) {
    Write-Host "Error: Docker service is not running. Please start Docker first."
    exit 1
}

# Create Docker data directory
$dockerPath = New-DockerDataDirectory

# Stop Docker service
Stop-DockerService

# Configure Docker daemon
Set-DockerDaemonConfig -DataRoot $dockerPath

# Start Docker service
Start-DockerService

# Verify configuration
if (Test-DockerConfig) {
    Write-Host "`nDocker has been successfully configured to use D:\Docker"
    Write-Host "You can now use Docker with the new configuration."
}
else {
    Write-Host "`nWarning: Docker configuration verification failed."
    Write-Host "Please check the Docker service and configuration manually."
    exit 1
}

Write-Host "`nNote: You may need to restart your computer for all changes to take effect." 