# Fix security vulnerabilities
Write-Host "Fixing security vulnerabilities..."
npm audit fix

# Check if the fix was successful
if ($LASTEXITCODE -eq 0) {
    Write-Host "Security vulnerabilities fixed successfully!"
} else {
    Write-Host "Failed to fix some security vulnerabilities. Please check the error messages above."
    exit 1
}

# Run tests after security fixes
Write-Host "Running tests after security fixes..."
npm run test

# Check if tests passed
if ($LASTEXITCODE -eq 0) {
    Write-Host "All tests passed after security fixes!"
} else {
 