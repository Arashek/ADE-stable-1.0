# Run tests
npm run test

# Check if the tests passed
if ($LASTEXITCODE -eq 0) {
    Write-Host "All tests passed successfully!"
} else {
    Write-Host "Some tests failed. Please check the error messages above."
    exit 1
} 