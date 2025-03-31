# Install npm-check-updates if not already installed
Write-Host "Checking for npm-check-updates installation..."
if (-not (Get-Command "ncu" -ErrorAction SilentlyContinue)) {
    Write-Host "Installing npm-check-updates..."
    npm install -g npm-check-updates
}

# Update dependencies
Write-Host "Updating dependencies..."
ncu -u

# Check if update was successful
if ($LASTEXITCODE -eq 0) {
    Write-Host "Dependencies updated successfully!"
} else {
    Write-Host "Failed to update dependencies. Please check the error messages above."
    exit 1
}

# Install updated dependencies
Write-Host "Installing updated dependencies..."
npm install

# Check if installation was successful
if ($LASTEXITCODE -eq 0) {
    Write-Host "Updated dependencies installed successfully!"
} else {
    Write-Host "Failed to install updated dependencies. Please check the error messages above."
    exit 1
}

# Run tests after update
Write-Host "Running tests after update..."
npm run test

# Check if tests passed
if ($LASTEXITCODE -eq 0) {
    Write-Host "All tests passed after dependency update!"
} else {
    Write-Host "Some tests failed after dependency update. Please check the error messages above."
    exit 1
} 