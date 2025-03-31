# Install license-checker if not already installed
Write-Host "Checking for license-checker installation..."
if (-not (Get-Command "license-checker" -ErrorAction SilentlyContinue)) {
    Write-Host "Installing license-checker..."
    npm install -g license-checker
}

# Check for dependency licenses
Write-Host "Checking for dependency licenses..."
$licenses = license-checker --summary

# Check if licenses were found
if ($LASTEXITCODE -eq 0) {
    Write-Host "Dependency licenses found:"
    $licenses | ForEach-Object {
        Write-Host "- $_"
    }
} else {
    Write-Host "Failed to check dependency licenses. Please check the error messages above."
    exit 1
} 