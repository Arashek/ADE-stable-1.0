# Run Prettier to format code
npm run format

# Check if formatting completed successfully
if ($LASTEXITCODE -eq 0) {
    Write-Host "Code formatting completed successfully!"
} else {
    Write-Host "Code formatting failed. Please check the error messages above."
    exit 1
} 