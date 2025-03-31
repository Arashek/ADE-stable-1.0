# Run ESLint
npm run lint

# Check if linting passed
if ($LASTEXITCODE -eq 0) {
    Write-Host "Linting completed successfully!"
} else {
    Write-Host "Linting found issues. Please fix the errors above."
    exit 1
} 