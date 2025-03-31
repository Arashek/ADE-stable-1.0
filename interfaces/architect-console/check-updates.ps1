# Install npm-check-updates if not already installed
Write-Host "Checking for npm-check-updates installation..."
if (-not (Get-Command "ncu" -ErrorAction SilentlyContinue)) {
    Write-Host "Installing npm-check-updates..."
    npm install -g npm-check-updates
}

# Check for dependency updates
Write-Host "Checking for dependency updates..."
$updates = ncu

# Check if updates were found
if ($LASTEXITCODE -eq 0) {
    Write-Host "No dependency updates found!"
} else {
    Write-Host "Dependency updates found:"
    $updates | ForEach-Object {
        Write-Host "- $_"
    }
    exit 1
} 