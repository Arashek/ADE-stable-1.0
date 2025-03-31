# Create Docker volume directories for ADE platform
$baseDir = "D:\ADE-stable-1.0-OSLLMS"

# Create base directory if it doesn't exist
if (-not (Test-Path $baseDir)) {
    New-Item -Path $baseDir -ItemType Directory -Force
    Write-Host "Created base directory: $baseDir"
}

# Define required volume directories
$volumeDirs = @(
    "ollama_models",
    "model_cache",
    "redis_data",
    "mongodb_data",
    "prometheus_data",
    "grafana_data"
)

# Create each volume directory
foreach ($dir in $volumeDirs) {
    $path = Join-Path $baseDir $dir
    if (-not (Test-Path $path)) {
        New-Item -Path $path -ItemType Directory -Force
        Write-Host "Created directory: $path"
    } else {
        Write-Host "Directory already exists: $path"
    }
}

Write-Host "All Docker volume directories have been created successfully."
