# Check dependency tree
Write-Host "Checking dependency tree..."

# Get full dependency tree
Write-Host "`nFull Dependency Tree:"
npm list

# Get production dependencies only
Write-Host "`nProduction Dependencies Only:"
npm list --production

# Get development dependencies only
Write-Host "`nDevelopment Dependencies Only:"
npm list --dev

# Get direct dependencies only
Write-Host "`nDirect Dependencies Only:"
npm list --depth=0

# Check for circular dependencies
Write-Host "`nChecking for circular dependencies..."
if (Get-Command "madge" -ErrorAction SilentlyContinue) {
    madge --circular .
} else {
    Write-Host "madge is not installed. Install it with 'npm install -g madge' to check for circular dependencies."
}

# Check for duplicate dependencies
Write-Host "`nChecking for duplicate dependencies..."
npm dedupe --dry-run

Write-Host "`nDependency tree check completed!" 