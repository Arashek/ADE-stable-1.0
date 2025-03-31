# Run ESLint
Write-Host "Running ESLint..."
npm run lint

# Check if linting passed
if ($LASTEXITCODE -ne 0) {
    Write-Host "ESLint found issues. Please fix them."
    exit 1
}

# Run TypeScript compiler check
Write-Host "Running TypeScript compiler check..."
npx tsc --noEmit

# Check if TypeScript compilation passed
if ($LASTEXITCODE -ne 0) {
    Write-Host "TypeScript compiler found issues. Please fix them."
    exit 1
}

# Run tests
Write-Host "Running tests..."
npm run test

# Check if tests passed
if ($LASTEXITCODE -ne 0) {
    Write-Host "Tests failed. Please fix them."
    exit 1
}

# Check for unused dependencies
Write-Host "Checking for unused dependencies..."
npx depcheck

# Check for outdated dependencies
Write-Host "Checking for outdated dependencies..."
npm outdated

# Check for security vulnerabilities
Write-Host "Checking for security vulnerabilities..."
npm audit

Write-Host "Code quality check completed successfully!" 