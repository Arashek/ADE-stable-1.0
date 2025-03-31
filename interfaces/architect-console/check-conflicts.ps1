# Install npm-check-conflicts if not already installed
Write-Host "Checking for npm-check-conflicts installation..."
if (-not (Get-Command "npm-check-conflicts" -ErrorAction SilentlyContinue)) {
    Write-Host "Installing npm-check-conflicts..."
    npm install -g npm-check-conflicts
}

# Check for dependency conflicts
Write-Host "Checking for dependency conflicts..."
$conflicts = npm-check-conflicts

# Check if conflicts were found
if ($LASTEXITCODE -eq 0) {
    Write-Host "No dependency conflicts found!"
} else {
    Write-Host "Dependency conflicts found:"
    $conflicts | ForEach-Object {
        Write-Host "- $_"
    }
    exit 1
} 