# Preview the production build
npm run preview

# Check if the preview server started successfully
if ($LASTEXITCODE -eq 0) {
    Write-Host "Preview server started successfully!"
} else {
    Write-Host "Failed to start preview server. Please check the error messages above."
    exit 1
} 