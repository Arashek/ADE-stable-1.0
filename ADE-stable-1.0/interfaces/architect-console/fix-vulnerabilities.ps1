# Fix dependency vulnerabilities
Write-Host "Fixing dependency vulnerabilities..."
npm audit fix

# Check if fix was successful
if ($LASTEXITCODE -eq 0) {
    Write-Host "Dependency vulnerabilities fixed successfully!"
} else {
    Write-Host "Failed to fix some dependency vulnerabilities. Please check the error messages above."
    exit 1
}

# Run tests after fix
Write-Host "Running tests after fix..."
npm run test

# Check if tests passed
if ($LASTEXITCODE -eq 0) {
    Write-Host "All tests passed after vulnerability fix!"
} else {
    Write-Host "Some tests failed after vulnerability fix. Please check the error messages above."
    exit 1
} 