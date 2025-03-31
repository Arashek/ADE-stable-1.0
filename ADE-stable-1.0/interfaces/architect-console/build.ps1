# Build the application for production
npm run build

# Check if the build was successful
if ($LASTEXITCODE -eq 0) {
    Write-Host "Build completed successfully!"
} else {
    Write-Host "Build failed. Please check the error messages above."
    exit 1
} 