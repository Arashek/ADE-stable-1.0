# Build the application
Write-Host "Building the application..."
npm run build

# Check if build was successful
if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed. Please fix the issues above."
    exit 1
}

# Deploy the application
Write-Host "Deploying the application..."
# Add your deployment commands here
# For example:
# - Copy files to a server
# - Use a deployment service
# - Deploy to a cloud platform

Write-Host "Deployment completed successfully!" 