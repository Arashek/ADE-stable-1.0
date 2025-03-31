# Install npm-check if not already installed
Write-Host "Checking for npm-check installation..."
if (-not (Get-Command "npm-check" -ErrorAction SilentlyContinue)) {
    Write-Host "Installing npm-check..."
    npm install -g npm-check
}

# Check for missing dependencies
Write-Host "Checking for missing dependencies..."
$missing = npm-check --missing

# Check if missing dependencies were found
if ($LASTEXITCODE -eq 0) {
    Write-Host "No missing dependencies found!"
} else {
    Write-Host "Missing dependencies found:"
    $missing | ForEach-Object {
        Write-Host "- $_"
    }
    exit 1
} 