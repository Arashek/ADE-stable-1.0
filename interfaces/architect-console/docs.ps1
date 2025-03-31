# Generate API documentation
Write-Host "Generating API documentation..."
npm run docs

# Check if documentation was generated successfully
if ($LASTEXITCODE -eq 0) {
    Write-Host "API documentation generated successfully!"
} else {
    Write-Host "Failed to generate API documentation. Please check the error messages above."
    exit 1
} 